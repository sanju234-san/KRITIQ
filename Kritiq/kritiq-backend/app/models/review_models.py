# Sayeed domain - Review request/response schemas
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional

SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "java", "c", "cpp", "csharp", "go", "rust", "ruby", "php"}

class ReviewIssue(BaseModel):
    title: str = Field(
        ..., 
        description="The summary title of the issue found", 
        example="Redundant function definition"
    )
    explanation: str = Field(
        ..., 
        description="Detailed explanation of the code smell or issue", 
        example="The function duplicate_method is defined twice in the same scope..."
    )
    suggested_fix: Optional[str] = Field(
        None, 
        description="Suggested replacement code block or instructions to resolve the issue", 
        example="Remove the second definition of duplicate_method."
    )
    severity: Optional[str] = Field(
        None, 
        description="Severity level of the issue (high, medium, low)", 
        example="medium"
    )
    line: Optional[int] = Field(
        None, 
        description="The line number where the issue was detected", 
        example=12
    )

class ReviewRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    code: str = Field(
        ..., 
        min_length=1, 
        max_length=100000, 
        description="The raw code snippet to review (cannot be empty)", 
        example="def double(x): return x * 2"
    )
    language: Optional[str] = Field(
        None, 
        description="The programming language of the code (must be supported)", 
        example="python"
    )
    repo_url: Optional[str] = Field(
        None, 
        description="Optional Git repository URL related to the code snippet", 
        example="https://github.com/example/repo"
    )
    filename: Optional[str] = Field(
        None, 
        description="Optional filename associated with the code snippet", 
        example="main.py"
    )

    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Code cannot be empty or only whitespace")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            lang = v.lower()
            if lang not in SUPPORTED_LANGUAGES:
                raise ValueError(f"Unsupported language: {v}. Supported: {sorted(list(SUPPORTED_LANGUAGES))}")
            return lang
        return v

class ReviewResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    review_id: str = Field(
        ..., 
        description="The unique database ID of the review result", 
        example="6a71e355-6671-460d-a02c-7b94b0dfa72d"
    )
    summary: str = Field(
        ..., 
        description="High-level summarization of the review result findings", 
        example="Clean code overall. Found 1 code smell related to naming conventions."
    )
    issues: List[ReviewIssue] = Field(
        ..., 
        description="List of specific code issues identified during the review"
    )
    raw_output: Optional[str] = Field(
        None, 
        description="The raw unparsed output of the AI reviewer service"
    )
