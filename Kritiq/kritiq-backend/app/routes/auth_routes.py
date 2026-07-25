from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user_models import UserRegister, UserLogin, TokenResponse, UserProfileResponse
from app.db.users_repo import users_repo
from app.auth.password_utils import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.auth.dependencies import get_current_user

# Sayeed domain
router = APIRouter()

@router.post(
    "/register", 
    response_model=TokenResponse, 
    status_code=status.HTTP_200_OK,
    summary="Register a new user",
    description="Creates a new user profile with a unique email, hashes the password using bcrypt, stores user data in MongoDB, and issues a JWT token to establish the user session.",
    response_description="Access token details for authentication",
    responses={
        200: {"description": "Registration successful, session access token returned."},
        400: {"description": "Bad Request - Email is already registered in the system."},
        422: {"description": "Validation Error - Password length < 8, or invalid email format."}
    }
)
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

@router.post(
    "/login", 
    response_model=TokenResponse, 
    status_code=status.HTTP_200_OK,
    summary="Authenticate user credentials",
    description="Validates the user's email and password against the MongoDB database and generates a JWT access token if verification succeeds.",
    response_description="Access token details for authentication",
    responses={
        200: {"description": "Login successful, session access token returned."},
        401: {"description": "Unauthorized - Invalid email or password credentials."},
        422: {"description": "Validation Error - Missing required payload fields."}
    }
)
async def login(payload: UserLogin):
    user = await users_repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    token = create_access_token(data={"sub": payload.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get(
    "/profile", 
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current user profile",
    description="Decodes the caller's JWT Bearer token and returns the current user's details (ID, name, email) from database record.",
    response_description="The profile details of the authenticated caller",
    responses={
        200: {"description": "Profile data retrieved successfully."},
        401: {"description": "Unauthorized - Missing, invalid, or expired authentication token."}
    }
)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user.get("_id")),
        "name": current_user.get("name"),
        "email": current_user.get("email")
    }
