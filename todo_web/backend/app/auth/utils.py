from datetime import datetime, timezone
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, status
import logging
from ..core.config import settings


logger = logging.getLogger(__name__)


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token using the shared secret.

    Args:
        token: The JWT token string to decode

    Returns:
        Decoded token payload as dictionary, or None if invalid
    """
    try:
        # Decode the token using the shared secret
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        logger.info(f"Successfully decoded JWT token for user: {payload.get('sub', 'unknown')}")
        return payload
    except PyJWTError as e:
        # Token is invalid, expired, or tampered with
        logger.warning(f"JWT token verification failed: {str(e)}")
        return None
    except Exception as e:
        # Other unexpected errors during decoding
        logger.error(f"Unexpected error during JWT token decoding: {str(e)}")
        return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract the user ID from a JWT token.

    Args:
        token: The JWT token string

    Returns:
        User ID string if found and valid, None otherwise
    """
    payload = decode_jwt_token(token)
    if payload:
        # Better Auth typically stores user ID in 'sub' (subject) field
        # but could also be in 'userId' or similar - check common fields
        return payload.get('sub') or payload.get('userId') or payload.get('id')
    return None


def is_token_expired(payload: Dict[str, Any]) -> bool:
    """
    Check if a token payload is expired based on exp field.

    Args:
        payload: The decoded token payload

    Returns:
        True if token is expired, False otherwise
    """
    if 'exp' in payload:
        exp_timestamp = payload['exp']
        current_timestamp = datetime.now(timezone.utc).timestamp()
        return current_timestamp > exp_timestamp
    return False


def validate_token_for_user(token: str, expected_user_id: str) -> bool:
    """
    Validate that a token belongs to the expected user.

    Args:
        token: The JWT token string
        expected_user_id: The user ID that should match the token

    Returns:
        True if token is valid and belongs to expected user, False otherwise
    """
    token_user_id = extract_user_id_from_token(token)
    return token_user_id == expected_user_id


def create_auth_error_response(message: str = "Unauthorized",
                              status_code: int = status.HTTP_401_UNAUTHORIZED) -> HTTPException:
    """
    Create a standardized authentication error response.

    Args:
        message: Error message to return
        status_code: HTTP status code (default 401)

    Returns:
        HTTPException with standardized format
    """
    return HTTPException(
        status_code=status_code,
        detail=message
    )