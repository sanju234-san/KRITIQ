"""
Pydantic v2 models for incoming GitHub webhook events.
"""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


class WebhookPayload(BaseModel):
    """
    Normalised payload extracted from a GitHub push / pull_request event.

    Only the fields KRITIQ cares about are kept — the raw GitHub payload
    is much larger and varies between event types.
    """

    repo_url: str = Field(
        ..., description="Full HTTPS URL of the repository"
    )
    commit_sha: str = Field(
        ..., description="Head commit SHA that triggered this event"
    )
    live_url: Optional[str] = Field(
        default=None,
        description="Optional deployed preview / production URL",
    )


class WebhookEvent(BaseModel):
    """Wrapper that pairs an event type with its parsed payload."""

    event_type: Literal["push", "pull_request"] = Field(
        ..., description="GitHub event type"
    )
    payload: WebhookPayload
