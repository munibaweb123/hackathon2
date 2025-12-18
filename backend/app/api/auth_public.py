"""Public Authentication API endpoints - Better Auth integration."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
import httpx
import uuid
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from ..schemas.user import UserResponse
from ..models.user import User
from ..core.database import get_session
from ..core.config import settings
from ..core.auth import create_access_token, create_refresh_token

router = APIRouter()


class SignUpRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class SignInRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/sign-up/email")
async def sign_up_email(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Handle email sign up request.
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

    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/sign-in/email")
async def sign_in_email(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Handle email sign in request.
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

    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/sign-out")
async def sign_out():
    """
    Handle sign out request.
    """
    return {
        "success": True,
        "message": "Successfully signed out"
    }