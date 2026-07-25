from fastapi import APIRouter, Depends, status
from app.auth.dependencies import get_current_user
from app.db.history_repo import history_repo
from app.models.explanation_models import ExplanationRequest, ExplanationResponse
from ai_agent.explanation_service import explain_code
import anyio

# Sayeed domain (Integrates with Sanjeevni's explanation_service)
router = APIRouter()

@router.post(
    "/explain", 
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate code explanations in plain English",
    description="Analyzes the provided code block and returns a detailed human-friendly explanation of its functionality.",
    response_description="Detailed description explanation of the code snippet",
    responses={
        200: {"description": "Explanation successfully generated and returned."},
        401: {"description": "Unauthorized - Missing or invalid JWT session token."},
        422: {"description": "Validation Error - Code field is empty or contains unsupported language name."}
    }
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
