"""Login endpoint for user authentication."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Any
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ...core.database import get_session
from ...core.auth import log_auth_event
from ...services.auth_service import AuthService
from ...schemas.auth import UserLoginRequest, UserLoginResponse

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# Apply rate limiting to login endpoints - max 5 attempts per minute per IP
@router.post("/login", response_model=UserLoginResponse)
@limiter.limit("5/minute")
async def login_user(
    request: Request,  # Need to include request for rate limiting
    login_data: UserLoginRequest,  # Using Pydantic model instead of form for our API
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Authenticate user and return access/refresh tokens.
    """
    try:
        # Use the auth service to authenticate the user via Better Auth
        user, access_token, refresh_token = await AuthService.authenticate_user(login_data, request)

        if not user:
            # Log failed login attempt
            log_auth_event(
                event_type="login_failed",
                email=login_data.email,
                ip_address=get_remote_address(request),
                user_agent=request.headers.get("user-agent"),
                success=False,
                details="Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Log successful login
        log_auth_event(
            event_type="login_success",
            user_id=user.id if user else None,
            email=user.email if user else login_data.email,
            ip_address=get_remote_address(request),
            user_agent=request.headers.get("user-agent"),
            success=True
        )

        # Prepare the response - use data from Better Auth
        if user:
            user_data = {
                "id": user.id,
                "email": user.email,
                "username": None,  # Better Auth doesn't have username in this implementation
                "first_name": None,  # Extract from name if needed
                "last_name": None,   # Extract from name if needed
                "is_verified": user.email_verified is not None,
                "created_at": user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
                "updated_at": user.updated_at.isoformat() if user.updated_at else datetime.utcnow().isoformat(),
            }
        else:
            # Fallback if user object wasn't created locally
            user_data = {
                "id": "",
                "email": login_data.email,
                "username": None,
                "first_name": None,
                "last_name": None,
                "is_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

        return UserLoginResponse(
            success=True,
            user=user_data,
            access_token=access_token,
            refresh_token=refresh_token
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except RateLimitExceeded:
        # This will be handled by the rate limiter's error handler
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


# Alternative login endpoint using OAuth2 form for compatibility with standard tools
# Also apply rate limiting to this endpoint
@router.post("/token")  # This can be used for OAuth2 compatible login
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,  # Need to include request for rate limiting
    form_data: OAuth2PasswordRequestForm = Depends()
    # Removed db_session dependency as it's not needed with new AuthService
):
    """
    OAuth2 compatible login endpoint, gets username and password, returns access and refresh tokens.
    """
    login_data = UserLoginRequest(
        email=form_data.username,  # OAuth2PasswordRequestForm uses 'username' field
        password=form_data.password
    )

    user, access_token, refresh_token = await AuthService.authenticate_user(login_data, request)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Prepare the response - use data from Better Auth
    if user:
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": None,  # Better Auth doesn't have username in this implementation
            "first_name": None,  # Extract from name if needed
            "last_name": None,   # Extract from name if needed
            "is_verified": user.email_verified is not None,
        }
    else:
        # Fallback if user object wasn't created locally
        user_data = {
            "id": "",
            "email": login_data.email,
            "username": None,
            "first_name": None,
            "last_name": None,
            "is_verified": False,
        }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_data
    }