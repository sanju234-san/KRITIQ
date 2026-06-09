"""
ReadmeWriterAgent — Compiles code reviews and fixes into a Markdown summary.
"""

from __future__ import annotations

import json
import logging
from typing import Any, List

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import BaseAgent, LangGraphState
from app.core.config import settings
from app.core.retry import retry_async

logger = logging.getLogger("kritiq.agents.ReadmeWriterAgent")

_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
_TEMPERATURE = 0.2
_MAX_TOKENS = 2048

# Maximum items to send to LLM to avoid context overflow
_MAX_FLAGS_FOR_PROMPT = 30
_MAX_FIXES_FOR_PROMPT = 15
_MAX_FILES_FOR_PROMPT = 50

_README_SYSTEM_PROMPT = """\
You are KRITIQ, an expert technical writer and lead developer.
Your task is to write a comprehensive project review summary report in Markdown.

The report MUST include these sections:
  1. **Project Overview** — Name the repository, summarize the tech stack, and list the total number of files analyzed.
  2. **Executive Summary** — Key metrics: total issues found, breakdown by severity (critical/high/medium/low), total fixes applied.
  3. **Critical & High-Severity Issues** — Detail each critical/high issue with file path, line number, description, and recommended action.
  4. **Auto-Applied Fixes** — For each fix, show the file, original code vs. fixed code, and a brief explanation.
  5. **Code Quality Recommendations** — General advice on improving maintainability, security, and performance.
  6. **Conclusion** — Overall health assessment of the codebase (Good / Needs Attention / Critical).

Formatting rules:
  - Use proper Markdown headings (##), tables, and code blocks.
  - Be concise but informative.
  - Return ONLY the Markdown content.
  - Do NOT wrap the response in outer markdown fences (e.g. do not wrap the entire document in ```markdown ... ```).
"""


class ReadmeWriterAgent(BaseAgent):
    """
    Agent that reads file names, findings, and applied fixes from the pipeline state,
    and queries Groq to compile a comprehensive, final review report in Markdown.
    """

    def __init__(self) -> None:
        super().__init__()
        self._llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=_MODEL,
            temperature=_TEMPERATURE,
            max_tokens=_MAX_TOKENS,
        )

    @retry_async()
    async def run(self, state: LangGraphState) -> LangGraphState:
        """Generate final review summary Markdown and update state."""
        self._log_start(state)

        files: List[dict[str, Any]] = state.get("files") or []
        flags: List[dict[str, Any]] = state.get("flags") or []
        fixes: List[dict[str, Any]] = state.get("fixes") or []
        repo_url = state.get("repo_url", "unknown")

        # Build a compact summary to avoid blowing the LLM context window
        user_prompt = self._build_prompt(repo_url, files, flags, fixes)

        messages = [
            SystemMessage(content=_README_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            readme_content: str = response.content  # type: ignore[assignment]

            # Clean up outer markdown wrappers if LLM still added them
            readme_content = readme_content.strip()
            if readme_content.startswith("```markdown"):
                readme_content = readme_content.split("```markdown", 1)[1]
            if readme_content.startswith("```md"):
                readme_content = readme_content.split("```md", 1)[1]
            if readme_content.endswith("```"):
                readme_content = readme_content.rsplit("```", 1)[0]
            readme_content = readme_content.strip()

            self._log_done("readme chars", len(readme_content))
            return {**state, "readme_content": readme_content}
        except Exception as exc:
            self.logger.error("LLM call failed for ReadmeWriterAgent: %s", exc)
            # Generate a fallback summary without LLM
            fallback = self._generate_fallback_summary(repo_url, files, flags, fixes)
            return {**state, "readme_content": fallback}

    def _build_prompt(
        self,
        repo_url: str,
        files: List[dict],
        flags: List[dict],
        fixes: List[dict],
    ) -> str:
        """Build a compact prompt that fits within the LLM context window."""
        file_paths = [f.get("path", "unknown") for f in files]

        # Severity distribution
        sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        cat_counts = {"security": 0, "bug": 0, "style": 0, "performance": 0, "docs": 0}
        for f in flags:
            sev = f.get("severity", "info")
            cat = f.get("category", "docs")
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        # Only include a sample of flags (prioritize critical/high)
        sorted_flags = sorted(
            flags,
            key=lambda f: ["critical", "high", "medium", "low", "info"].index(
                f.get("severity", "info")
            ),
        )
        sampled_flags = sorted_flags[:_MAX_FLAGS_FOR_PROMPT]

        # Compact flag representation
        flag_lines = []
        for f in sampled_flags:
            flag_lines.append(
                f"- [{f.get('severity', '?').upper()}] {f.get('file_path', '?')}:{f.get('line_number', '?')} "
                f"({f.get('category', '?')}) — {f.get('description', 'N/A')}"
            )

        # Compact fix representation
        fix_lines = []
        for f in fixes[:_MAX_FIXES_FOR_PROMPT]:
            fix_lines.append(
                f"- {f.get('explanation', 'N/A')} (validated: {f.get('validated', False)})"
            )

        truncated_files = file_paths[:_MAX_FILES_FOR_PROMPT]
        files_note = ""
        if len(file_paths) > _MAX_FILES_FOR_PROMPT:
            files_note = f"\n... and {len(file_paths) - _MAX_FILES_FOR_PROMPT} more files"

        truncation_note = ""
        if len(flags) > _MAX_FLAGS_FOR_PROMPT:
            truncation_note = (
                f"\n(Showing top {_MAX_FLAGS_FOR_PROMPT} of {len(flags)} total issues. "
                f"Include the full count in the report.)"
            )

        prompt = (
            f"Repository: {repo_url}\n"
            f"Total Files Analyzed: {len(file_paths)}\n"
            f"Files:\n" + "\n".join(f"  - {p}" for p in truncated_files) + files_note + "\n\n"
            f"Issue Severity Breakdown: {json.dumps(sev_counts)}\n"
            f"Issue Category Breakdown: {json.dumps(cat_counts)}\n\n"
            f"Flagged Issues ({len(flags)} total):{truncation_note}\n"
            + "\n".join(flag_lines) + "\n\n"
            f"Applied Fixes ({len(fixes)} total):\n"
            + ("\n".join(fix_lines) if fix_lines else "  None") + "\n"
        )

        return prompt

    def _generate_fallback_summary(
        self,
        repo_url: str,
        files: List[dict],
        flags: List[dict],
        fixes: List[dict],
    ) -> str:
        """Generate a basic summary without the LLM when LLM call fails."""
        sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in flags:
            sev = f.get("severity", "info")
            sev_counts[sev] = sev_counts.get(sev, 0) + 1

        critical_high = sev_counts["critical"] + sev_counts["high"]
        health = "Good" if critical_high == 0 else ("Needs Attention" if critical_high < 5 else "Critical")

        lines = [
            f"# KRITIQ Analysis Report",
            f"",
            f"## Repository",
            f"**{repo_url}**",
            f"",
            f"## Executive Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Files Analyzed | {len(files)} |",
            f"| Total Issues | {len(flags)} |",
            f"| Critical | {sev_counts['critical']} |",
            f"| High | {sev_counts['high']} |",
            f"| Medium | {sev_counts['medium']} |",
            f"| Low | {sev_counts['low']} |",
            f"| Info | {sev_counts['info']} |",
            f"| Auto-Fixed | {len(fixes)} |",
            f"",
            f"## Health Assessment: **{health}**",
            f"",
        ]

        if critical_high > 0:
            lines.append("## Critical & High-Severity Issues\n")
            for f in flags:
                if f.get("severity") in ("critical", "high"):
                    lines.append(
                        f"- **[{f.get('severity', '?').upper()}]** `{f.get('file_path', '?')}:{f.get('line_number', '?')}` "
                        f"— {f.get('description', 'N/A')}"
                    )
            lines.append("")

        if fixes:
            lines.append("## Applied Fixes\n")
            for f in fixes:
                lines.append(f"- {f.get('explanation', 'Fix applied')}")
            lines.append("")

        return "\n".join(lines)
