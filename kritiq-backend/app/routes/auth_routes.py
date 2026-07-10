from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user_models import UserRegister, UserLogin, TokenResponse, UserProfileResponse
from app.db.users_repo import users_repo
from app.auth.password_utils import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.auth.dependencies import get_current_user

# Sayeed domain
router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister):
    existing_user = await users_repo.get_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_pwd = hash_password(payload.password)
    user_data = {
        "name": payload.name,
        "email": payload.email,
        "password": hashed_pwd
    }
    await users_repo.create_user(user_data)
    token = create_access_token(data={"sub": payload.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    user = await users_repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    token = create_access_token(data={"sub": payload.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user.get("_id")),
        "name": current_user.get("name"),
        "email": current_user.get("email")
    }

