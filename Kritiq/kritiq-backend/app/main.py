from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import (
    auth_routes,
    repository_routes,
    review_routes,
    translation_routes,
    explanation_routes,
    history_routes
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
        {"name": "repositories", "description": "Manage repository configurations and GitHub connection states."}
    ]
)

register_error_handlers(app)

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    # Enforce 1MB payload body size limit
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
    response = await call_next(request)
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(repository_routes.router, prefix="/repositories", tags=["Repositories"])
app.include_router(review_routes.router, prefix="/reviews", tags=["Reviews"])
app.include_router(translation_routes.router, prefix="/translations", tags=["Translations"])
app.include_router(explanation_routes.router, prefix="/explanations", tags=["Explanations"])
app.include_router(history_routes.router, prefix="/history", tags=["History"])

@app.get("/", summary="Kritiq API health check root")
async def root():
    return {"message": "Kritiq API is running."}

