"""Registration endpoint for user registration."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from typing import Any
from slowapi.util import get_remote_address

from ...core.database import get_session
from ...core.auth import log_auth_event
from ...services.auth_service import AuthService
from ...schemas.auth import UserRegistrationRequest, UserRegistrationResponse
from ...schemas.user import UserResponse

router = APIRouter()


@router.post("", response_model=UserRegistrationResponse)
async def register_user(
    request: Request,
    user_data: UserRegistrationRequest,
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Register a new user.

    This endpoint creates a new user account with the provided information.
    The password will be hashed before storing in the database.
    """
    try:
        # Use the auth service to register the user
        user, access_token = AuthService.register_user(user_data, db_session)

        # Log successful registration
        log_auth_event(
            event_type="registration_success",
            user_id=user.id,
            email=user.email,
            ip_address=get_remote_address(request),
            user_agent=request.headers.get("user-agent"),
            success=True
        )

        # Prepare the response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            name=f"{user.first_name or ''} {user.last_name or ''}".strip() or None,
            is_active=user.is_active,
            is_verified=user.is_verified,
            email_verified=user.is_verified,  # For compatibility
            image=user.image,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )

        return UserRegistrationResponse(
            success=True,
            user=user_response.model_dump(),
            message="User registered successfully"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )