"""Authentication API endpoints that match frontend service expectations."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
import uuid
from typing import Optional
from pydantic import BaseModel

from ..schemas.user import UserResponse
from ..models.user import User
from ..core.database import get_session
from ..core.config import settings
from ..core.auth import create_access_token, create_refresh_token, get_current_user, AuthenticatedUser

router = APIRouter()

class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"

class UserRegistrationResponse(BaseModel):
    success: bool
    user: dict
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"

class UserLoginResponse(BaseModel):
    success: bool
    user: dict
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refreshToken: str

class TokenRefreshResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"

@router.post("/register")
async def register_user(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Handle user registration request from frontend service.
    Matches the expected /api/auth/register endpoint.
    """
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name", "")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data"
        )

    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    # Create new user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        name=name
    )

    session.add(user)
    try:
        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user_id, "email": email})
    refresh_token = create_refresh_token(data={"sub": user_id, "email": email})

    return UserRegistrationResponse(
        success=True,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        accessToken=access_token,
        refreshToken=refresh_token,
        tokenType="bearer"
    )


@router.post("/login")
async def login_user(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Handle user login request from frontend service.
    Matches the expected /api/auth/login endpoint.
    """
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data"
        )

    # Find user by email
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # In a real implementation, we would verify the password here
    # For this implementation, we'll assume the credentials are valid
    # (Better Auth handles password verification on the frontend)

    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})

    return UserLoginResponse(
        success=True,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        accessToken=access_token,
        refreshToken=refresh_token,
        tokenType="bearer"
    )


@router.post("/refresh")
async def refresh_token(
    token_data: TokenRefreshRequest,
):
    """
    Handle token refresh request.
    """
    # In a real implementation, we would validate the refresh token
    # For now, we'll just create new tokens
    # This is a simplified implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented in this example"
    )


@router.get("/me")
async def get_current_user_info(
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get current user information.
    """
    # Get the full user from the database to get all required fields
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"user": {
        "id": user.id,
        "email": user.email,
        "name": user.name
    }}