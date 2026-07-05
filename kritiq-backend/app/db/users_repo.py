# Sayeed domain - Database operations for users
from app.db.mongo_client import db_client

class UsersRepository:
    def __init__(self):
        # self.collection = db_client.get_collection("users")
        pass

    async def create_user(self, user_data: dict) -> dict:
        # TODO: Store in MongoDB
        return user_data

    async def get_by_email(self, email: str) -> dict:
        # TODO: Retrieve from MongoDB
        return None

users_repo = UsersRepository()
