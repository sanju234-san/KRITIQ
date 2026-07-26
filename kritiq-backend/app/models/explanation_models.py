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
    filename: Optional[str] = Field(
        None,
        description="Optional filename associated with the code snippet (for display/storage)",
        example="main.py"
    )
    file_path: Optional[str] = Field(
        None,
        description="Optional repository file path for MCP project context",
        example="src/auth/login.py"
    )
    repo_owner: Optional[str] = Field(
        None,
        description="Optional GitHub repo owner for MCP project context retrieval",
        example="octocat"
    )
    repo_name: Optional[str] = Field(
        None,
        description="Optional GitHub repo name for MCP project context retrieval",
        example="Hello-World"
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
    explanation_id: Optional[str] = Field(
        None,
        description="The unique database ID of the stored explanation record (populated after save, used for revisit links).",
        example="6a71e355-6671-460d-a02c-7b94b0dfa72d"
    )
    explanation: str = Field(
        ..., 
        description="The detailed natural language explanation of the provided code logic", 
        example="This is a python list comprehension that generates a list of square numbers from 0 to 81..."
    )
    code: Optional[str] = Field(
        None,
        description="The original source code that was explained (populated on GET revisit endpoint for display)."
    )
    language: Optional[str] = Field(
        None,
        description="Programming language of the explained code (populated on GET endpoint)."
    )
    filename: Optional[str] = Field(
        None,
        description="Original filename of the explained code (populated on GET endpoint)."
    )
    file_path: Optional[str] = Field(
        None,
        description="Original repository file path (populated on GET endpoint for reference)."
    )
    repo_owner: Optional[str] = Field(
        None,
        description="GitHub repository owner if the code came from a connected repo (populated on GET endpoint)."
    )
    repo_name: Optional[str] = Field(
        None,
        description="GitHub repository name if the code came from a connected repo (populated on GET endpoint)."
    )
    created_at: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp of when the explanation was generated (populated on GET endpoint)."
    )
