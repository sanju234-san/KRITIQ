# Sayeed domain - History list schema
from pydantic import BaseModel
from typing import List, Dict, Any

class HistoryItem(BaseModel):
    id: str
    type: str
    timestamp: str
    summary: str
    details: Dict[str, Any]

class HistoryListResponse(BaseModel):
    history: List[HistoryItem]
