# Sayeed domain - Database operations for histories
from app.db.mongo_client import db_client
import uuid
from datetime import datetime

class HistoryRepository:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = db_client.get_collection("history")
        return self._collection

    async def log_activity(self, user_id: str, type: str, summary: str, details: dict) -> dict:
        activity_data = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": type,
            "summary": summary,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.collection.insert_one(activity_data)
        return activity_data

    async def get_history_by_user(self, user_id: str, limit: int = 20, skip: int = 0, activity_type: str = None) -> list:
        query = {"user_id": user_id}
        if activity_type:
            query["type"] = activity_type
        cursor = self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        return list(cursor)


history_repo = HistoryRepository()
