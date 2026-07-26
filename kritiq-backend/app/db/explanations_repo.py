# Sayeed domain - Database operations for explanations
from app.db.mongo_client import db_client
import uuid
from datetime import datetime

class ExplanationsRepository:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = db_client.get_collection("explanations")
        return self._collection

    async def save_explanation(self, user_id: str, explanation_data: dict) -> dict:
        explanation_data["_id"] = str(uuid.uuid4())
        explanation_data["user_id"] = user_id
        explanation_data["created_at"] = datetime.utcnow().isoformat()
        self.collection.insert_one(explanation_data)
        return explanation_data

    async def get_explanation_by_id(self, explanation_id: str) -> dict:
        return self.collection.find_one({"_id": explanation_id})

    async def get_explanations_by_user(self, user_id: str, limit: int = 20, skip: int = 0) -> list:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)


explanations_repo = ExplanationsRepository()
