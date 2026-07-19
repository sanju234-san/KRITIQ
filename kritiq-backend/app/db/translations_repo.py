# Sayeed domain - Database operations for translations
from app.db.mongo_client import db_client
import uuid
from datetime import datetime

class TranslationsRepository:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = db_client.get_collection("translations")
        return self._collection

    async def save_translation(self, user_id: str, translation_data: dict) -> dict:
        translation_data["_id"] = str(uuid.uuid4())
        translation_data["user_id"] = user_id
        translation_data["created_at"] = datetime.utcnow().isoformat()
        self.collection.insert_one(translation_data)
        return translation_data

    async def get_translation_by_id(self, translation_id: str) -> dict:
        return self.collection.find_one({"_id": translation_id})

    async def get_translations_by_user(self, user_id: str, limit: int = 20, skip: int = 0) -> list:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)


translations_repo = TranslationsRepository()

