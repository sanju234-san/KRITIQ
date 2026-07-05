from fastapi import APIRouter
from app.models.review_models import ReviewRequest, ReviewResponse

# Sayeed domain (Integrates with Sanjeevni's review_service)
router = APIRouter()

@router.post("/", response_model=ReviewResponse)
async def submit_review(payload: ReviewRequest):
    # TODO: Call review_service from ai_agent
    return {
        "review_id": "mock-rev-id",
        "status": "completed",
        "summary": "Mock review summary.",
        "issues": []
    }

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str):
    # TODO: Fetch review from reviews_repo
    return {
        "review_id": review_id,
        "status": "completed",
        "summary": "Mock review summary.",
        "issues": []
    }
