"""
KRITIQ — Application settings loaded from environment / .env file.

Uses python-dotenv as the primary loader so that env vars are available
to any module, not only those going through pydantic-settings.
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load .env from the backend/ directory (two levels up from this file)
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)


class Settings(BaseSettings):
    """Central configuration sourced from environment variables."""

    # ── LLM ──────────────────────────────────────────────
    GROQ_API_KEY: str = Field(..., description="Groq cloud API key")

    # ── GitHub ───────────────────────────────────────────
    GITHUB_TOKEN: str = Field(..., description="GitHub PAT for API access")
    GITHUB_WEBHOOK_SECRET: str = Field(
        ..., description="Secret used to verify incoming webhook signatures"
    )

    # ── MongoDB ──────────────────────────────────────────
    MONGODB_URI: str = Field(..., description="MongoDB Atlas connection string")
    MONGODB_DB_NAME: str = Field(
        default="kritiq", description="Mongo database name"
    )

    # ── OAuth ────────────────────────────────────────────
    GITHUB_CLIENT_ID: str = Field(
        default="mock_github_client_id", description="GitHub OAuth App Client ID"
    )
    GITHUB_CLIENT_SECRET: str = Field(
        default="mock_github_client_secret", description="GitHub OAuth App Client Secret"
    )
    GITHUB_CALLBACK_URL: str = Field(
        default="http://localhost:8000/auth/github/callback", description="GitHub Callback URL"
    )
    GOOGLE_CLIENT_ID: str = Field(
        default="mock_google_client_id", description="Google OAuth Client ID"
    )
    GOOGLE_CLIENT_SECRET: str = Field(
        default="mock_google_client_secret", description="Google OAuth Client Secret"
    )
    GOOGLE_CALLBACK_URL: str = Field(
        default="http://localhost:8000/auth/google/callback", description="Google Callback URL"
    )

    # ── JWT & Security ───────────────────────────────────
    JWT_SECRET_KEY: str = Field(
        default="your_super_secret_key_here", description="Secret key for encoding JWTs"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256", description="Algorithm used to sign JWTs"
    )
    JWT_EXPIRE_DAYS: int = Field(
        default=7, description="Number of days before JWT expires"
    )

    # ── App ──────────────────────────────────────────────
    APP_ENV: str = Field(
        default="development", description="development | staging | production"
    )
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173",
        description="Comma-separated allowed origins for CORS",
    )
    FRONTEND_URL: str = Field(
        default="http://localhost:5173",
        description="Frontend application URL for redirects",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    # ── Helpers ──────────────────────────────────────────
    @property
    def cors_origin_list(self) -> list[str]:
        """Return CORS_ORIGINS as a list split on commas."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]

