"""Me endpoint to get current user information."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Any

from ...core.database import get_session
from ...core.auth import get_current_user, AuthenticatedUser
from ...models.user import User
from ...schemas.auth import UserProfileResponse

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_info(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Get information about the currently authenticated user.
    """
    try:
        # Fetch the full user record from the database to get all fields
        user = db_session.get(User, current_user.id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Return user information
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user information: {str(e)}"
        )