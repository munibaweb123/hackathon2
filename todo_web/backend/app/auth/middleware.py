from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .utils import decode_jwt_token, extract_user_id_from_token
from ..core.config import settings
import logging


logger = logging.getLogger(__name__)

# Initialize security scheme for extracting JWT from Authorization header
security = HTTPBearer()


class JWTAuthMiddleware:
    """
    JWT Authentication Middleware for FastAPI
    Verifies JWT tokens in the Authorization header and extracts user information
    """

    def __init__(self):
        self.security = HTTPBearer()
        self.logger = logging.getLogger(__name__)

    async def __call__(self, request: Request) -> dict:
        """
        Process the incoming request and verify JWT token

        Args:
            request: The incoming FastAPI request

        Returns:
            Dictionary containing user information if token is valid

        Raises:
            HTTPException: If token is missing, invalid, or expired
        """
        # Extract credentials from the Authorization header
        credentials: HTTPAuthorizationCredentials = await self.security(request)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authorization credentials provided"
            )

        token = credentials.credentials

        # Decode and verify the JWT token
        payload = decode_jwt_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        # Extract user ID from token
        user_id = extract_user_id_from_token(token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not extract user ID from token"
            )

        # Add user info to request state for use in route handlers
        request.state.user_id = user_id
        request.state.user_info = payload

        return {
            "user_id": user_id,
            "user_info": payload,
            "token_valid": True
        }


# Convenience function to verify JWT token in route dependencies
async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency function to verify JWT token in route handlers

    Args:
        credentials: HTTP authorization credentials from security scheme

    Returns:
        Dictionary containing user information if token is valid

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization credentials provided"
        )

    token = credentials.credentials

    # Decode and verify the JWT token
    payload = decode_jwt_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Extract user ID from token
    user_id = extract_user_id_from_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not extract user ID from token"
        )

    return {
        "user_id": user_id,
        "user_info": payload,
        "token_valid": True
    }


# Function to verify user has access to specific resource
async def verify_user_access(credentials: HTTPAuthorizationCredentials = Depends(security),
                           resource_user_id: str = None) -> dict:
    """
    Verify that the authenticated user has access to a specific resource

    Args:
        credentials: HTTP authorization credentials from security scheme
        resource_user_id: The user ID of the resource being accessed

    Returns:
        Dictionary containing user information if access is authorized

    Raises:
        HTTPException: If token is invalid or user doesn't have access to the resource
    """
    auth_result = await verify_jwt_token(credentials)
    user_id = auth_result["user_id"]

    # If resource_user_id is provided, verify it matches the authenticated user
    if resource_user_id and user_id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )

    return auth_result