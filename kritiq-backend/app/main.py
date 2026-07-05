from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    auth_routes,
    repository_routes,
    review_routes,
    translation_routes,
    explanation_routes,
    history_routes
)
from app.core.config import settings

# Sayeed domain - FastAPI App entrypoint
app = FastAPI(title="Kritiq API", version="0.1.0")

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

@app.get("/")
async def root():
    return {"message": "Kritiq API is running."}
