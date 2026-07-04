from fastapi import APIRouter
from app.models.history_models import HistoryResponse
from typing import List

# Sayeed domain
router = APIRouter()

@router.get("/", response_model=List[HistoryResponse])
async def get_history():
    # TODO: Fetch logs from history_repo
    return []
