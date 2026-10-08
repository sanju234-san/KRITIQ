"""Parse and validate AI code-review responses.

New AI responses are strict JSON. A small legacy Markdown parser remains as a
backward-compatible safety net for older stored/provider responses.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from app.models.review_models import ReviewAIResult


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    # Remove common Markdown emphasis/backticks from structured scalar fields.
    text = re.sub(r"^#{1,6}\s*", "", text)
    text = re.sub(r"^\*{1,3}|\*{1,3}$", "", text)
    text = re.sub(r"^_{1,3}|_{1,3}$", "", text)
    text = text.replace("\\`", "`")
    return text.strip().strip(":").strip()


def _normalize_line(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    match = re.search(r"\b(?:line\s*)?(\d+)\b", str(value), re.IGNORECASE)
    return int(match.group(1)) if match else None


def _normalize_severity(value: Any) -> str:
    value = _clean_text(value).lower()
    if value in {"critical", "high", "severe"}:
        return "high"
    if value in {"warning", "medium", "moderate"}:
        return "medium"
    return "low" if value in {"low", "minor", "info", "informational"} else "medium"


def _normalize_issue(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": _clean_text(issue.get("title") or issue.get("message") or "Untitled issue"),
        "line": _normalize_line(issue.get("line")),
        "severity": _normalize_severity(issue.get("severity")),
        "explanation": _clean_text(issue.get("explanation") or issue.get("description") or "No detailed explanation available."),
        "suggested_fix": _clean_text(issue.get("suggested_fix") or issue.get("suggestedFix") or issue.get("fix")) or None,
    }


def _extract_json_object(raw_text: str) -> Optional[dict[str, Any]]:
    text = (raw_text or "").strip()
    if not text:
        return None

    # Handle ```json ... ``` without requiring the model to obey perfectly.
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.IGNORECASE | re.DOTALL)
    candidates = [fenced.group(1)] if fenced else []
    if not fenced:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            candidates.append(text[start : end + 1])

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    return None


def parse_structured_review(raw_text: str) -> tuple[str, list[dict]]:
    payload = _extract_json_object(raw_text)
    if payload is None or not isinstance(payload.get("issues", []), list):
        raise ValueError("AI review response was not valid JSON with an issues array")

    normalized = {
        "summary": _clean_text(payload.get("summary")) or "No summary generated.",
        "issues": [_normalize_issue(item) for item in payload.get("issues", []) if isinstance(item, dict)],
    }
    validated = ReviewAIResult.model_validate(normalized)
    return validated.summary, [issue.model_dump() for issue in validated.issues]


def _strip_markdown_heading(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text.strip())
    # Prefer an initial bold heading as the title when present.
    bold = re.match(r"^\*\*(.+?)\*\*", text, re.DOTALL)
    if bold:
        return _clean_text(bold.group(1))
    text = re.sub(r"\*{1,3}", "", text)
    text = re.sub(r"_{1,3}", "", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return text.strip().rstrip(":").strip()


def parse_legacy_review(raw_text: str) -> tuple[str, list[dict]]:
    """Best-effort parser for old Markdown responses already in circulation."""
    text = (raw_text or "").strip()
    summary = "No summary parsed."

    summary_match = re.search(r"Summary\s*:\s*(.*?)(?=\n\s*Issues\s*:|\Z)", text, re.IGNORECASE | re.DOTALL)
    if summary_match:
        summary = summary_match.group(1).strip()
    else:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if paragraphs:
            summary = paragraphs[0]

    issues_match = re.search(r"Issues\s*:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
    if not issues_match:
        return summary, []

    content = issues_match.group(1).strip()
    # Normal numbered Markdown blocks first; then fall back to a single block.
    blocks = [b.strip() for b in re.split(r"(?m)^\s*\d+[.)]\s+", content) if b.strip()]
    if not blocks:
        blocks = [content]

    issues: list[dict] = []
    for block in blocks:
        line_match = re.search(r"(?:\*{0,2}\s*)?line\s*(?:number)?\s*:?\s*(\d+)", block, re.IGNORECASE)
        line_num = int(line_match.group(1)) if line_match else None

        severity_match = re.search(r"(?:\*{0,2}\s*)severity\s*:?\s*(high|medium|low|critical|warning)", block, re.IGNORECASE)
        severity = _normalize_severity(severity_match.group(1) if severity_match else block)

        exp_match = re.search(r"\*{0,2}\s*(?:Explanation|Description|Details?|Root Cause)\s*:\s*\*{0,2}", block, re.IGNORECASE)
        fix_match = re.search(r"\*{0,2}\s*(?:Suggested\s*Fix|Fix|Recommendation|Suggestion|Solution)\s*:\s*\*{0,2}", block, re.IGNORECASE)

        # A malformed one-line response often begins with **Title**...***Line:**.
        if exp_match:
            title_part = block[: line_match.start() if line_match else exp_match.start()]
            explanation_start = exp_match.end()
            explanation_end = fix_match.start() if fix_match and fix_match.start() > explanation_start else len(block)
            explanation = block[explanation_start:explanation_end].strip()
        else:
            title_part = block[: line_match.start() if line_match else len(block)]
            explanation = block[line_match.end():].strip(" -:\n") if line_match else block
            if fix_match:
                explanation = block[(line_match.end() if line_match else 0):fix_match.start()].strip(" -:\n")

        title = _strip_markdown_heading(title_part)
        # If title has a separator before explanatory prose, keep only the heading.
        title = re.split(r"\s+-\s+", title, maxsplit=1)[0].strip()
        title = re.sub(r"\s+-\s*$", "", title).strip()
        if not title:
            title = "Code issue"

        suggested_fix = None
        if fix_match:
            suggested_fix = block[fix_match.end():].strip()
        elif re.search(r"suggested\s*fix", explanation, re.IGNORECASE):
            inline_fix = re.split(r"suggested\s*fix\s*:\s*", explanation, maxsplit=1, flags=re.IGNORECASE)
            if len(inline_fix) == 2:
                explanation, suggested_fix = inline_fix[0].strip(), inline_fix[1].strip()

        issues.append({
            "title": _clean_text(title),
            "explanation": _clean_text(explanation) or "No detailed explanation available.",
            "suggested_fix": _clean_text(suggested_fix) or None,
            "severity": severity,
            "line": line_num,
        })

    return _clean_text(summary) or "No summary generated.", issues


def parse_raw_review(raw_text: str) -> tuple[str, list[dict]]:
    """Prefer strict JSON; use the legacy parser only as a compatibility fallback."""
    try:
        return parse_structured_review(raw_text)
    except ValueError:
        return parse_legacy_review(raw_text)
