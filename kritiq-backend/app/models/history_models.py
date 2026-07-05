# Sayeed domain - History list schema
from pydantic import BaseModel
from datetime import datetime

class HistoryResponse(BaseModel):
    history_id: str
    user_id: str
    ref_id: str
    ref_type: str  # 'review' or 'translation'
    timestamp: datetime
