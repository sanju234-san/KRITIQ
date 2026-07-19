from fastapi import APIRouter, status
from typing import List

# Sayeed domain
router = APIRouter()

@router.post(
    "/connect",
    status_code=status.HTTP_200_OK,
    summary="Connect a GitHub repository",
    description="Mock placeholder endpoint representing integration to connect a user's GitHub repository for monitoring.",
    responses={
        200: {"description": "Repository connection state established."}
    }
)
async def connect_repository(repo_url: str):
    # TODO: Connect GitHub repository
    return {"status": "connected", "repository": repo_url}

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="List connected repositories",
    description="Mock placeholder endpoint to retrieve a list of all currently connected repositories.",
    responses={
        200: {"description": "Repositories retrieved successfully."}
    }
)
async def list_repositories():
    # TODO: List repositories
    return []
