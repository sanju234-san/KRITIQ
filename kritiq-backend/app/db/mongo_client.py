# Sayeed domain - MongoDB connection client
from pymongo import MongoClient
from app.core.config import settings

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, name: str):
        if self.db is None:
            self.connect(settings.MONGODB_URI, settings.DATABASE_NAME)
        return self.db[name]

db_client = MongoDBClient()

