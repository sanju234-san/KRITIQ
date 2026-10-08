# Sayeed domain - Database operations for users
from app.db.mongo_client import db_client
from datetime import datetime, timezone

class UsersRepository:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = db_client.get_collection("users")
        return self._collection

    async def create_user(self, user_data: dict) -> dict:
        user_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        self.collection.insert_one(user_data)
        return user_data

    async def get_by_email(self, email: str) -> dict | None:
        return self.collection.find_one({"email": email})

    async def get_by_github_id(self, github_id: str | int) -> dict | None:
        return self.collection.find_one({"github_id": str(github_id)})

    async def update_user(self, user_id, updates: dict) -> dict | None:
        if updates:
            self.collection.update_one({"_id": user_id}, {"$set": updates})
        return self.collection.find_one({"_id": user_id})

    async def upsert_github_user(self, *, github_id: str, email: str, name: str,
                                  github_username: str, github_access_token: str,
                                  avatar_url: str | None = None) -> dict:
        existing = self.collection.find_one({"github_id": str(github_id)})
        patch = {
            "github_id": str(github_id),
            "github_username": github_username,
            "github_access_token": github_access_token,
            "avatar_url": avatar_url,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if existing:
            new_email = existing.get("email") or email
            new_name = existing.get("name") or name
            patch["email"] = new_email
            patch["name"] = new_name
            self.collection.update_one({"_id": existing["_id"]}, {"$set": patch})
            return self.collection.find_one({"_id": existing["_id"]})

        by_email = self.collection.find_one({"email": email}) if email else None
        if by_email:
            patch["email"] = by_email["email"]
            patch["name"] = by_email.get("name") or name
            self.collection.update_one({"_id": by_email["_id"]}, {"$set": patch})
            return self.collection.find_one({"_id": by_email["_id"]})

        doc = {
            "name": name,
            "email": email,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **patch,
        }
        self.collection.insert_one(doc)
        return doc

users_repo = UsersRepository()

