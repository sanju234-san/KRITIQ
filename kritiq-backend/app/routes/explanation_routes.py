from fastapi import APIRouter, Depends, status
from app.auth.dependencies import get_current_user
from app.db.history_repo import history_repo
from app.models.explanation_models import ExplanationRequest, ExplanationResponse
from ai_agent.explanation_service import explain_code
import anyio

router = APIRouter()

@router.post(
    "/", 
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate code explanations in plain English",
    description="Analyzes the provided code block and returns a detailed human-friendly explanation of its functionality."
)
@router.post(
    "/explain", 
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
async def explain_issue(payload: ExplanationRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    
    explanation = await anyio.to_thread.run_sync(explain_code, payload.code, payload.language)
    
    details = {
        "language": payload.language,
        "code_snippet": payload.code[:100] + "..." if len(payload.code) > 100 else payload.code
    }
    await history_repo.log_activity(
        user_id=user_id,
        type="explanation",
        summary=f"Requested explanation for {payload.language} code",
        details=details
    )
    
    return {"explanation": explanation}
