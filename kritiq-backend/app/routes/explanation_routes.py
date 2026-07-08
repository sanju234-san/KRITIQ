from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.db.history_repo import history_repo
from ai_agent.explanation_service import explain_code

# Sayeed domain (Integrates with Sanjeevni's explanation_service)
router = APIRouter()

class ExplanationRequest(BaseModel):
    code: str
    language: str = "python"

@router.post("/explain")
async def explain_issue(payload: ExplanationRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    
    explanation = explain_code(payload.code, payload.language)
    
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
