from fastapi import APIRouter
from app.models.translation_models import TranslationRequest, TranslationResponse

# Sayeed domain (Integrates with Sanjeevni's translation_service)
router = APIRouter()

@router.post("/", response_model=TranslationResponse)
async def submit_translation(payload: TranslationRequest):
    # TODO: Call translation_service from ai_agent
    return {
        "translation_id": "mock-trans-id",
        "status": "completed",
        "translated_code": "System.out.println(\"Hello World\");"
    }

@router.get("/{translation_id}", response_model=TranslationResponse)
async def get_translation(translation_id: str):
    # TODO: Fetch translation from translations_repo
    return {
        "translation_id": translation_id,
        "status": "completed",
        "translated_code": "System.out.println(\"Hello World\");"
    }
