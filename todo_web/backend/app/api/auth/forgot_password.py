"""Forgot password endpoint for initiating password reset."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session
from typing import Any

from ...core.database import get_session
from ...services.auth_service import AuthService
from ...schemas.auth import PasswordResetRequest, PasswordResetResponse

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/forgot-password", response_model=PasswordResetResponse)
@limiter.limit("3/hour")
async def forgot_password(
    request: Request,
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Initiate a password reset by sending a reset email to the user.

    In a real implementation, this would send an email with a reset link.
    For this implementation, we'll just trigger the token creation.
    """
    try:
        # Create password reset token using the auth service
        success = AuthService.create_password_reset_token(reset_request.email, db_session)

        if success:
            # In a real implementation, we would send an email here with background_tasks
            # background_tasks.add_task(send_password_reset_email, reset_request.email, reset_token)

            return PasswordResetResponse(
                success=True,
                message="If an account exists with this email, a reset link has been sent"
            )
        else:
            # For security, we don't reveal if the email exists or not
            return PasswordResetResponse(
                success=True,
                message="If an account exists with this email, a reset link has been sent"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset request failed: {str(e)}"
        )