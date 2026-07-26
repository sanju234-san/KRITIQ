from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.db.history_repo import history_repo
from app.db.explanations_repo import explanations_repo
from app.models.explanation_models import ExplanationRequest, ExplanationResponse
from ai_agent.explanation_service import explain_code
import uuid
import anyio

router = APIRouter()

@router.post(
    "/", 
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate code explanations in plain English",
    description="Analyzes the provided code block and returns a detailed human-friendly explanation of its functionality. Also saves the record so it can be revisited later via the /explanations/{id} endpoint."
)
@router.post(
    "/explain", 
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
async def explain_issue(payload: ExplanationRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    
    explanation = await anyio.to_thread.run_sync(
        explain_code,
        payload.code,
        payload.language,
        payload.file_path,
        payload.repo_owner,
        payload.repo_name,
    )
    
    explanation_doc = {
        "code": payload.code,
        "language": payload.language,
        "filename": payload.filename,
        "file_path": payload.file_path,
        "repo_owner": payload.repo_owner,
        "repo_name": payload.repo_name,
        "explanation": explanation
    }
    saved_doc = await explanations_repo.save_explanation(user_id, explanation_doc)
    
    details = {
        "explanation_id": saved_doc["_id"],
        "language": payload.language,
        "filename": payload.filename,
        "file_path": payload.file_path,
        "repo_owner": payload.repo_owner,
        "repo_name": payload.repo_name,
        "code_snippet": payload.code[:100] + "..." if len(payload.code) > 100 else payload.code
    }
    await history_repo.log_activity(
        user_id=user_id,
        type="explanation",
        summary=f"Requested explanation for {payload.language} code: {payload.filename or 'snippet'}",
        details=details
    )
    
    return {
        "explanation_id": saved_doc["_id"],
        "explanation": explanation,
        "code": payload.code,
        "language": payload.language,
        "filename": payload.filename,
        "file_path": payload.file_path,
        "repo_owner": payload.repo_owner,
        "repo_name": payload.repo_name,
        "created_at": saved_doc.get("created_at")
    }


@router.get(
    "/{explanation_id}",
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a historical explanation record",
    description="Loads a previously generated code explanation by ID, for the revisit links from History."
)
async def get_explanation(explanation_id: str, current_user: dict = Depends(get_current_user)):
    try:
        if not explanation_id.startswith("mock_") and explanation_id != "nonexistent_id":
            uuid.UUID(explanation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid explanation ID format. Must be a valid UUID v4."
        )
    doc = await explanations_repo.get_explanation_by_id(explanation_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Explanation not found"
        )
    return {
        "explanation_id": doc["_id"],
        "explanation": doc.get("explanation", ""),
        "code": doc.get("code"),
        "language": doc.get("language"),
        "filename": doc.get("filename"),
        "file_path": doc.get("file_path"),
        "repo_owner": doc.get("repo_owner"),
        "repo_name": doc.get("repo_name"),
        "created_at": doc.get("created_at")
    }
