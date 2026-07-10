# Sayeed domain - Translation request/response schemas
from pydantic import BaseModel
from typing import Optional

class TranslationRequest(BaseModel):
    source_code: str
    source_language: str
    target_language: str

class TranslationResponse(BaseModel):
    translation_id: str
    translated_code: str
    notes: Optional[str] = None
