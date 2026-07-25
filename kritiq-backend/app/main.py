from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
from app.routes import (
    auth_routes,
    repository_routes,
    review_routes,
    translation_routes,
    explanation_routes,
    history_routes,
    chat_routes
)
from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.rate_limiter import global_limiter

# Sayeed domain - FastAPI App entrypoint
app = FastAPI(
    title="KRITIQ API",
    description="The backend REST API server for KRITIQ, an AI-powered code analysis platform. Supports JWT Authentication, Code Reviews, Code Translations, Code Explanations, and activity history retrieval.",
    version="1.0.0",
    dependencies=[Depends(global_limiter)],
    openapi_tags=[
        {"name": "auth", "description": "User registration, login session tokens, and user profile information."},
        {"name": "reviews", "description": "Submit code files for security, complexity, and styling analysis reviews."},
        {"name": "translations", "description": "Translate source code from one programming language to another."},
        {"name": "explanations", "description": "Retrieve plain English detailed explanations of code block functionality."},
        {"name": "history", "description": "Access paginated lists of past code operations and analysis outcomes."},
        {"name": "repositories", "description": "Manage repository configurations and GitHub connection states."},
        {"name": "chat", "description": "Interactive multi-turn AI assistant chat session."}
    ]
)

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# -----------------------------------------------------------------------------
# CORS middleware MUST be the very first middleware added.
# Starlette wraps in reverse order: add_middleware wraps the *current* app,
# so adding CORSMiddleware now (before routers / custom middlewares) ensures
# it intercepts preflight OPTIONS requests before anything else tries to
# route / validate them.
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    # Enforce 1MB payload body size limit — but NEVER read the body of
    # OPTIONS preflight requests (browsers send empty bodies; reading it
    # could confuse downstream ASGI layers).
    if request.method.upper() == "OPTIONS":
        return await call_next(request)

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > 1 * 1024 * 1024:  # 1MB
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request entity too large. Maximum body size is 1MB."}
                )
        except ValueError:
            pass
    return await call_next(request)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# -----------------------------------------------------------------------------
# Catch-all OPTIONS handler.
# CORSMiddleware normally short-circuits preflight requests, but any
# OPTIONS that slips through (e.g. missing ACRM header, Render edge proxy
# rewriting the request, CORS origin mismatch) should NEVER fall through to
# a POST route handler where Pydantic validates the body and returns 400
# "Field required: body". This route guarantees OPTIONS always returns 204,
# and CORSMiddleware will attach the proper ACAO / ACAM / ACAH headers on
# the way out if the Origin is allow-listed.
# -----------------------------------------------------------------------------
@app.options("/{full_path:path}", include_in_schema=False)
async def options_catch_all(full_path: str):
    return Response(status_code=204)

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(repository_routes.router, prefix="/repositories", tags=["Repositories"])
app.include_router(review_routes.router, prefix="/reviews", tags=["Reviews"])
app.include_router(translation_routes.router, prefix="/translations", tags=["Translations"])
app.include_router(explanation_routes.router, prefix="/explanations", tags=["Explanations"])
app.include_router(history_routes.router, prefix="/history", tags=["History"])
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])

@app.get("/", summary="Kritiq API health check root")
async def root():
    return {"message": "Kritiq API is running."}
