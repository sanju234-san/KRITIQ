"""
MongoRepository — Async repository for managing ReviewReport documents in MongoDB.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings
from app.schemas.report import ReviewReport

logger = logging.getLogger("kritiq.mongo_repository")


class MongoRepository:
    """
    Repository layer for managing persistence of review reports in MongoDB.
    
    Uses the Motor async driver to execute operations non-blockingly.
    """

    def __init__(self, uri: str, db_name: str) -> None:
        self._uri = uri
        self._db_name = db_name
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    def connect(self) -> None:
        """Initialize the Motor client and database connections."""
        if self._client is not None:
            logger.warning("MongoDB client is already connected.")
            return

        logger.info("Connecting to MongoDB database: %s", self._db_name)
        self._client = AsyncIOMotorClient(self._uri)
        self._db = self._client[self._db_name]

    def close(self) -> None:
        """Close the active Motor client connection."""
        if self._client is None:
            logger.warning("MongoDB client is already disconnected.")
            return

        logger.info("Closing MongoDB connection.")
        self._client.close()
        self._client = None
        self._db = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Access the database handle. Raises error if database is not connected."""
        if self._db is None:
            raise RuntimeError("Database connection not initialized. Call connect() first.")
        return self._db

    async def ping(self) -> None:
        """Verify the database connection by sending a ping command."""
        if self._client is None:
            raise RuntimeError("Database connection not initialized.")
        await self._client.admin.command("ping")

    # ── CRUD Operations ──────────────────────────────────

    async def save_report(self, report: ReviewReport) -> str:
        """
        Insert a new ReviewReport document or update an existing one.
        
        Maps the Pydantic UUID `id` to the MongoDB `_id` field.
        """
        doc = report.model_dump(mode="json")
        # Map Pydantic 'id' to MongoDB '_id'
        doc["_id"] = doc.pop("id")

        await self.db.reports.replace_one(
            {"_id": doc["_id"]},
            doc,
            upsert=True
        )
        logger.info("Saved report_id=%s to reports collection", report.id)
        return report.id

    async def get_report(self, report_id: str) -> Optional[ReviewReport]:
        """
        Fetch a single ReviewReport from the database by its unique ID.
        Supports both ObjectId strings and string UUIDs.
        """
        query_id = report_id
        if ObjectId.is_valid(report_id):
            query_id = ObjectId(report_id)

        doc = await self.db.reports.find_one({"_id": query_id})
        
        # Fallback to string search if we checked with ObjectId and got nothing
        if not doc and isinstance(query_id, ObjectId):
            doc = await self.db.reports.find_one({"_id": report_id})

        if not doc:
            logger.debug("Report not found for report_id=%s", report_id)
            return None

        # Map '_id' back to 'id' as a string for validation
        doc["id"] = str(doc.pop("_id"))
        return ReviewReport.model_validate(doc)

    async def list_reports(
        self,
        repo_url: str,
        skip: int = 0,
        limit: int = 10,
    ) -> List[ReviewReport]:
        """
        Retrieve a paginated list of ReviewReports for a specific repository,
        sorted by creation date in descending order.
        """
        cursor = self.db.reports.find({"repo_url": repo_url})
        cursor = cursor.sort("created_at", -1).skip(skip).limit(limit)

        reports: List[ReviewReport] = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            reports.append(ReviewReport.model_validate(doc))

        logger.info("Listed %d reports for repo_url=%s", len(reports), repo_url)
        return reports

    async def list_all_reports(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ReviewReport]:
        """
        Retrieve a paginated list of all ReviewReports across all repositories,
        sorted by creation date in descending order.
        """
        cursor = self.db.reports.find({})
        cursor = cursor.sort("created_at", -1).skip(skip).limit(limit)

        reports: List[ReviewReport] = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            reports.append(ReviewReport.model_validate(doc))

        logger.info("Listed %d reports globally", len(reports))
        return reports


# ── Module-level Repository Instance ─────────────────────

mongo_repository = MongoRepository(
    uri=settings.MONGODB_URI,
    db_name=settings.MONGODB_DB_NAME
)
