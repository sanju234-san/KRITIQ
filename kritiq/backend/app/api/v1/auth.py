"""
Authentication router — manages GitHub & Google OAuth login, callbacks, logout, and token validation.
"""

from datetime import datetime, timezone
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.services.mongo_repository import mongo_repository

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize Authlib OAuth client
oauth = OAuth()
oauth.register(
    name="github",
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def upsert_user(
    provider: str,
    provider_id: str,
    email: Optional[str],
    name: str,
    avatar_url: str,
) -> dict:
    """Helper to update user's last login or insert a new user in MongoDB users collection."""
    now = datetime.now(timezone.utc)
    
    existing_user = await mongo_repository.db.users.find_one({
        "provider": provider,
        "provider_id": provider_id
    })

    if existing_user:
        update_fields = {
            "name": name,
            "avatar_url": avatar_url,
            "last_login": now,
        }
        if email:
            update_fields["email"] = email
            
        await mongo_repository.db.users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": update_fields}
        )
        # Fetch updated doc
        user = await mongo_repository.db.users.find_one({"_id": existing_user["_id"]})
    else:
        new_user = {
            "provider": provider,
            "provider_id": provider_id,
            "email": email or "",
            "name": name,
            "avatar_url": avatar_url,
            "created_at": now,
            "last_login": now,
        }
        res = await mongo_repository.db.users.insert_one(new_user)
        new_user["_id"] = res.inserted_id
        user = new_user

    return user


# ── GitHub OAuth ─────────────────────────────────────────

@router.get("/github")
async def github_login(request: Request):
    """Redirect to GitHub's OAuth login screen."""
    # Fast path for developer fallback verification
    if settings.GITHUB_CLIENT_ID == "mock_github_client_id":
        user = await upsert_user(
            "github",
            "mock_id_123",
            "mock.user@github.com",
            "Mock GitHub User",
            "https://avatars.githubusercontent.com/u/583231?v=4"
        )
        jwt_token = create_access_token(user_id=user["_id"], email=user["email"])
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?token={jwt_token}")

    redirect_uri = settings.GITHUB_CALLBACK_URL
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request):
    """Exchange authorization code from GitHub for user profile and issue JWT."""
    if settings.GITHUB_CLIENT_ID == "mock_github_client_id":
        user = await upsert_user(
            "github",
            "mock_id_123",
            "mock.user@github.com",
            "Mock GitHub User",
            "https://avatars.githubusercontent.com/u/583231?v=4"
        )
        jwt_token = create_access_token(user_id=user["_id"], email=user["email"])
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?token={jwt_token}")

    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub authentication failed: {str(e)}"
        )

    resp = await oauth.github.get("user", token=token)
    profile = resp.json()

    # Retrieve private email if not returned in public user response
    email = profile.get("email")
    if not email:
        email_resp = await oauth.github.get("user/emails", token=token)
        emails = email_resp.json()
        for e in emails:
            if e.get("primary") or e.get("verified"):
                email = e.get("email")
                break
        if not email and emails:
            email = emails[0].get("email")

    provider_id = str(profile.get("id"))
    name = profile.get("name") or profile.get("login") or "GitHub User"
    avatar_url = profile.get("avatar_url") or ""

    user = await upsert_user("github", provider_id, email, name, avatar_url)
    jwt_token = create_access_token(user_id=user["_id"], email=user["email"])

    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?token={jwt_token}")


# ── Google OAuth ─────────────────────────────────────────

@router.get("/google")
async def google_login(request: Request):
    """Redirect to Google's OAuth login screen."""
    # Fast path for developer fallback verification
    if settings.GOOGLE_CLIENT_ID == "mock_google_client_id":
        user = await upsert_user(
            "google",
            "mock_google_id_123",
            "mock.user@gmail.com",
            "Mock Google User",
            "https://lh3.googleusercontent.com/a/default-user"
        )
        jwt_token = create_access_token(user_id=user["_id"], email=user["email"])
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?token={jwt_token}")

    redirect_uri = settings.GOOGLE_CALLBACK_URL
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request):
    """Exchange authorization code from Google for user profile and issue JWT."""
    if settings.GOOGLE_CLIENT_ID == "mock_google_client_id":
        user = await upsert_user(
            "google",
            "mock_google_id_123",
            "mock.user@gmail.com",
            "Mock Google User",
            "https://lh3.googleusercontent.com/a/default-user"
        )
        jwt_token = create_access_token(user_id=user["_id"], email=user["email"])
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?token={jwt_token}")

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )

    userinfo = token.get("userinfo")
    if not userinfo:
        resp = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
        userinfo = resp.json()

    provider_id = str(userinfo.get("sub"))
    email = userinfo.get("email")
    name = userinfo.get("name") or userinfo.get("given_name") or "Google User"
    avatar_url = userinfo.get("picture") or ""

    user = await upsert_user("google", provider_id, email, name, avatar_url)
    jwt_token = create_access_token(user_id=user["_id"], email=user["email"])

    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?token={jwt_token}")


# ── Profile & Logout ─────────────────────────────────────

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Fetch current authenticated user profile."""
    # Exclude internal ObjectId to avoid JSON serialization issues
    user_profile = {k: v for k, v in current_user.items() if k != "_id"}
    return user_profile


@router.post("/logout")
async def logout(request: Request):
    """Clear session data and complete logout."""
    request.session.clear()
    return {"status": "success", "message": "Logged out successfully"}
