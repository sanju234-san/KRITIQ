# Sayeed domain - Review request/response schemas
from pydantic import BaseModel
from typing import List, Optional

class ReviewIssue(BaseModel):
    title: str
    explanation: str
    suggested_fix: Optional[str] = None
    severity: Optional[str] = None
    line: Optional[int] = None

class ReviewRequest(BaseModel):
    code: str
    language: Optional[str] = None
    repo_url: Optional[str] = None
    filename: Optional[str] = None

class ReviewResponse(BaseModel):
    review_id: str
    summary: str
    issues: List[ReviewIssue]
    raw_output: Optional[str] = None
