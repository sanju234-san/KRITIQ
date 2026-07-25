# Sayeed domain - Database operations for connected repositories
from app.db.mongo_client import db_client
import uuid
from datetime import datetime

class RepositoriesRepository:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = db_client.get_collection("repositories")
        return self._collection

    async def add_repository(self, repo_data: dict) -> dict:
        repo_data["_id"] = str(uuid.uuid4())
        repo_data["created_at"] = datetime.utcnow().isoformat()
        self.collection.insert_one(repo_data)
        return repo_data

    async def get_repositories_by_user(self, user_id: str) -> list:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        return list(cursor)

repositories_repo = RepositoriesRepository()
