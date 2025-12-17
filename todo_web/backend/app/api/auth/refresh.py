"""Refresh token endpoint for obtaining new access tokens."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Any

from ...core.database import get_session
from ...core.auth import create_access_token, create_refresh_token
from ...models.user import User
from ...schemas.auth import TokenRefreshRequest, TokenResponse

router = APIRouter()


@router.post("", response_model=TokenResponse)
async def refresh_access_token(
    token_data: TokenRefreshRequest,
    db_session: Session = Depends(get_session)
) -> Any:
    """
    Refresh an access token using a refresh token.

    In a complete implementation, we would validate that the refresh token
    is valid and hasn't been revoked. For this implementation, we'll assume
    the refresh token is valid and belongs to the user.
    """
    try:
        # In a real implementation, we would check if the refresh token is valid
        # and hasn't been revoked in the database. For now, we'll decode the token
        # to get the user information and issue new tokens.

        from ...core.auth import verify_token
        payload = verify_token(token_data.refresh_token)

        if not payload or "type" not in payload or payload["type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database to ensure they still exist and are active
        user = db_session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists or is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        new_access_token_data = {
            "user_id": user.id,
            "email": user.email
        }

        new_refresh_token_data = {
            "user_id": user.id,
            "email": user.email
        }

        new_access_token = create_access_token(
            data=new_access_token_data,
            expires_delta=timedelta(hours=1)
        )

        new_refresh_token = create_refresh_token(
            data=new_refresh_token_data,
            expires_delta=timedelta(days=7)
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )