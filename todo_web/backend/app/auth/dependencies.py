from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict, Any, Optional
from .utils import decode_jwt_token, extract_user_id_from_token, validate_token_for_user
from .middleware import verify_jwt_token
from ..models.user import User  # Assuming there's a User model
from ..models.task import Task  # Assuming there's a Task model


# Initialize security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get the current authenticated user from the JWT token.

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


async def get_current_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Extract just the user ID from the current authenticated user.

    Args:
        current_user: The current authenticated user (from get_current_user dependency)

    Returns:
        User ID string
    """
    return current_user["user_id"]


async def require_authenticated_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require that a user is authenticated, returning their information.

    This is a wrapper around get_current_user that makes the authentication requirement explicit.

    Args:
        current_user: The current authenticated user (from get_current_user dependency)

    Returns:
        Dictionary containing user information
    """
    # The authentication check already happened in get_current_user
    # This function exists to make the authentication requirement explicit in route dependencies
    return current_user


async def verify_user_owns_resource(
    user_id_from_token: str = Depends(get_current_user_id),
    resource_user_id: str = None
) -> bool:
    """
    Verify that the authenticated user owns a specific resource.

    Args:
        user_id_from_token: User ID extracted from JWT token (from get_current_user_id dependency)
        resource_user_id: The user ID associated with the resource being accessed

    Returns:
        True if the user owns the resource, raises HTTPException otherwise

    Raises:
        HTTPException: If the user doesn't own the resource
    """
    if resource_user_id and user_id_from_token != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )

    return True


def get_user_id_from_path_and_token(
    path_user_id: str,
    token_user_id: str = Depends(get_current_user_id)
) -> bool:
    """
    Verify that the user ID in the path matches the user ID in the JWT token.

    Args:
        path_user_id: User ID from the request path parameter
        token_user_id: User ID from the JWT token (from get_current_user_id dependency)

    Returns:
        True if the user IDs match, raises HTTPException otherwise

    Raises:
        HTTPException: If the user IDs don't match
    """
    if path_user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data"
        )

    return True


def require_valid_token_only(
    current_user: Dict[str, Any] = Depends(require_authenticated_user)
) -> bool:
    """
    Simple dependency that just requires a valid token, without returning user info.

    Args:
        current_user: The current authenticated user (from require_authenticated_user dependency)

    Returns:
        True if token is valid
    """
    return True