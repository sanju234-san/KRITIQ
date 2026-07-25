import pytest
from datetime import timedelta
import jwt
from fastapi import HTTPException
from app.auth.jwt_handler import create_access_token, decode_access_token
from app.core.config import settings

def test_jwt_generation_and_decoding():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    assert token is not None
    
    decoded = decode_access_token(token)
    assert decoded["sub"] == "test@example.com"

def test_jwt_expired():
    data = {"sub": "test@example.com"}
    # Create a token that expired 10 minutes ago
    token = create_access_token(data, expires_delta=timedelta(minutes=-10))
    assert decode_access_token(token) is None

def test_jwt_invalid_signature():
    token = jwt.encode({"sub": "test@example.com"}, "wrong_secret_key", algorithm="HS256")
    assert decode_access_token(token) is None

def test_jwt_malformed():
    assert decode_access_token("malformed_token_string") is None
