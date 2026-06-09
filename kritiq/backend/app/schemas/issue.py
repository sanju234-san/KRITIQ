"""
Pydantic v2 models for flagged code issues and their fixes.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────

class SeverityEnum(str, Enum):
    """How critical a flagged issue is."""

    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class CategoryEnum(str, Enum):
    """Classification bucket for a flagged issue."""

    security = "security"
    bug = "bug"
    style = "style"
    performance = "performance"
    docs = "docs"


# ── Models ───────────────────────────────────────────────

class FlaggedIssue(BaseModel):
    """A single issue detected during code review."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    file_path: str
    line_number: int
    severity: SeverityEnum
    category: CategoryEnum
    description: str
    suggested_fix: str
    flagged_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Fix(BaseModel):
    """A code fix generated (and optionally validated) for a FlaggedIssue."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    issue_id: str
    original_code: str
    fixed_code: str
    explanation: str
    validated: bool = False
    commit_sha: Optional[str] = None
