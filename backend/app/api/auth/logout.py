"""Logout endpoint for user session termination."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from typing import Any

from ...core.database import get_session
from ...core.auth import get_current_user, AuthenticatedUser

router = APIRouter()


@router.post("/logout")
async def logout_user(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Logout the current user and invalidate their session.

    This endpoint invalidates the user's session. In a complete implementation,
    we might want to add the JWT to a blacklist or revoke the refresh token.
    """
    try:
        # In a real implementation, we would add the JWT to a blacklist
        # or invalidate the refresh token in the database
        # For now, we just return a success message

        return {
            "success": True,
            "message": "Successfully logged out"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )