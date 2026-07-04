# Sayeed domain - Review request/response schemas
from pydantic import BaseModel
from typing import List, Optional

class ReviewIssue(BaseModel):
    severity: str
    line: Optional[int] = None
    message: str

class ReviewRequest(BaseModel):
    language: str
    source: str  # 'repository' or 'upload'
    repository_id: Optional[str] = None
    file_path: Optional[str] = None
    code_content: Optional[str] = None
    request_translation: bool = False

class ReviewResponse(BaseModel):
    review_id: str
    status: str
    summary: str
    issues: List[ReviewIssue]
