"""
KRITIQ API — FastAPI application entry-point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.webhooks import router as webhook_router
from app.api.v1.reports import router as reports_router
from app.api.v1.auth import router as auth_router
from app.services.mongo_repository import mongo_repository

# ── Lifespan (startup / shutdown) ────────────────────────


def get_db():
    """Return the active MongoDB database handle."""
    return mongo_repository.db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect to MongoDB on startup; close on shutdown."""
    mongo_repository.connect()
    # Force a connection check so we fail fast on bad credentials
    await mongo_repository.ping()
    yield
    mongo_repository.close()


# ── App ──────────────────────────────────────────────────

app = FastAPI(
    title="KRITIQ API",
    description="Autonomous code-review & fixer agent backend",
    version="0.1.0",
    lifespan=lifespan,
)

# ── Middleware ───────────────────────────────────────────

from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────

app.include_router(webhook_router)
app.include_router(reports_router)
app.include_router(auth_router)



# ── Static Files Mount ───────────────────────────────────
import os
from fastapi.staticfiles import StaticFiles

os.makedirs("temp", exist_ok=True)
app.mount("/temp", StaticFiles(directory="temp"), name="temp")


# ── Root health endpoint ─────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    """Return MongoDB connectivity status."""
    try:
        await mongo_repository.ping()
        return {"status": "healthy", "mongo": "connected"}
    except Exception as exc:
        return {"status": "degraded", "mongo": str(exc)}


# ── Playground Key-Testing Endpoint ──────────────────────

@app.get("/playground/test-keys", tags=["Playground"])
async def test_keys():
    """Validate all API keys and environment configurations."""
    import httpx
    
    # 1. Test MongoDB
    try:
        await mongo_repository.ping()
        mongo_status = {"status": "OK", "error": None}
    except Exception as e:
        mongo_status = {"status": "ERROR", "error": str(e)}

    # 2. Test Groq API Key
    try:
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=6.0
            )
            if response.status_code == 200:
                groq_status = {"status": "OK", "error": None}
            else:
                try:
                    err_msg = response.json().get("error", {}).get("message", response.text)
                except Exception:
                    err_msg = response.text
                groq_status = {"status": "ERROR", "error": f"HTTP {response.status_code}: {err_msg}"}
    except Exception as e:
        groq_status = {"status": "ERROR", "error": str(e)}

    # 3. Test GitHub Token
    try:
        headers = {
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=6.0
            )
            if response.status_code == 200:
                user_login = response.json().get("login")
                github_status = {"status": "OK", "username": user_login, "error": None}
            else:
                try:
                    err_msg = response.json().get("message", response.text)
                except Exception:
                    err_msg = response.text
                github_status = {"status": "ERROR", "error": f"HTTP {response.status_code}: {err_msg}"}
    except Exception as e:
        github_status = {"status": "ERROR", "error": str(e)}

    # 4. Check GitHub OAuth Configuration
    github_oauth = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "is_configured": settings.GITHUB_CLIENT_ID not in ["your_github_client_id", "mock_github_client_id", "", None],
        "has_secret": settings.GITHUB_CLIENT_SECRET not in ["your_github_client_secret", "mock_github_client_secret", "", None],
        "callback_url": settings.GITHUB_CALLBACK_URL
    }

    # 5. Check Google OAuth Configuration
    google_oauth = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "is_configured": settings.GOOGLE_CLIENT_ID not in ["your_google_client_id", "mock_google_client_id", "", None],
        "has_secret": settings.GOOGLE_CLIENT_SECRET not in ["your_google_client_secret", "mock_google_client_secret", "", None],
        "callback_url": settings.GOOGLE_CALLBACK_URL
    }

    # 6. Check JWT Security Configuration
    jwt_config = {
        "is_configured": settings.JWT_SECRET_KEY not in ["your_super_secret_key_here", "", None],
        "length_ok": len(settings.JWT_SECRET_KEY) >= 32 if settings.JWT_SECRET_KEY else False
    }

    return {
        "mongodb": mongo_status,
        "groq": groq_status,
        "github_token": github_status,
        "github_oauth": github_oauth,
        "google_oauth": google_oauth,
        "jwt": jwt_config
    }

