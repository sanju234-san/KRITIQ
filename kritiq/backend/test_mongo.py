"""
test_mongo.py — Unit test script to verify MongoRepository CRUD operations.
Mocks the motor.motor_asyncio client calls.
"""

import os
import sys

# Set up dummy environment variables for settings validation before any app imports
os.environ["GROQ_API_KEY"] = "mock_groq_key"
os.environ["GITHUB_TOKEN"] = "mock_github_token"
os.environ["GITHUB_WEBHOOK_SECRET"] = "mock_webhook_secret"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["MONGODB_DB_NAME"] = "test_db"

import asyncio
from unittest.mock import AsyncMock, MagicMock

# Add backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.services.mongo_repository import MongoRepository
from app.schemas.report import ReviewReport, StatusEnum
from app.schemas.issue import FlaggedIssue, SeverityEnum, CategoryEnum


async def main():
    print("Testing KRITIQ MongoRepository CRUD Operations...")

    # Instantiate repository
    repo = MongoRepository(
        uri="mongodb://localhost:27017",
        db_name="test_db",
    )

    # Mock client and database objects
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_db.reports = mock_collection
    mock_client.__getitem__.return_value = mock_db
    repo._client = mock_client
    repo._db = mock_db

    # Define mock data report
    report = ReviewReport(
        repo_url="https://github.com/octocat/my-repo",
        commit_sha="abc123def456",
        flags=[
            FlaggedIssue(
                file_path="main.py",
                line_number=10,
                severity=SeverityEnum.critical,
                category=CategoryEnum.security,
                description="SQL Injection",
                suggested_fix="Fix it",
            )
        ],
        fixes=[],
        status=StatusEnum.complete,
        summary="A security issues report",
    )

    # 1. Test save_report
    mock_replace = AsyncMock()
    mock_collection.replace_one = mock_replace

    saved_id = await repo.save_report(report)

    assert saved_id == report.id
    mock_replace.assert_called_once()
    call_args = mock_replace.call_args[0]
    
    # Assert filter maps correctly to _id
    assert call_args[0] == {"_id": report.id}
    
    # Assert document structure maps Pydantic id -> _id
    assert call_args[1]["_id"] == report.id
    assert "id" not in call_args[1]

    print("[OK] save_report operation verification passed.")

    # 2. Test get_report
    mock_find_one = AsyncMock()
    mock_collection.find_one = mock_find_one

    # Test 2a: String UUID retrieval
    db_doc = report.model_dump(mode="json")
    db_doc["_id"] = db_doc.pop("id")
    mock_find_one.return_value = db_doc.copy()

    retrieved = await repo.get_report(report.id)

    assert retrieved is not None
    assert retrieved.id == report.id
    assert retrieved.repo_url == report.repo_url
    assert len(retrieved.flags) == 1
    assert retrieved.flags[0].description == "SQL Injection"

    mock_find_one.assert_called_with({"_id": report.id})

    # Test 2b: ObjectId retrieval
    from bson import ObjectId
    obj_id = ObjectId()
    db_doc_obj = report.model_dump(mode="json")
    db_doc_obj["_id"] = obj_id
    db_doc_obj.pop("id")
    mock_find_one.reset_mock()
    mock_find_one.return_value = db_doc_obj.copy()

    retrieved_obj = await repo.get_report(str(obj_id))
    assert retrieved_obj is not None
    assert retrieved_obj.id == str(obj_id)
    mock_find_one.assert_called_with({"_id": obj_id})

    print("[OK] get_report operation (both UUID and ObjectId) verification passed.")

    # 3. Test list_reports (pagination & sorting)
    mock_cursor = MagicMock()
    mock_collection.find.return_value = mock_cursor
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    # Simulate cursor async iteration
    async def mock_async_iterator(self):
        yield db_doc.copy()

    mock_cursor.__aiter__ = mock_async_iterator

    reports = await repo.list_reports(
        repo_url="https://github.com/octocat/my-repo",
        skip=0,
        limit=10,
    )

    assert len(reports) == 1
    assert reports[0].id == report.id
    assert reports[0].repo_url == "https://github.com/octocat/my-repo"

    mock_collection.find.assert_called_once_with({"repo_url": "https://github.com/octocat/my-repo"})
    mock_cursor.sort.assert_called_once_with("created_at", -1)
    mock_cursor.skip.assert_called_once_with(0)
    mock_cursor.limit.assert_called_once_with(10)

    print("[OK] list_reports operation verification passed.")
    print("\n[SUCCESS] MongoRepository testing passed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
