"""
Pydantic v2 models for the review report aggregate.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.issue import Fix, FlaggedIssue


class StatusEnum(str, Enum):
    """Pipeline execution status."""

    pending = "pending"
    running = "running"
    complete = "complete"
    failed = "failed"


class StepStatusEnum(str, Enum):
    """Status of an individual pipeline step."""

    pending = "pending"
    running = "running"
    complete = "complete"
    failed = "failed"


class PipelineStep(BaseModel):
    """Represents a single step in the agentic pipeline."""

    name: str  # e.g., "clone_repo", "code_review", "auto_fix", "screenshot_uml", "readme_writer"
    status: StepStatusEnum = StepStatusEnum.pending
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


class ReviewReport(BaseModel):
    """Top-level report produced at the end of an agent pipeline run."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    repo_url: str
    commit_sha: str

    flags: List[FlaggedIssue] = Field(default_factory=list)
    fixes: List[Fix] = Field(default_factory=list)

    readme_path: Optional[str] = None
    screenshot_paths: List[str] = Field(default_factory=list)
    uml_path: Optional[str] = None
    summary: Optional[str] = None

    status: StatusEnum = StatusEnum.pending
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    
    # ── Progress and timing additions ────────────────────
    steps: List[PipelineStep] = Field(default_factory=list)
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None

