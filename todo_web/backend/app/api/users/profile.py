"""User profile endpoints for managing user information."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Any

from ...core.database import get_session
from ...core.auth import get_current_user, AuthenticatedUser
from ...services.auth_service import AuthService
from ...schemas.auth import UserProfileUpdateRequest, UserProfileResponse

router = APIRouter()


@router.put("", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Update user profile information.
    """
    try:
        # Prepare profile data for update
        profile_dict = profile_data.model_dump(exclude_unset=True)

        # Use the auth service to update the user profile
        updated_user = AuthService.update_user_profile(current_user.id, profile_dict, db_session)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Return updated user information
        return UserProfileResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )