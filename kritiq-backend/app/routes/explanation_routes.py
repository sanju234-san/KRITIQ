from fastapi import APIRouter

# Sayeed domain (Integrates with Sanjeevni's explanation_service)
router = APIRouter()

@router.post("/explain")
async def explain_issue(issue_id: str):
    # TODO: Call explanation_service from ai_agent
    return {"explanation": "This issue is flagged because of potential SQL Injection risk."}
