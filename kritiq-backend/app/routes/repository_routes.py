from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import re
import requests
import base64

from app.auth.dependencies import get_current_user
from app.db.repositories_repo import repositories_repo
from repo_integration.github_api import list_repo_files, HEADERS, GITHUB_API_BASE

# Sayeed domain
router = APIRouter()

class RepositoryConnectRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    repo_url: str = Field(
        ...,
        description="The GitHub repository URL, e.g. https://github.com/owner/repo",
        example="https://github.com/octocat/Hello-World"
    )

class RepositoryResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    id: str = Field(
        ...,
        description="The unique database ID of the connected repository record",
        example="6a71e355-6671-460d-a02c-7b94b0dfa72d"
    )
    user_id: str = Field(
        ...,
        description="The user ID of the repository owner",
        example="1a21e355-6671-460d-a02c-7b94b0dfa72d"
    )
    repo_url: str = Field(
        ...,
        description="The fully connected repository URL",
        example="https://github.com/octocat/Hello-World"
    )
    owner: str = Field(
        ...,
        description="The GitHub owner/organization name parsed from URL",
        example="octocat"
    )
    name: str = Field(
        ...,
        description="The GitHub repository name parsed from URL",
        example="Hello-World"
    )
    created_at: str = Field(
        ...,
        description="ISO 8601 timestamp of when the repository was connected",
        example="2026-07-25T11:19:04Z"
    )


def parse_github_url(url: str) -> tuple[str, str]:
    cleaned = url.strip()
    
    ssh_match = re.match(r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$", cleaned)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2)
        
    url_no_proto = re.sub(r"^https?://", "", cleaned)
    
    web_match = re.match(r"^(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/)?$", url_no_proto)
    if web_match:
        return web_match.group(1), web_match.group(2)
        
    simple_match = re.match(r"^([^/]+)/([^/]+?)(?:\.git)?(?:/)?$", url_no_proto)
    if simple_match:
        return simple_match.group(1), simple_match.group(2)
        
    raise ValueError("Invalid GitHub repository URL format")


def fetch_all_repo_files_recursive(owner: str, name: str) -> list[str]:
    """
    Recursively lists all real files inside a repository (including subdirectories like client/ and server/)
    using the GitHub Git Trees API.
    """
    branch = "main"
    try:
        r = requests.get(f"{GITHUB_API_BASE}/repos/{owner}/{name}", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            branch = r.json().get("default_branch", "main")
    except Exception:
        pass

    tree_url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/git/trees/{branch}?recursive=1"
    try:
        resp = requests.get(tree_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            tree = data.get("tree", [])
            # Filter type == 'blob' (files only, excluding directory entries)
            file_paths = [item["path"] for item in tree if item.get("type") == "blob"]
            if file_paths:
                return file_paths
    except Exception as e:
        print("Git Trees API recursive fetch failed:", e)

    # Fallback to root contents list
    return list_repo_files(owner, name)


@router.post(
    "/connect",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Connect a GitHub repository",
    description="Connects a user's GitHub repository, validates its access/existence via the GitHub REST API, and stores it in MongoDB."
)
async def connect_repository(payload: RepositoryConnectRequest, current_user: dict = Depends(get_current_user)):
    repo_url = payload.repo_url
    
    try:
        owner, repo = parse_github_url(repo_url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    files = list_repo_files(owner, repo)
    if len(files) == 1 and files[0].startswith("Error:"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=files[0]
        )
        
    repo_document = {
        "user_id": str(current_user["_id"]),
        "repo_url": repo_url,
        "owner": owner,
        "name": repo
    }
    
    stored_repo = await repositories_repo.add_repository(repo_document)
    
    return {
        "id": stored_repo["_id"],
        "user_id": stored_repo["user_id"],
        "repo_url": stored_repo["repo_url"],
        "owner": stored_repo["owner"],
        "name": stored_repo["name"],
        "created_at": stored_repo["created_at"]
    }


@router.get(
    "/",
    response_model=List[RepositoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List connected repositories"
)
async def list_repositories(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    repos = await repositories_repo.get_repositories_by_user(user_id)
    
    response_list = []
    for repo in repos:
        response_list.append({
            "id": repo["_id"],
            "user_id": repo["user_id"],
            "repo_url": repo["repo_url"],
            "owner": repo["owner"],
            "name": repo["name"],
            "created_at": repo["created_at"]
        })
        
    return response_list


@router.get(
    "/{owner}/{name}/files",
    status_code=status.HTTP_200_OK,
    summary="List all files inside a connected repository recursively"
)
async def get_repository_files(owner: str, name: str, path: str = "", current_user: dict = Depends(get_current_user)):
    files = fetch_all_repo_files_recursive(owner, name)
    if len(files) == 1 and files[0].startswith("Error:"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=files[0]
        )
    return {"owner": owner, "name": name, "files": files}


@router.get(
    "/{owner}/{name}/file-content",
    status_code=status.HTTP_200_OK,
    summary="Fetch raw file content from a connected repository"
)
async def get_repository_file_content(owner: str, name: str, path: str, current_user: dict = Depends(get_current_user)):
    # Try fetching raw file from main and master branches
    for branch in ["main", "master"]:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{name}/{branch}/{path}"
        resp = requests.get(raw_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return {"owner": owner, "name": name, "path": path, "content": resp.text}
            
    # Fallback to GitHub Contents API
    contents_url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/contents/{path}"
    resp = requests.get(contents_url, headers=HEADERS, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, dict) and data.get("encoding") == "base64":
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return {"owner": owner, "name": name, "path": path, "content": content}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Unable to fetch file content for '{path}'."
    )
