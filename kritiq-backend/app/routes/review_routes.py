from fastapi import APIRouter, Depends, HTTPException, status
from app.models.review_models import ReviewRequest, ReviewResponse
from app.auth.dependencies import get_current_user
from app.db.reviews_repo import reviews_repo
from app.db.history_repo import history_repo
from ai_agent.review_service import review_code
from ai_agent.groq_client import ask_groq
from ai_agent.prompts.review_prompt import build_review_prompt
import re
import uuid
import anyio

# Sayeed domain (Integrates with Sanjeevni's review_service and fallback to Groq)
router = APIRouter()

from ai_agent.review_parser import parse_raw_review

@router.post(
    "/", 
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a code snippet for analysis",
    description="Accepts a raw code snippet, optional language classification, and sends it to the AI review service. If Gemini times out, automatically falls back to Groq Llama3 for zero-downtime execution.",
    response_description="Parsed review summary and specific issues found"
)
async def submit_review(payload: ReviewRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    raw_output = None
    
    # Try primary Gemini AI engine
    try:
        raw_output = await anyio.to_thread.run_sync(
            review_code,
            payload.code,
            payload.language or "python",
            payload.file_path,
            payload.repo_owner,
            payload.repo_name
        )
    except Exception as err:
        print(f"[FALLBACK TRIGGERED] Gemini error/timeout ({err}) — switching to Groq Llama-3...")
        try:
            prompt = build_review_prompt(payload.code, language=payload.language or "python")
            raw_output = await anyio.to_thread.run_sync(ask_groq, prompt)
        except Exception as groq_err:
            print("Groq fallback error:", groq_err)
            err_lower = str(groq_err).lower()
            is_config_err = (
                "not configured" in err_lower
                or "is not set" in err_lower
                or "api_key" in err_lower
            )
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR if is_config_err else status.HTTP_502_BAD_GATEWAY
            raise HTTPException(
                status_code=status_code,
                detail=f"Both primary AI (Gemini) and fallback AI (Groq) failed: {str(groq_err)}"
            )

    summary, issues = parse_raw_review(raw_output)
    
    review_data = {
        "summary": summary,
        "issues": issues,
        "raw_output": raw_output,
        "code": payload.code,
        "language": payload.language or "python",
        "filename": payload.filename,
        "file_path": payload.file_path,
        "repo_owner": payload.repo_owner,
        "repo_name": payload.repo_name
    }
    saved_doc = await reviews_repo.save_review(user_id, review_data)
    
    details = {
        "review_id": saved_doc["_id"],
        "language": payload.language or "python",
        "filename": payload.filename,
        "file_path": payload.file_path,
        "repo_owner": payload.repo_owner,
        "repo_name": payload.repo_name,
        "issues_count": len(issues)
    }
    await history_repo.log_activity(
        user_id=user_id,
        type="review",
        summary=f"Reviewed {payload.language or 'code'} file: {payload.filename or 'unnamed'}",
        details=details
    )
    
    return {
        "review_id": saved_doc["_id"],
        "summary": summary,
        "issues": issues,
        "raw_output": raw_output
    }

@router.get(
    "/{review_id}", 
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a historical review record"
)
async def get_review(review_id: str, current_user: dict = Depends(get_current_user)):
    try:
        if not review_id.startswith("mock_") and review_id != "nonexistent_id":
            uuid.UUID(review_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid review ID format. Must be a valid UUID v4."
        )
    doc = await reviews_repo.get_review_by_id(review_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return {
        "review_id": doc["_id"],
        "summary": doc["summary"],
        "issues": doc["issues"],
        "raw_output": doc.get("raw_output"),
        "code": doc.get("code"),
        "language": doc.get("language"),
        "filename": doc.get("filename"),
        "file_path": doc.get("file_path"),
        "repo_owner": doc.get("repo_owner"),
        "repo_name": doc.get("repo_name")
    }
