"""
Report endpoints — retrieves and lists review reports from MongoDB.
"""

from typing import List
from uuid import uuid4
from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.schemas.report import ReviewReport, StatusEnum
from app.schemas.webhook import WebhookPayload
from app.services.mongo_repository import mongo_repository
from app.core.orchestrator import run_pipeline

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/", response_model=List[ReviewReport])
async def list_reports(repo_url: str, skip: int = 0, limit: int = 10):
    """Return all review reports for a specific repository URL."""
    return await mongo_repository.list_reports(repo_url, skip=skip, limit=limit)


@router.post("/run", status_code=202)
async def run_review(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """Trigger a new codebase audit pipeline in the background."""
    if not payload.repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required")
    
    report_id = str(uuid4())
    
    # Pre-create pending report record in MongoDB
    report = ReviewReport(
        id=report_id,
        repo_url=payload.repo_url,
        commit_sha=payload.commit_sha or "main",
        status=StatusEnum.pending,
        flags=[],
        fixes=[],
        screenshot_paths=[],
    )
    await mongo_repository.save_report(report)

    # Queue the background task
    background_tasks.add_task(run_pipeline, payload, report_id)
    
    return {"report_id": report_id, "status": "pending"}


@router.get("/recent", response_model=List[ReviewReport])
async def list_recent_reports(skip: int = 0, limit: int = 20):
    """Retrieve the most recent review reports across all repositories."""
    return await mongo_repository.list_all_reports(skip=skip, limit=limit)


@router.get("/{report_id}", response_model=ReviewReport)
async def get_report(report_id: str):
    """Fetch a single report by ID."""
    report = await mongo_repository.get_report(report_id)
    if not report:
         raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/health")
async def reports_health():
    """Lightweight health-check for this sub-router."""
    return {"status": "ok"}
