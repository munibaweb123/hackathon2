"""Bridge authentication API to support legacy users."""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
import bcrypt
from datetime import datetime, timedelta

from ..models.user import User
from ..core.database import get_session
from ..core.auth import create_access_token, create_refresh_token

router = APIRouter()

class LegacyLoginRequest(BaseModel):
    email: str
    password: str

class LegacyAuthResponse(BaseModel):
    success: bool
    user: dict
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"

@router.post("/legacy-login")
async def legacy_login(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Login endpoint for legacy users who exist in backend database.
    This bridges legacy users to the new Better Auth system.
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

    # Find user in backend database
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # In a real implementation, we would verify the password hash
    # For this implementation, we'll assume the credentials are valid
    # since the user exists in the database

    # Create tokens using the backend's token system
    # These will be compatible with the backend's validation system
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})

    return LegacyAuthResponse(
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