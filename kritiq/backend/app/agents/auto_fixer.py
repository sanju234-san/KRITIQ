"""
AutoFixerAgent — generates, validates, and commits code fixes for flagged issues.
"""

from __future__ import annotations

import ast
import json
import re
import logging
from typing import Any, List, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import BaseAgent, LangGraphState
from app.core.config import settings
from app.core.retry import retry_async
from app.schemas.issue import Fix, FlaggedIssue
from app.services.github_service import github_service

logger = logging.getLogger("kritiq.agents.AutoFixerAgent")

_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
_TEMPERATURE = 0.1
_MAX_TOKENS = 2048
_MAX_FILE_CHARS = 6_000

_FIX_SYSTEM_PROMPT = """\
You are KRITIQ, an expert software developer.
You are given a file and a flagged issue in that file. Your task is to generate a code fix for this issue.

You must return a JSON object with exactly these keys:
  original_code: The EXACT contiguous block of code from the file that needs to be replaced. This must match a substring in the file EXACTLY (including whitespace, newlines, and indentation) so that a simple string replacement will succeed.
  fixed_code: The new code that should replace the original_code.
  explanation: A brief explanation of the fix.

Rules:
  - Do NOT wrap the response in markdown fences or any other text.
  - Return ONLY the JSON object.
  - The original_code MUST match the file contents exactly.
"""

_FENCE_RE = re.compile(
    r"```(?:json)?\s*\n?(.*?)\n?\s*```",
    re.DOTALL,
)


class AutoFixerAgent(BaseAgent):
    """
    Agent that processes all FlaggedIssues in the graph state, generates fixes,
    validates syntax, and commits verified fixes back to the repository.
    """

    def __init__(self) -> None:
        super().__init__()
        self._llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=_MODEL,
            temperature=_TEMPERATURE,
            max_tokens=_MAX_TOKENS,
        )

    async def run(self, state: LangGraphState) -> LangGraphState:
        """Iterate over flags, apply fixes, and update state."""
        self._log_start(state)

        files: List[dict[str, Any]] = list(state.get("files") or [])
        flags: List[dict[str, Any]] = list(state.get("flags") or [])
        fixes: List[dict[str, Any]] = list(state.get("fixes") or [])
        repo_url = state.get("repo_url", "")
        branch = state.get("commit_sha", "")

        # Map file paths to file info dicts in state for easy lookups and updates
        file_map = {f.get("path"): f for f in files}

        for flag_dict in flags:
            try:
                issue = FlaggedIssue.model_validate(flag_dict)
            except Exception as exc:
                self.logger.warning("Skipped invalid issue in state: %s", exc)
                continue

            # We only fix critical, high, and medium severity issues to be safe
            if issue.severity not in ["critical", "high", "medium"]:
                self.logger.debug("Skipped fix for low-severity issue: %s", issue.id)
                continue

            file_info = file_map.get(issue.file_path)
            if not file_info:
                self.logger.warning("File not found in state for path: %s", issue.file_path)
                continue

            file_content = file_info.get("content", "")
            if not file_content.strip():
                continue

            # Generate and validate fix in retry loop
            fix = await self.generate_fix_with_retry(issue, file_content)
            if not fix:
                self.logger.warning("Failed to generate a validated fix for issue: %s", issue.id)
                continue

            # Commit the fix back to GitHub
            try:
                commit_sha = await self.commit_fix(fix, issue, repo_url, file_content, branch)
                fix.commit_sha = commit_sha
                
                # Update in-memory file content so subsequent fixes build on top of this fix!
                updated_content = file_content.replace(fix.original_code, fix.fixed_code)
                file_info["content"] = updated_content
                file_content = updated_content
                
                fixes.append(fix.model_dump(mode="json"))
                self.logger.info("Successfully applied and committed fix for issue=%s", issue.id)
            except Exception as exc:
                self.logger.error("Failed to commit fix for issue=%s: %s", issue.id, exc)

        self._log_done("fixes", len(fixes) - len(state.get("fixes") or []))
        return {**state, "files": files, "fixes": fixes}

    async def generate_fix_with_retry(self, issue: FlaggedIssue, file_content: str) -> Optional[Fix]:
        """Attempt to generate and validate a fix, retrying up to 3 times."""
        for attempt in range(1, 4):
            self.logger.debug("Generating fix for issue=%s (attempt %d/3)", issue.id, attempt)
            fix = await self.generate_fix(issue, file_content)
            if not fix:
                continue

            # Check: original_code exists in the file
            if fix.original_code not in file_content:
                self.logger.debug("Validation failed: original_code not found in file content.")
                continue

            # Check: syntax validation for python files
            if issue.file_path.endswith(".py"):
                new_content = file_content.replace(fix.original_code, fix.fixed_code)
                try:
                    ast.parse(new_content)
                    fix.validated = True
                except SyntaxError as err:
                    self.logger.debug("Validation failed: SyntaxError in generated python fix: %s", err)
                    continue
            else:
                # Basic non-python safety checks (non-empty replacement code)
                if not fix.fixed_code.strip():
                    self.logger.debug("Validation failed: fixed_code is empty.")
                    continue
                fix.validated = True

            # If we get here, the fix is successfully validated!
            return fix

        return None

    @retry_async()
    async def generate_fix(self, issue: FlaggedIssue, file_content: str) -> Optional[Fix]:
        """Invoke Groq to get replacement code for the issue."""
        # Truncate content if too long
        if len(file_content) > _MAX_FILE_CHARS:
            file_content = file_content[:_MAX_FILE_CHARS] + "\n\n... [truncated]"

        # Line-number the file so the LLM has context
        numbered = "\n".join(
            f"{i}: {line}"
            for i, line in enumerate(file_content.splitlines(), start=1)
        )

        user_prompt = (
            f"File Path: `{issue.file_path}`\n"
            f"Vulnerability/Issue Line: {issue.line_number}\n"
            f"Severity: {issue.severity}\n"
            f"Category: {issue.category}\n"
            f"Issue Description: {issue.description}\n"
            f"Suggested Action: {issue.suggested_fix}\n\n"
            f"Source File Code:\n```\n{numbered}\n```"
        )

        messages = [
            SystemMessage(content=_FIX_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            raw_text: str = response.content  # type: ignore[assignment]
            return self._parse_fix_response(raw_text, issue.id)
        except Exception as exc:
            self.logger.error("LLM call failed for fix generation on issue %s: %s", issue.id, exc)
            return None

    def _parse_fix_response(self, raw: str, issue_id: str) -> Optional[Fix]:
        """Parse raw response from LLM into a Fix Pydantic model."""
        m = _FENCE_RE.search(raw)
        cleaned = m.group(1).strip() if m else raw.strip()

        try:
            data = json.loads(cleaned)
            return Fix(
                issue_id=issue_id,
                original_code=data.get("original_code", ""),
                fixed_code=data.get("fixed_code", ""),
                explanation=data.get("explanation", ""),
                validated=False,
            )
        except Exception as exc:
            self.logger.warning("Failed to parse fix JSON for issue %s: %s", issue_id, exc)
            return None

    async def commit_fix(
        self,
        fix: Fix,
        issue: FlaggedIssue,
        repo_url: str,
        file_content: str,
        branch: Optional[str] = None,
    ) -> str:
        """Commit the generated fix to the GitHub repository branch."""
        # Replace original code block with fix
        new_content = file_content.replace(fix.original_code, fix.fixed_code)
        
        # Build conventional commit message
        commit_message = f"fix: resolve {issue.severity} {issue.category} issue in {issue.file_path}"

        commit_sha = await github_service.commit_file(
            repo_url=repo_url,
            file_path=issue.file_path,
            content=new_content,
            message=commit_message,
            branch=branch,
        )
        return commit_sha
