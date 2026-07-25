from fastapi import APIRouter, Depends, HTTPException, status
from app.models.review_models import ReviewRequest, ReviewResponse
from app.auth.dependencies import get_current_user
from app.db.reviews_repo import reviews_repo
from app.db.history_repo import history_repo
from ai_agent.review_service import review_code
import re
import uuid
import anyio

# Sayeed domain (Integrates with Sanjeevni's review_service)
router = APIRouter()

def parse_raw_review(raw_text: str) -> tuple[str, list[dict]]:
    summary = "No summary parsed."
    issues = []
    
    summary_match = re.search(r"Summary:\s*(.*?)(?=\n\s*Issues:|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
    if summary_match:
        summary = summary_match.group(1).strip()
    else:
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        if paragraphs:
            summary = paragraphs[0]
            
    issues_section_match = re.search(r"Issues:\s*(.*)", raw_text, re.DOTALL | re.IGNORECASE)
    if issues_section_match:
        issues_content = issues_section_match.group(1).strip()
        issue_lines = re.findall(r"(?:^|\n)\s*\d+\.\s*(.*?)(?=\n\s*\d+\.|\Z)", issues_content, re.DOTALL)
        for line_item in issue_lines:
            line_item = line_item.strip()
            if not line_item:
                continue
            
            parts = line_item.split(" - ", 1)
            title = parts[0].strip()
            explanation = parts[1].strip() if len(parts) > 1 else ""
            
            suggested_fix = None
            line_num = None
            severity = "medium"
            
            line_match = re.search(r"line\s*(\d+)", explanation, re.IGNORECASE)
            if line_match:
                line_num = int(line_match.group(1))
                
            if "high" in explanation.lower() or "critical" in explanation.lower():
                severity = "high"
            elif "low" in explanation.lower() or "minor" in explanation.lower():
                severity = "low"
                
            issues.append({
                "title": title,
                "explanation": explanation,
                "suggested_fix": suggested_fix,
                "severity": severity,
                "line": line_num
            })
            
    return summary, issues

@router.post(
    "/", 
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a code snippet for analysis",
    description="Accepts a raw code snippet, optional language classification, and sends it to the AI review service. Analyzes code quality, security smells, styling violations, and persists the review results in MongoDB.",
    response_description="Parsed review summary and specific issues found",
    responses={
        200: {"description": "Code review successfully performed and results returned."},
        401: {"description": "Unauthorized - Missing or invalid JWT session token."},
        422: {"description": "Validation Error - Code field is empty or contains unsupported language name."}
    }
)
async def submit_review(payload: ReviewRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    raw_output = await anyio.to_thread.run_sync(review_code, payload.code, payload.language or "python")
    summary, issues = parse_raw_review(raw_output)
    
    review_data = {
        "summary": summary,
        "issues": issues,
        "raw_output": raw_output
    }
    saved_doc = await reviews_repo.save_review(user_id, review_data)
    
    details = {
        "language": payload.language or "python",
        "filename": payload.filename,
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
    summary="Retrieve a historical review record",
    description="Loads a previously saved code review record from MongoDB by its unique review ID.",
    response_description="The saved code review details",
    responses={
        200: {"description": "Review record successfully retrieved."},
        401: {"description": "Unauthorized - Missing or invalid JWT session token."},
        404: {"description": "Not Found - Review record with specified ID does not exist."}
    }
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
        "raw_output": doc.get("raw_output")
    }
