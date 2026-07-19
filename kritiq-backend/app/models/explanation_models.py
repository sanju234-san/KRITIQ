# Sayeed domain - Explanation request/response schemas
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional

SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "java", "c", "cpp", "csharp", "go", "rust", "ruby", "php"}

class ExplanationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    code: str = Field(
        ..., 
        min_length=1, 
        max_length=100000, 
        description="The raw code snippet to be explained (cannot be empty)", 
        example="[x**2 for x in range(10)]"
    )
    language: str = Field(
        "python", 
        description="The programming language of the code (must be supported)", 
        example="python"
    )

    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Code cannot be empty or only whitespace")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        lang = v.lower()
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {v}. Supported: {sorted(list(SUPPORTED_LANGUAGES))}")
        return lang

class ExplanationResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    explanation: str = Field(
        ..., 
        description="The detailed natural language explanation of the provided code logic", 
        example="This is a python list comprehension that generates a list of square numbers from 0 to 81..."
    )
