# Sayeed domain - User request/response schemas
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegister(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="The display name of the user", 
        example="Sayeed Ahmed"
    )
    email: EmailStr = Field(
        ..., 
        description="The email address of the user (must be a valid format and unique)", 
        example="sayeed@example.com"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=64, 
        description="Secure password for the user (minimum length of 8 characters)", 
        example="securepwd123"
    )

class UserLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr = Field(
        ..., 
        description="Registered email address of the user", 
        example="sayeed@example.com"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=64, 
        description="User password", 
        example="securepwd123"
    )

class TokenResponse(BaseModel):
    access_token: str = Field(
        ..., 
        description="The JWT access token used to authenticate requests", 
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: str = Field(
        ..., 
        description="The token protocol type (typically Bearer)", 
        example="bearer"
    )

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    id: str = Field(
        ..., 
        description="The unique database ID of the user", 
        example="507f1f77bcf86cd799439011"
    )
    name: str = Field(
        ..., 
        description="Display name of the user", 
        example="Sayeed Ahmed"
    )
    email: EmailStr = Field(
        ..., 
        description="The registered email of the user", 
        example="sayeed@example.com"
    )
