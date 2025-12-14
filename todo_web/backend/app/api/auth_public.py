"""Public Authentication API endpoints - Better Auth integration."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select

from ..schemas.user import UserResponse
from ..models.user import User
from ..core.database import get_session

router = APIRouter()


@router.post("/sign-up/email")
async def sign_up_email(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Handle email sign up request.

    This endpoint is for compatibility with Better Auth client.
    Actual user creation happens when JWT is decoded in auth middleware.
    """
    # Parse request data
    try:
        data = await request.json()
        email = data.get("email")
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

    # In a real implementation, this would trigger Better Auth sign up
    # For now, we'll just return a success response
    # The actual user creation happens when JWT is decoded in auth middleware
    return {
        "success": True,
        "message": "Sign up initiated - please check your email for verification"
    }


@router.post("/sign-in/email")
async def sign_in_email(
    request: Request,
):
    """
    Handle email sign in request.

    This endpoint is for compatibility with Better Auth client.
    """
    # Parse request data
    try:
        data = await request.json()
        email = data.get("email")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data"
        )

    # In a real implementation, this would trigger Better Auth sign in
    # For now, we'll just return a success response
    return {
        "success": True,
        "message": "Sign in initiated - please check your email for verification"
    }


@router.post("/sign-out")
async def sign_out():
    """
    Handle sign out request.

    This endpoint is for compatibility with Better Auth client.
    """
    return {
        "success": True,
        "message": "Successfully signed out"
    }