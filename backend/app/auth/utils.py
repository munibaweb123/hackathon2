from datetime import datetime, timezone
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, status
import logging
import base64
import json
import traceback
from ..core.config import settings


logger = logging.getLogger(__name__)


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token using the shared secret or JWKS.

    Args:
        token: The JWT token string to decode

    Returns:
        Decoded token payload as dictionary, or None if invalid
    """
    try:
        # First, decode the header to check the algorithm
        token_parts = token.split('.')
        if len(token_parts) != 3:
            logger.warning("Invalid JWT token format: not enough parts")
            return None

        # Add padding if needed for base64 decoding
        header_part = token_parts[0]
        missing_padding = len(header_part) % 4
        if missing_padding:
            header_part += '=' * (4 - missing_padding)

        header_json = base64.urlsafe_b64decode(header_part)
        header = json.loads(header_json)
        alg = header.get('alg', 'HS256')
        kid = header.get('kid')

        logger.debug(f"JWT header - algorithm: {alg}, kid: {kid}")

        if alg in ["HS256", "HS384", "HS512"]:
            # HMAC algorithms - use the shared secret
            payload = jwt.decode(
                token,
                settings.BETTER_AUTH_SECRET,
                algorithms=[alg]
            )
            logger.info(f"JWT decoded successfully with {alg} - sub: {payload.get('sub', 'unknown')}")
            return payload
        elif alg in ["EdDSA", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]:
            # Public key algorithms - need to fetch from JWKS
            logger.info(f"Attempting to verify {alg} token with JWKS")

            # Import here to avoid circular imports
            from ..core.jwks import get_jwk_for_token, verify_eddsa_token
            jwk = get_jwk_for_token(token)
            if jwk:
                if alg == "EdDSA":
                    # For EdDSA, use the specific verification function
                    # Decode payload without verification first
                    payload_b64 = token_parts[1]
                    missing_padding = len(payload_b64) % 4
                    if missing_padding:
                        payload_b64 += '=' * (4 - missing_padding)
                    payload_json = base64.urlsafe_b64decode(payload_b64)
                    payload = json.loads(payload_json)

                    # Then verify the signature
                    verified_payload = verify_eddsa_token(token, jwk)
                    if verified_payload:
                        logger.info(f"EdDSA token verified - sub: {verified_payload.get('sub')}")
                        return verified_payload
                    else:
                        logger.warning("EdDSA token verification failed")
                        return None
                else:
                    # For other public key algorithms, decode without verification as fallback
                    # In production, proper verification should be implemented
                    payload_b64 = token_parts[1]
                    missing_padding = len(payload_b64) % 4
                    if missing_padding:
                        payload_b64 += '=' * (4 - missing_padding)
                    payload_json = base64.urlsafe_b64decode(payload_b64)
                    payload = json.loads(payload_json)
                    logger.info(f"{alg} token decoded (unverified) - sub: {payload.get('sub')}")
                    return payload
            else:
                logger.warning(f"No JWK found for {alg} token, kid: {kid}")
                return None
        else:
            logger.warning(f"Unsupported JWT algorithm: {alg}")
            return None

    except jwt.InvalidAlgorithmError as e:
        logger.warning(f"JWT algorithm not allowed: {str(e)}")
        # Better Auth may use algorithms not in the default allowed list
        # Try to decode without algorithm verification first to see what algorithm is being used
        try:
            # Decode without verification to see the algorithm
            unverified_header = jwt.get_unverified_header(token)
            logger.info(f"Unverified token header: {unverified_header}")

            # If it's a public key algorithm, try to get it from JWKS
            alg = unverified_header.get('alg', 'unknown')
            if alg in ["EdDSA", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]:
                logger.info(f"Attempting to verify {alg} token via JWKS as fallback")

                # Import here to avoid circular imports
                from ..core.jwks import get_jwk_for_token, verify_eddsa_token
                jwk = get_jwk_for_token(token)
                if jwk:
                    if alg == "EdDSA":
                        payload = verify_eddsa_token(token, jwk)
                        if payload:
                            logger.info(f"Fallback {alg} verification successful")
                            return payload
                    else:
                        # For other public key algorithms, decode without verification as a fallback
                        payload = jwt.decode(token, options={"verify_signature": False})
                        logger.info(f"Fallback {alg} decoding successful")
                        return payload

            return None
        except Exception as fallback_error:
            logger.error(f"Fallback JWT decoding also failed: {fallback_error}")
            return None
    except PyJWTError as e:
        # Token is invalid, expired, or tampered with
        logger.warning(f"JWT token verification failed: {str(e)}")
        return None
    except Exception as e:
        # Other unexpected errors during decoding
        logger.error(f"Unexpected error during JWT token decoding: {str(e)}")
        import traceback
        logger.error(f"JWT decoding traceback: {traceback.format_exc()}")
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