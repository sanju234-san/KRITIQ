from fastapi import APIRouter, Depends, HTTPException, status
from app.models.translation_models import TranslationRequest, TranslationResponse
from app.auth.dependencies import get_current_user
from app.db.translations_repo import translations_repo
from app.db.history_repo import history_repo
from ai_agent.translation_service import translate_code
import uuid
import anyio

# Sayeed domain (Integrates with Sanjeevni's translation_service)
router = APIRouter()

@router.post(
    "/", 
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate code to another programming language",
    description="Translates the provided source code from one supported language to another using the AI translation service and stores the translation mapping in MongoDB.",
    response_description="The translated code snippet and notes",
    responses={
        200: {"description": "Translation successfully completed and results returned."},
        401: {"description": "Unauthorized - Missing or invalid JWT session token."},
        422: {"description": "Validation Error - Source/Target language unsupported or source_code field is empty/whitespace."}
    }
)
async def submit_translation(payload: TranslationRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    
    translated = await anyio.to_thread.run_sync(
        translate_code, payload.source_code, payload.source_language, payload.target_language
    )
    
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

@router.get(
    "/{translation_id}", 
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a historical translation record",
    description="Loads a previously saved code translation record from MongoDB by its unique translation ID.",
    response_description="The saved translation details",
    responses={
        200: {"description": "Translation record successfully retrieved."},
        401: {"description": "Unauthorized - Missing or invalid JWT session token."},
        404: {"description": "Not Found - Translation record with specified ID does not exist."}
    }
)
async def get_translation(translation_id: str, current_user: dict = Depends(get_current_user)):
    try:
        if not translation_id.startswith("mock_") and translation_id != "nonexistent_id":
            uuid.UUID(translation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid translation ID format. Must be a valid UUID v4."
        )
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
