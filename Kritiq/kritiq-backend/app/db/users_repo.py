# Sayeed domain - Database operations for users
from app.db.mongo_client import db_client

class UsersRepository:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = db_client.get_collection("users")
        return self._collection

    async def create_user(self, user_data: dict) -> dict:
        self.collection.insert_one(user_data)
        return user_data

    async def get_by_email(self, email: str) -> dict:
        return self.collection.find_one({"email": email})

users_repo = UsersRepository()

