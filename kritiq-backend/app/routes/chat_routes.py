from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from app.auth.dependencies import get_current_user
from ai_agent.chat_service import chat_turn
import anyio

router = APIRouter()

class ChatRequest(BaseModel):
    user_message: str
    history: Optional[List[dict]] = []

@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Interactive AI Chat turn"
)
async def chat_endpoint(payload: ChatRequest, current_user: dict = Depends(get_current_user)):
    response, updated_history = await anyio.to_thread.run_sync(
        chat_turn, payload.user_message, payload.history
    )
    return {"response": response, "history": updated_history}
