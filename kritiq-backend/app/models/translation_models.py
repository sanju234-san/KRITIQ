# Sayeed domain - Translation request/response schemas
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional

SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "java", "c", "cpp", "csharp", "go", "rust", "ruby", "php"}

class TranslationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    source_code: str = Field(
        ..., 
        min_length=1, 
        max_length=100000, 
        description="The source code to be translated (cannot be empty)", 
        example="print('hello')"
    )
    source_language: str = Field(
        ..., 
        description="The language of the source code (must be supported)", 
        example="python"
    )
    target_language: str = Field(
        ..., 
        description="The target language to translate the code into (must be supported and different from source)", 
        example="java"
    )

    @field_validator("source_code")
    @classmethod
    def validate_source_code_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Source code cannot be empty or only whitespace")
        return v

    @field_validator("source_language", "target_language")
    @classmethod
    def validate_languages(cls, v: str) -> str:
        lang = v.lower()
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {v}. Supported: {sorted(list(SUPPORTED_LANGUAGES))}")
        return lang

    @model_validator(mode="after")
    def prevent_same_languages(self) -> "TranslationRequest":
        src = self.source_language.lower()
        tgt = self.target_language.lower()
        if src == tgt:
            raise ValueError("Source and target languages cannot be identical")
        return self

class TranslationResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    translation_id: str = Field(
        ..., 
        description="The unique database ID of the translation result", 
        example="df61e389-9831-4e0d-a02c-7b94b0dfa72d"
    )
    translated_code: str = Field(
        ..., 
        description="The target language translated code block returned by the service", 
        example="System.out.println(\"hello\");"
    )
    notes: Optional[str] = Field(
        None, 
        description="Optional execution notes or contextual recommendations", 
        example="Successfully translated from python to java."
    )
