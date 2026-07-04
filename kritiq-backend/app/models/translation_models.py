# Sayeed domain - Translation request/response schemas
from pydantic import BaseModel
from typing import Optional

class TranslationRequest(BaseModel):
    source_language: str
    target_language: str
    source: str  # 'repository' or 'upload'
    file_name: str
    code_content: Optional[str] = None

class TranslationResponse(BaseModel):
    translation_id: str
    status: str
    translated_code: str
