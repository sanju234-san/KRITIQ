# Sayeed domain - Database operations for reviews
from app.db.mongo_client import db_client
import uuid
from datetime import datetime

class ReviewsRepository:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = db_client.get_collection("reviews")
        return self._collection

    async def save_review(self, user_id: str, review_data: dict) -> dict:
        review_data["_id"] = str(uuid.uuid4())
        review_data["user_id"] = user_id
        review_data["created_at"] = datetime.utcnow().isoformat()
        self.collection.insert_one(review_data)
        return review_data

    async def get_review_by_id(self, review_id: str) -> dict:
        return self.collection.find_one({"_id": review_id})

    async def get_reviews_by_user(self, user_id: str) -> list:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        return list(cursor)

reviews_repo = ReviewsRepository()

