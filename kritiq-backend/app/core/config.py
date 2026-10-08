# Sayeed domain - App configuration settings loading
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "kritiq"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GITHUB_TOKEN: str = ""
    JWT_SECRET: str = "mock-secret"
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 120
    FRONTEND_URL: str = "http://localhost:5173"
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/auth/github/callback"
    GITHUB_OAUTH_SCOPES: str = "read:user user:email repo"


    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
