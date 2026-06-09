"""
CodeReviewerAgent — LLM-powered code review using Groq Llama 3.3-70B.

Iterates over every file in the pipeline state, sends each one to the
LLM with a structured prompt, and parses the JSON response into a list
of ``FlaggedIssue`` models that get appended to ``state["flags"]``.
"""

from __future__ import annotations

import json
import re
from typing import Any, List

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import BaseAgent, LangGraphState
from app.core.config import settings
from app.core.retry import retry_async
from app.schemas.issue import CategoryEnum, FlaggedIssue, SeverityEnum

# ── Constants ────────────────────────────────────────────

_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
_TEMPERATURE = 0.1          # low temp → deterministic, precise output
_MAX_TOKENS = 2048
_MAX_FILE_CHARS = 6_000     # truncate to fit within free-tier TPM limits

# ── System prompt ────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are KRITIQ, an expert autonomous code reviewer.
Analyse the source file provided by the user and identify:
  • Bugs and logic errors
  • Security vulnerabilities (SQL injection, XSS, path traversal, secrets in code, …)
  • Code smells and anti-patterns
  • Performance issues
  • Missing or misleading documentation

For EACH issue, return a JSON object with exactly these keys:
  file_path   – the file path (given by the user)
  line_number – approximate line number (integer)
  severity    – one of: critical, high, medium, low, info
  category    – one of: security, bug, style, performance, docs
  description – concise explanation of the problem
  suggested_fix – concrete code or action to fix it

Return ONLY a JSON array of issue objects.  
If the file has no issues, return an empty array: []

Rules:
  • Do NOT wrap the JSON in markdown fences or any other text.
  • Do NOT add commentary outside the JSON array.
  • Be precise with line numbers — count from 1.
"""

# ── Helpers ──────────────────────────────────────────────

# Matches ```json ... ``` or ``` ... ``` wrapping that LLMs sometimes add
_FENCE_RE = re.compile(
    r"```(?:json)?\s*\n?(.*?)\n?\s*```",
    re.DOTALL,
)


def _strip_fences(text: str) -> str:
    """Remove markdown code fences if the LLM wrapped its response."""
    m = _FENCE_RE.search(text)
    return m.group(1).strip() if m else text.strip()


def _safe_parse_issues(
    raw: str,
    file_path: str,
    logger,
) -> List[FlaggedIssue]:
    """
    Parse LLM output into validated ``FlaggedIssue`` models.

    Handles:
      • Markdown fence stripping
      • Single-object (not wrapped in array) responses
      • Graceful skip of malformed items
    """
    cleaned = _strip_fences(raw)

    # ── Try JSON parse ───────────────────────────────────
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(
            "JSON decode failed for %s — raw response:\n%.300s",
            file_path,
            raw,
        )
        return []

    # Normalise: single object → list
    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        logger.warning("Unexpected JSON shape for %s: %s", file_path, type(data))
        return []

    # ── Validate each item ───────────────────────────────
    issues: List[FlaggedIssue] = []
    for item in data:
        try:
            # Ensure file_path is set even if LLM omits it
            item.setdefault("file_path", file_path)
            issues.append(FlaggedIssue.model_validate(item))
        except Exception as exc:
            logger.debug("Skipped malformed issue in %s: %s", file_path, exc)

    return issues


# ── Agent ────────────────────────────────────────────────


class CodeReviewerAgent(BaseAgent):
    """
    Sends every file in the state to Groq Llama 3.3-70B and collects
    ``FlaggedIssue`` results.

    Usage inside a LangGraph node::

        reviewer = CodeReviewerAgent()
        state = await reviewer.run(state)
        # state["flags"] now contains the flagged issues
    """

    def __init__(self) -> None:
        super().__init__()
        self._llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=_MODEL,
            temperature=_TEMPERATURE,
            max_tokens=_MAX_TOKENS,
        )

    # ── Core logic ───────────────────────────────────────

    async def run(self, state: LangGraphState) -> LangGraphState:
        """Review every file and populate ``state["flags"]``."""
        self._log_start(state)

        files: List[dict[str, Any]] = state.get("files") or []
        all_flags: List[dict[str, Any]] = list(state.get("flags") or [])

        for file_info in files:
            path = file_info.get("path", "unknown")
            content = file_info.get("content", "")

            if not content.strip():
                self.logger.debug("Skipped empty file: %s", path)
                continue

            issues = await self._review_file(path, content)
            # Serialise FlaggedIssue → dict so the state stays JSON-safe
            all_flags.extend(issue.model_dump(mode="json") for issue in issues)

        self._log_done("flags", len(all_flags) - len(state.get("flags") or []))

        return {**state, "flags": all_flags}

    # ── Private ──────────────────────────────────────────

    @retry_async()
    async def _review_file(
        self, file_path: str, content: str
    ) -> List[FlaggedIssue]:
        """Send a single file to the LLM and parse the result."""
        # Truncate giant files to stay within context window
        if len(content) > _MAX_FILE_CHARS:
            content = content[:_MAX_FILE_CHARS] + "\n\n... [truncated]"
            self.logger.debug("Truncated %s to %d chars", file_path, _MAX_FILE_CHARS)

        # Number the lines so the LLM can reference them
        numbered = "\n".join(
            f"{i}: {line}"
            for i, line in enumerate(content.splitlines(), start=1)
        )

        user_prompt = (
            f"File: `{file_path}`\n\n"
            f"```\n{numbered}\n```"
        )

        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            raw_text: str = response.content  # type: ignore[assignment]
        except Exception as exc:
            self.logger.error("LLM call failed for %s: %s", file_path, exc)
            return []

        issues = _safe_parse_issues(raw_text, file_path, self.logger)
        self.logger.info(
            "  %s → %d issue(s)", file_path, len(issues)
        )
        return issues
