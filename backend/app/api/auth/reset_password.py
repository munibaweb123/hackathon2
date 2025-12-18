"""Reset password endpoint for confirming password reset."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Any

from ...core.database import get_session
from ...services.auth_service import AuthService
from ...schemas.auth import PasswordResetConfirmRequest, PasswordResetResponse

router = APIRouter()


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    reset_data: PasswordResetConfirmRequest,
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Confirm password reset using the provided token and new password.
    """
    try:
        # Use the auth service to reset the user's password
        success = AuthService.reset_user_password(reset_data.token, reset_data.new_password, db_session)

        if success:
            return PasswordResetResponse(
                success=True,
                message="Password has been reset successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )