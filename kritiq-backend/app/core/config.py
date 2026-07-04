# Sayeed domain - App configuration settings loading
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "kritiq"
    GEMINI_API_KEY: str = ""
    GITHUB_TOKEN: str = ""
    JWT_SECRET: str = "mock-secret"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
