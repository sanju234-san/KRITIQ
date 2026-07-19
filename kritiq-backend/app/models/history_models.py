# Sayeed domain - History list schema
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class HistoryItem(BaseModel):
    id: str = Field(
        ..., 
        description="The unique database log ID of the history entry", 
        example="aa82e389-9831-4e0d-a02c-7b94b0dfa12d"
    )
    type: str = Field(
        ..., 
        description="The type of activity logged (review, translation, explanation)", 
        example="review"
    )
    timestamp: str = Field(
        ..., 
        description="ISO timestamp when the activity occurred", 
        example="2026-07-16T19:51:47Z"
    )
    summary: str = Field(
        ..., 
        description="A brief description of what the user did", 
        example="Reviewed python file: main.py"
    )
    details: Dict[str, Any] = Field(
        ..., 
        description="Activity-specific attributes and reference IDs", 
        example={"review_id": "6a71e355-6671-460d-a02c-7b94b0dfa72d", "issues_count": 3}
    )

class HistoryListResponse(BaseModel):
    history: List[HistoryItem] = Field(
        ..., 
        description="A paginated list of the user's historical code activities"
    )
