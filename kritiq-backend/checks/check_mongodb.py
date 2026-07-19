import os
import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")

print("=" * 60)
print("MongoDB Connection Checker")
print("=" * 60)

if not uri:
    print("[ERROR] MONGODB_URI not found")
    exit()

print(f"URI Found: {uri[:35]}...")

start = time.time()

try:
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )

    client.admin.command("ping")

    elapsed = time.time() - start

    print("[SUCCESS] MongoDB Connected")
    print(f"Time: {elapsed:.2f}s")

    print("\nDatabases:")
    for db in client.list_database_names():
        print("-", db)

except ServerSelectionTimeoutError as e:
    elapsed = time.time() - start

    print("\n[ERROR] Connection Failed")
    print(f"Time: {elapsed:.2f}s")
    print(e)

except Exception as e:
    print("\n[ERROR] Unexpected Error")
    print(e)
