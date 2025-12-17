"""JWT-based authentication for Better Auth integration."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlmodel import Session, select
import logging
import base64
import json
import httpx
from urllib.parse import urljoin

from .config import settings
from .database import get_session
from .jwks import get_jwk_for_token, verify_eddsa_token
from ..models.user import User


logger = logging.getLogger(__name__)

# Security scheme for JWT Bearer tokens
security = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """Authenticated user data passed to endpoints."""

    id: str
    email: Optional[str] = None
    name: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default to 1 hour if no expiration is provided
        expire = datetime.utcnow() + timedelta(hours=1)

    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default to 7 days if no expiration is provided
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire.timestamp(), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.JWTError as e:
        logger.warning(f"JWT token verification failed: {str(e)}")
        return None


def is_token_expired(expiration_time: datetime) -> bool:
    """Check if a token has expired."""
    return datetime.utcnow() > expiration_time


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token, supporting various algorithms including EdDSA.

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

        # Decode the header part (first part)
        header_part = token_parts[0]
        # Add padding if needed for base64 decoding
        missing_padding = len(header_part) % 4
        if missing_padding:
            header_part += '=' * (4 - missing_padding)

        header_json = base64.b64decode(header_part)
        header = json.loads(header_json)
        alg = header.get('alg', 'HS256')
        kid = header.get('kid')  # Key ID for JWKS lookup

        logger.debug(f"JWT token algorithm: {alg}, kid: {kid}")

        if alg in ["HS256", "HS384", "HS512"]:
            # HMAC algorithms - use the shared secret
            payload = jwt.decode(
                token,
                settings.BETTER_AUTH_SECRET,
                algorithms=[alg]
            )
            logger.debug(f"Successfully decoded JWT token using HMAC for user: {payload.get('sub', 'unknown')}")
            return payload
        elif alg == "EdDSA":
            # EdDSA algorithm - use the JWKS module to verify
            logger.debug("Attempting to verify EdDSA token with JWKS")
            jwk = get_jwk_for_token(token)
            if jwk:
                payload = verify_eddsa_token(token, jwk)
                if payload:
                    logger.debug(f"Successfully verified EdDSA token for user: {payload.get('sub', 'unknown')}")
                    return payload
                else:
                    logger.warning("EdDSA token verification failed")
                    return None
            else:
                logger.warning("No JWK found for EdDSA token")
                # For security, if we can't properly verify the token with the appropriate algorithm,
                # we return None to indicate authentication failure
                # In a production system, you might want to implement a call to Better Auth's API
                # to validate the session, but that would require additional network calls
                logger.warning("Unable to verify EdDSA token - no public key available")
                return None
        elif alg in ["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]:
            # Other asymmetric algorithms - would need different verification methods
            logger.warning(f"Asymmetric algorithm {alg} requires public key verification, which is not fully implemented")
            return None
        else:
            logger.warning(f"Unsupported JWT algorithm: {alg}")
            return None

    except jwt.InvalidAlgorithmError as e:
        logger.warning(f"JWT algorithm not allowed: {str(e)}")
        return None
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidSignatureError as e:
        logger.warning(f"JWT signature is invalid: {str(e)}")
        # This could happen if the secret doesn't match or algorithm is wrong
        # For security, we should not accept invalid signatures
        # Instead, we'll return None to indicate authentication failure
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT token is invalid: {str(e)}")
        return None
    except Exception as e:
        # Other unexpected errors during decoding
        logger.error(f"Unexpected error during JWT token decoding: {str(e)}")
        import traceback
        logger.debug(f"JWT decoding traceback: {traceback.format_exc()}")
        return None


def extract_user_id_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extract the user ID from a decoded JWT payload.

    Better Auth typically stores user ID in 'sub' (subject) field.

    Args:
        payload: The decoded JWT payload

    Returns:
        User ID string if found, None otherwise
    """
    # Better Auth stores user ID in 'sub' field
    return payload.get('sub') or payload.get('userId') or payload.get('id')


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> AuthenticatedUser:
    """
    Dependency to get the current authenticated user from JWT token or via Better Auth session validation.

    Args:
        request: FastAPI request object
        credentials: HTTP Authorization header credentials
        session: Database session

    Returns:
        AuthenticatedUser with user data

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    # First, try to authenticate with JWT token from Authorization header
    if credentials:
        token = credentials.credentials

        # Decode and verify the JWT token
        payload = decode_jwt_token(token)

        if payload:
            # Extract user ID from payload
            user_id = extract_user_id_from_payload(payload)

            if user_id:
                # Extract email and name from payload if available
                user_email = payload.get('email')
                user_name = payload.get('name')

                # Get or create user in database (sync with Better Auth)
                statement = select(User).where(User.id == user_id)
                user = session.exec(statement).first()

                if not user:
                    # Create user record if it doesn't exist (first time from Better Auth)
                    user = User(
                        id=user_id,
                        email=user_email or "",
                        name=user_name,
                    )
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    logger.info(f"Created new user record for: {user_id}")

                return AuthenticatedUser(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                )

        # If JWT token is invalid, raise unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        # No JWT token provided, try to validate session with Better Auth API
        # This approach works when the frontend can't send JWT in headers
        # but the session cookies are available to make a request to Better Auth
        try:
            # Get Better Auth URL from settings
            better_auth_url = settings.BETTER_AUTH_URL

            # Make a request to Better Auth's session endpoint to validate the session
            # This will work if the request includes the session cookies
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Copy cookies from the original request to validate session
                cookies_dict = dict(request.cookies)

                response = await client.get(
                    f"{better_auth_url}/api/auth/session",
                    cookies=cookies_dict,
                    headers={"accept": "application/json"}
                )

                if response.status_code == 200:
                    session_data = response.json()
                    if "user" in session_data and session_data["user"]:
                        user_info = session_data["user"]
                        user_id = user_info.get("id")

                        if user_id:
                            # Extract email and name from session data
                            user_email = user_info.get("email", "")
                            user_name = user_info.get("name")

                            # Get or create user in database (sync with Better Auth)
                            statement = select(User).where(User.id == user_id)
                            user = session.exec(statement).first()

                            if not user:
                                # Create user record if it doesn't exist (first time from Better Auth)
                                user = User(
                                    id=user_id,
                                    email=user_email,
                                    name=user_name,
                                )
                                session.add(user)
                                session.commit()
                                session.refresh(user)
                                logger.info(f"Created new user record for: {user_id}")

                            return AuthenticatedUser(
                                id=user.id,
                                email=user.email,
                                name=user.name,
                            )

        except Exception as e:
            logger.warning(f"Better Auth session validation failed: {e}")
            # Continue to raise unauthorized error below

        # If no JWT token and session validation failed, raise unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_user_access(user_id_from_path: str, current_user: AuthenticatedUser) -> None:
    """
    Verify that the authenticated user has access to the requested resource.

    Args:
        user_id_from_path: User ID from URL path
        current_user: Currently authenticated user

    Raises:
        HTTPException: If user doesn't have access
    """
    if user_id_from_path != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources",
        )


def log_auth_event(
    event_type: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    details: Optional[str] = None
) -> None:
    """
    Log authentication events for audit purposes.

    Args:
        event_type: Type of event (login, logout, register, password_reset, etc.)
        user_id: User ID if available
        email: Email if available
        ip_address: Client IP address
        user_agent: Client user agent string
        success: Whether the action was successful
        details: Additional details about the event
    """
    log_level = logging.INFO if success else logging.WARNING

    log_message = f"AUTH_AUDIT | event={event_type} | success={success}"

    if user_id:
        log_message += f" | user_id={user_id}"
    if email:
        log_message += f" | email={email}"
    if ip_address:
        log_message += f" | ip={ip_address}"
    if user_agent:
        # Truncate user agent to avoid extremely long log lines
        truncated_ua = user_agent[:100] + "..." if len(user_agent) > 100 else user_agent
        log_message += f" | user_agent={truncated_ua}"
    if details:
        log_message += f" | details={details}"

    logger.log(log_level, log_message)
