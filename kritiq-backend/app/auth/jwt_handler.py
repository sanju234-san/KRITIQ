# Sayeed domain - JWT Token generation and validation handlers
# pyrefly: ignore [missing-import]
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

JWTError = getattr(jwt, "PyJWTError", Exception)

def create_access_token(data: dict, expires_delta: timedelta = None, minutes: int | None = None):
    to_encode = data.copy()
    if minutes is not None:
        expires_delta = timedelta(minutes=minutes)
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

def decode_token_safe(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


