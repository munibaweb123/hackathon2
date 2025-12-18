"""Authentication API endpoints - Better Auth cookie-based integration."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.auth import get_current_user, AuthenticatedUser
from ..core.database import get_session
from ..schemas.user import UserResponse
from ..models.user import User

router = APIRouter()


@router.get("/get-session")
async def get_session_endpoint(
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserResponse:
    """
    Get current user session information from cookie.

    This endpoint validates the Better Auth session cookie and returns user info.

    Returns:
        UserResponse: Current user information
    """
    # Get the full user from the database to get all required fields
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)