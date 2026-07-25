# Sayeed domain - MongoDB connection client
# pyrefly: ignore [missing-import]
from pymongo import MongoClient
from app.core.config import settings

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        # Create required database indexes
        try:
            self.db["users"].create_index("email", unique=True)
            self.db["reviews"].create_index("user_id")
            self.db["translations"].create_index("user_id")
            self.db["history"].create_index("user_id")
        except Exception as e:
            import logging
            logging.getLogger("app").warning("Could not create database indexes: %s", str(e))



    def get_collection(self, name: str):
        if self.db is None:
            self.connect(settings.MONGODB_URI, settings.DATABASE_NAME)
        return self.db[name]

db_client = MongoDBClient()

