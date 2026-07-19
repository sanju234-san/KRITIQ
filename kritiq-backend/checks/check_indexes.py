from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

db = client.get_default_database()

for name in db.list_collection_names():
    print(f"\n{name}")
    indexes = db[name].index_information()
    for idx in indexes:
        print(" ", idx)
