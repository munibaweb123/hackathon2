"""Registration endpoint for user registration."""

from datetime import datetime
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


@router.post("/register", response_model=UserRegistrationResponse)
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
        # Use the auth service to register the user via Better Auth
        user, access_token = await AuthService.register_user(user_data, request)

        # Log successful registration
        log_auth_event(
            event_type="registration_success",
            user_id=user.id if user else None,
            email=user.email if user else user_data.email,
            ip_address=get_remote_address(request),
            user_agent=request.headers.get("user-agent"),
            success=True
        )

        # Prepare the response - use the user data from Better Auth
        if user:
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                username=None,  # Better Auth doesn't have username in this implementation
                first_name=None,  # Extract from name if needed
                last_name=None,   # Extract from name if needed
                name=user.name,
                is_active=True,  # Better Auth handles account activation
                is_verified=user.email_verified is not None,  # Use email_verified status
                email_verified=user.email_verified is not None,
                image=user.image,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=None  # Not tracked in this implementation
            )
        else:
            # Fallback if user object wasn't created locally
            user_response = UserResponse(
                id="",  # Will be filled by Better Auth
                email=user_data.email,
                username=None,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                name=f"{user_data.first_name or ''} {user_data.last_name or ''}".strip() or user_data.email.split('@')[0],
                is_active=True,
                is_verified=False,
                email_verified=False,
                image=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login_at=None
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