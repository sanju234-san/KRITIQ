"""
SecurityAuditorAgent — LLM-powered security review using Groq Llama 3.3-70B.

Scans files for hardcoded secrets, SQL/command injections, insecure dependencies,
and OWASP Top 10 patterns. Incorporates quick regex scans before Groq analysis.
"""

from __future__ import annotations

import json
import re
import asyncio
from typing import Any, List

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import BaseAgent, LangGraphState
from app.core.config import settings
from app.core.retry import retry_async
from app.schemas.issue import CategoryEnum, FlaggedIssue, SeverityEnum

# ── Constants ────────────────────────────────────────────

_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
_TEMPERATURE = 0.1
_MAX_TOKENS = 2048
_MAX_FILE_CHARS = 6_000

# ── Regex Secret Scanning ────────────────────────────────

_SECRET_PATTERNS = {
    "Generic Secret/API Key": re.compile(
        r"(?i)\b(api_key|apikey|secret|password|passwd|pwd|token|auth_token|jwt|private_key|access_key|conn_str|connection_string)\b\s*[:=]\s*['\"`]([a-zA-Z0-9_\-\.\+\=\/\\~\!\@\#\$\%\^\&\*\(\)]{8,})['\"`]"
    ),
    "PEM Private Key": re.compile(r"-----BEGIN\s+(?:RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE\s+KEY-----"),
    "AWS API Key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Slack Token": re.compile(r"xox[bapr]-[0-9a-zA-Z]{10,20}-[0-9a-zA-Z]{10,20}"),
    "Google API Key": re.compile(r"AIzaSy[a-zA-Z0-9_\-]{33}"),
}


def _is_placeholder(val: str) -> bool:
    """Check if the matched secret is a template or placeholder to reduce noise."""
    val_lower = val.lower()
    placeholders = {
        "your_", "placeholder", "dummy", "test", "example",
        "mock", "key_here", "secret_here", "password_here",
        "my_api_key", "my_secret", "<", ">", "${", "}", "default_value"
    }
    return any(p in val_lower for p in placeholders) or len(val) < 8


# ── System Prompts ───────────────────────────────────────

_SECRETS_SYSTEM_PROMPT = """\
You are KRITIQ, an expert security auditor.
Analyze the provided source file specifically for hardcoded secrets, credentials, API keys, tokens, passwords, database URIs, or private keys.

For EACH secret or credential vulnerability identified, return a JSON object with exactly these keys:
  file_path   – the file path (given by the user)
  line_number – approximate line number (integer)
  severity    – one of: critical, high, medium, low, info
  category    – must be "security"
  description – concise explanation of the secret leak risk
  suggested_fix – concrete recommendation to move it to env vars or a secret manager

Return ONLY a JSON array of issue objects.  
If the file has no hardcoded secrets, return an empty array: []

Rules:
  • Do NOT wrap the JSON in markdown fences or any other text.
  • Do NOT add commentary outside the JSON array.
  • Be precise with line numbers.
"""

_INJECTIONS_SYSTEM_PROMPT = """\
You are KRITIQ, an expert security auditor.
Analyze the provided source file for security vulnerabilities such as:
  • SQL injection (raw queries, string formatting in SQL)
  • OS Command injection (unsafe subprocess calls, system commands)
  • Path traversal (unsafe file access, filename concatenation)
  • Cross-Site Scripting (XSS), CSRF, or SSRF
  • Insecure dependencies or outdated patterns (e.g. parsing requirements.txt or package.json)
  • Other OWASP Top 10 vulnerabilities

For EACH vulnerability identified, return a JSON object with exactly these keys:
  file_path   – the file path (given by the user)
  line_number – approximate line number (integer)
  severity    – one of: critical, high, medium, low, info
  category    – must be "security"
  description – concise explanation of the vulnerability and risk
  suggested_fix – concrete code or action to fix it (e.g., parameterised queries, sanitisation, etc.)

Return ONLY a JSON array of issue objects.  
If the file has no such vulnerabilities, return an empty array: []

Rules:
  • Do NOT wrap the JSON in markdown fences or any other text.
  • Do NOT add commentary outside the JSON array.
  • Be precise with line numbers.
"""

# Matches ```json ... ``` or ``` ... ``` wrapping that LLMs sometimes add
_FENCE_RE = re.compile(
    r"```(?:json)?\s*\n?(.*?)\n?\s*```",
    re.DOTALL,
)


# ── Agent Class ──────────────────────────────────────────


class SecurityAuditorAgent(BaseAgent):
    """
    Scans files for security flaws using regex pattern matching and LLMs.
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
        """Scan every file for security flaws and update state."""
        self._log_start(state)

        files: List[dict[str, Any]] = state.get("files") or []
        # In a parallel LangGraph node, we output results under state["security_flags"]
        # which will be merged by the downstream join node.
        new_flags: List[dict[str, Any]] = []

        # Run concurrent checks for each file
        tasks = [self._audit_file(f.get("path", "unknown"), f.get("content", "")) for f in files]
        results = await asyncio.gather(*tasks)

        for file_issues in results:
            for issue in file_issues:
                new_flags.append(issue.model_dump(mode="json"))

        self._log_done("security flags", len(new_flags))

        return {**state, "security_flags": new_flags}

    async def _audit_file(self, file_path: str, content: str) -> List[FlaggedIssue]:
        """Run both secret scanning and injection audits on a file concurrently."""
        if not content.strip():
            return []

        # Run secrets scan and injections scan concurrently
        secrets_task = self.scan_secrets(file_path, content)
        injections_task = self.check_injections(file_path, content)
        
        secrets_issues, injections_issues = await asyncio.gather(secrets_task, injections_task)
        
        # Combine issues and return
        return secrets_issues + injections_issues

    async def scan_secrets(self, file_path: str, content: str) -> List[FlaggedIssue]:
        """
        Scan a file for hardcoded secrets. Uses regex patterns first,
        followed by a Groq LLM deep scan for credentials.
        """
        issues: List[FlaggedIssue] = []

        # 1. Regex Pass
        for i, line in enumerate(content.splitlines(), start=1):
            for name, pattern in _SECRET_PATTERNS.items():
                match = pattern.search(line)
                if match:
                    if len(match.groups()) >= 2:
                        val = match.group(2)
                        if _is_placeholder(val):
                            continue

                    issues.append(
                        FlaggedIssue(
                            file_path=file_path,
                            line_number=i,
                            severity=SeverityEnum.critical,
                            category=CategoryEnum.security,
                            description=f"Potential hardcoded secret or API key detected: {name}.",
                            suggested_fix="Extract secret key to environment variables (.env) or load from a secure secrets vault."
                        )
                    )
                    break  # Avoid flagging the same line multiple times

        # 2. Groq Deep Scan Pass
        llm_issues = await self._call_groq(file_path, content, _SECRETS_SYSTEM_PROMPT)

        # Merge findings, prioritizing regex detections on exact lines
        regex_lines = {iss.line_number for iss in issues}
        for llm_iss in llm_issues:
            # Overwrite category to security
            llm_iss.category = CategoryEnum.security
            if llm_iss.line_number not in regex_lines:
                issues.append(llm_iss)

        return issues

    async def check_injections(self, file_path: str, content: str) -> List[FlaggedIssue]:
        """
        Query Groq model to identify SQL Injection, OS command injection,
        path traversal, insecure library usage, or OWASP Top 10 flaws.
        """
        issues = await self._call_groq(file_path, content, _INJECTIONS_SYSTEM_PROMPT)
        
        # Ensure category is always set to security
        for issue in issues:
            issue.category = CategoryEnum.security

        return issues

    # ── LLM helper ──────────────────────────────────────────

    @retry_async()
    async def _call_groq(
        self, file_path: str, content: str, system_prompt: str
    ) -> List[FlaggedIssue]:
        """Helper to invoke Groq API and parse response."""
        if len(content) > _MAX_FILE_CHARS:
            content = content[:_MAX_FILE_CHARS] + "\n\n... [truncated]"

        # Number lines for precise LLM references
        numbered = "\n".join(
            f"{i}: {line}"
            for i, line in enumerate(content.splitlines(), start=1)
        )

        user_prompt = f"File: `{file_path}`\n\n```\n{numbered}\n```"
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            raw_text: str = response.content  # type: ignore[assignment]
        except Exception as exc:
            self.logger.error("LLM call failed for %s: %s", file_path, exc)
            return []

        return self._safe_parse_issues(raw_text, file_path)

    def _safe_parse_issues(self, raw: str, file_path: str) -> List[FlaggedIssue]:
        """Safely parse LLM JSON output to FlaggedIssue list."""
        m = _FENCE_RE.search(raw)
        cleaned = m.group(1).strip() if m else raw.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            self.logger.warning(
                "JSON decode failed for %s security scan — raw response:\n%.300s",
                file_path,
                raw,
            )
            return []

        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            self.logger.warning("Unexpected security scan JSON shape: %s", type(data))
            return []

        issues: List[FlaggedIssue] = []
        for item in data:
            try:
                item.setdefault("file_path", file_path)
                item.setdefault("category", "security")
                issues.append(FlaggedIssue.model_validate(item))
            except Exception as exc:
                self.logger.debug("Skipped malformed security issue: %s", exc)

        return issues
