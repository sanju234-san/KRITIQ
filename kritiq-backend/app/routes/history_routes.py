from fastapi import APIRouter, Depends, Query, status
from app.models.history_models import HistoryListResponse, HistoryItem
from app.models.review_models import ReviewResponse
from app.models.translation_models import TranslationResponse
from app.auth.dependencies import get_current_user
from app.db.history_repo import history_repo
from app.db.reviews_repo import reviews_repo
from app.db.translations_repo import translations_repo
from typing import List, Optional

# Sayeed domain
router = APIRouter()

@router.get(
    "/", 
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve paginated activity logs",
    description="Returns a paginated list of all code analysis actions (reviews, translations, explanations) performed by the current user, sorted from newest to oldest.",
    response_description="A list of code activities matching pagination filters",
    responses={
        200: {"description": "History successfully retrieved."},
        401: {"description": "Unauthorized - Missing or invalid JWT session token."}
    }
)
async def get_history(
    limit: int = Query(
        20, 
        ge=1, 
        le=100, 
        description="The maximum number of items to return in the response", 
        examples=[10]
    ),
    skip: int = Query(
        0, 
        ge=0, 
        description="The number of items to offset/skip for pagination", 
        examples=[0]
    ),
    type: Optional[str] = Query(
        None, 
        description="Optional filter for activity types (review, translation, explanation)", 
        examples=["review"]
    ),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user.get("_id"))
    logs = await history_repo.get_history_by_user(user_id, limit=limit, skip=skip, activity_type=type)
    
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

@router.get(
    "/reviews", 
    response_model=List[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve paginated review logs",
    description="Loads a paginated list of historical code reviews submitted by the user, sorted from newest to oldest.",
    response_description="A list of historical reviews",
    responses={
        200: {"description": "Review history successfully retrieved."},
        401: {"description": "Unauthorized - Missing or invalid JWT session token."}
    }
)
async def get_history_reviews(
    limit: int = Query(
        20, 
        ge=1, 
        le=100, 
        description="Maximum number of items to return", 
        examples=[5]
    ),
    skip: int = Query(
        0, 
        ge=0, 
        description="Number of items to offset/skip", 
        examples=[0]
    ),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user.get("_id"))
    reviews = await reviews_repo.get_reviews_by_user(user_id, limit=limit, skip=skip)
    
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

@router.get(
    "/translations", 
    response_model=List[TranslationResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve paginated translation logs",
    description="Loads a paginated list of historical code translations performed by the user, sorted from newest to oldest.",
    response_description="A list of historical translations",
    responses={
        200: {"description": "Translation history successfully retrieved."},
        401: {"description": "Unauthorized - Missing or invalid JWT session token."}
    }
)
async def get_history_translations(
    limit: int = Query(
        20, 
        ge=1, 
        le=100, 
        description="Maximum number of items to return", 
        examples=[5]
    ),
    skip: int = Query(
        0, 
        ge=0, 
        description="Number of items to offset/skip", 
        examples=[0]
    ),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user.get("_id"))
    translations = await translations_repo.get_translations_by_user(user_id, limit=limit, skip=skip)
    
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
