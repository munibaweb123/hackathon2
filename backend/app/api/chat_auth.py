"""Authentication middleware for chat endpoints in AI Chatbot feature."""

from fastapi import HTTPException, Request
from app.auth.dependencies import get_current_user
from app.models.user import User
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware


class ChatAuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware specifically for chat endpoints."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[any]]
    ):
        """
        Process authentication for chat endpoints.

        Args:
            request: The incoming request
            call_next: Next middleware in the chain

        Returns:
            Processed response
        """
        # Check if this is a chat endpoint
        if request.url.path.startswith("/api/") and "chat" in request.url.path:
            # For now, rely on the existing authentication dependency
            # In a real implementation, this would verify JWT tokens, session cookies, etc.
            pass

        response = await call_next(request)
        return response


def verify_chat_access(current_user: User, requested_user_id: str):
    """
    Verify that the authenticated user has access to chat with the requested user ID.

    Args:
        current_user: The authenticated user
        requested_user_id: The user ID being requested

    Raises:
        HTTPException: If the user doesn't have access
    """
    if current_user.id != requested_user_id:
        raise HTTPException(
            status_code=403,
            detail=f"User {current_user.id} does not have access to chat for user {requested_user_id}"
        )


def validate_jwt_token(token: str) -> dict:
    """
    Validate JWT token for chat authentication.

    Args:
        token: JWT token to validate

    Returns:
        Decoded token claims if valid

    Raises:
        HTTPException: If token is invalid
    """
    # This would integrate with the existing Better Auth JWT validation
    # For now, we'll return a placeholder implementation
    if not token or len(token) < 10:  # Basic validation
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )

    # In a real implementation, this would decode and validate the JWT
    # using the Better Auth JWKS endpoint
    return {"user_id": "temp_user", "valid": True}