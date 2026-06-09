"""
Security utilities — JWT token generation and current user validation dependency.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from bson import ObjectId

from app.core.config import settings
from app.services.mongo_repository import mongo_repository

# Standard scheme that reads the Authorization: Bearer <token> header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def create_access_token(user_id: str, email: Optional[str] = None) -> str:
    """Generate a signed JWT token valid for 7 days."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency to extract and validate the JWT token.
    Returns the user document from the MongoDB 'users' collection.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Query user database
    query_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
    user = await mongo_repository.db.users.find_one({"_id": query_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Normalize _id to id string for easier JSON serialization in routes
    user["id"] = str(user["_id"])
    return user
