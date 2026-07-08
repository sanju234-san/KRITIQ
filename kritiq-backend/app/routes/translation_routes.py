from fastapi import APIRouter, Depends, HTTPException, status
from app.models.translation_models import TranslationRequest, TranslationResponse
from app.auth.dependencies import get_current_user
from app.db.translations_repo import translations_repo
from app.db.history_repo import history_repo
from ai_agent.translation_service import translate_code

# Sayeed domain (Integrates with Sanjeevni's translation_service)
router = APIRouter()

@router.post("/", response_model=TranslationResponse)
async def submit_translation(payload: TranslationRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    
    # Call Gemini translation
    translated = translate_code(payload.source_code, payload.source_language, payload.target_language)
    
    translation_data = {
        "source_code": payload.source_code,
        "source_language": payload.source_language,
        "target_language": payload.target_language,
        "translated_code": translated
    }
    saved_doc = await translations_repo.save_translation(user_id, translation_data)
    
    details = {
        "source_language": payload.source_language,
        "target_language": payload.target_language
    }
    await history_repo.log_activity(
        user_id=user_id,
        type="translation",
        summary=f"Translated from {payload.source_language} to {payload.target_language}",
        details=details
    )
    
    return {
        "translation_id": saved_doc["_id"],
        "translated_code": translated,
        "notes": f"Successfully translated from {payload.source_language} to {payload.target_language}."
    }

@router.get("/{translation_id}", response_model=TranslationResponse)
async def get_translation(translation_id: str, current_user: dict = Depends(get_current_user)):
    doc = await translations_repo.get_translation_by_id(translation_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    return {
        "translation_id": doc["_id"],
        "translated_code": doc["translated_code"],
        "notes": f"Retrieved translation from {doc.get('source_language')} to {doc.get('target_language')}."
    }
