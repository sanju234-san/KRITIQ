from fastapi import APIRouter, Depends
from app.models.history_models import HistoryListResponse, HistoryItem
from app.models.review_models import ReviewResponse
from app.models.translation_models import TranslationResponse
from app.auth.dependencies import get_current_user
from app.db.history_repo import history_repo
from app.db.reviews_repo import reviews_repo
from app.db.translations_repo import translations_repo
from typing import List

# Sayeed domain
router = APIRouter()

@router.get("/", response_model=HistoryListResponse)
async def get_history(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    logs = await history_repo.get_history_by_user(user_id)
    
    history_items = []
    for log in logs:
        history_items.append(
            HistoryItem(
                id=str(log.get("_id")),
                type=log.get("type"),
                timestamp=log.get("timestamp"),
                summary=log.get("summary"),
                details=log.get("details", {})
            )
        )
        
    return {"history": history_items}

@router.get("/reviews", response_model=List[ReviewResponse])
async def get_history_reviews(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    reviews = await reviews_repo.get_reviews_by_user(user_id)
    
    response_items = []
    for doc in reviews:
        response_items.append(
            ReviewResponse(
                review_id=str(doc.get("_id")),
                summary=doc.get("summary"),
                issues=doc.get("issues", []),
                raw_output=doc.get("raw_output")
            )
        )
    return response_items

@router.get("/translations", response_model=List[TranslationResponse])
async def get_history_translations(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user.get("_id"))
    translations = await translations_repo.get_translations_by_user(user_id)
    
    response_items = []
    for doc in translations:
        response_items.append(
            TranslationResponse(
                translation_id=str(doc.get("_id")),
                translated_code=doc.get("translated_code"),
                notes=f"Retrieved translation from {doc.get('source_language')} to {doc.get('target_language')}."
            )
        )
    return response_items
