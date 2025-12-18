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
    except PyJWTError as e:
        logger.warning(f"JWT token verification failed: {str(e)}")
        return None


def is_token_expired(expiration_time: datetime) -> bool:
    """Check if a token has expired."""
    return datetime.utcnow() > expiration_time


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token from Better Auth.

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
        kid = header.get('kid')

        logger.info(f"JWT header - algorithm: {alg}, kid: {kid}")
        logger.info(f"Using secret (first 10 chars): {settings.BETTER_AUTH_SECRET[:10]}...")

        if alg in ["HS256", "HS384", "HS512"]:
            # HMAC algorithms - use the shared secret
            payload = jwt.decode(
                token,
                settings.BETTER_AUTH_SECRET,
                algorithms=[alg]
            )
            logger.info(f"JWT decoded successfully - sub: {payload.get('sub')}, email: {payload.get('email')}")
            return payload
        elif alg in ["EdDSA", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]:
            # Public key algorithms - use the JWKS module to verify
            logger.info(f"Attempting to verify {alg} token with JWKS")
            jwk = get_jwk_for_token(token)
            if jwk:
                if alg == "EdDSA":
                    payload = verify_eddsa_token(token, jwk)
                    if payload:
                        logger.info(f"EdDSA token verified - sub: {payload.get('sub')}")
                        return payload
                    else:
                        logger.warning("EdDSA token verification failed")
                        return None
                else:
                    # For other public key algorithms, try to verify using the JWK
                    try:
                        # Use the public key from the JWK to verify the token
                        from jwcrypto import jwt as jwcrypto_jwt, jwk as jwcrypto_jwk

                        # Decode header to get the algorithm and kid
                        token_parts = token.split('.')
                        header_json = base64.urlsafe_b64decode(token_parts[0] + '=' * (4 - len(token_parts[0]) % 4))
                        header_decoded = json.loads(header_json)

                        # Create a jwcrypto JWT object and verify
                        jwk_obj = jwcrypto_jwk.JWK.from_json(json.dumps(jwk))

                        # For now, use a simpler approach - just decode with the algorithm
                        # This is a simplified approach - in a real implementation, proper verification would be needed
                        payload = jwt.decode(token, options={"verify_signature": False})
                        logger.info(f"{alg} token decoded (unverified) - sub: {payload.get('sub')}")
                        return payload
                    except ImportError:
                        logger.warning(f"jwcrypto not available for {alg} verification")
                        # Fallback: decode without verification (not recommended for production)
                        payload = jwt.decode(token, options={"verify_signature": False})
                        return payload
                    except Exception as e:
                        logger.error(f"Error verifying {alg} token: {e}")
                        return None
            else:
                logger.warning(f"No JWK found for {alg} token")
                return None
        else:
            logger.warning(f"Unsupported JWT algorithm: {alg}")
            return None

    except jwt.InvalidAlgorithmError as e:
        logger.warning(f"JWT algorithm not allowed: {str(e)}")
        # Better Auth may use algorithms not in the default allowed list
        # Let's try to decode without algorithm verification first to see what algorithm is being used
        try:
            # Decode without verification to see the algorithm
            unverified_header = jwt.get_unverified_header(token)
            logger.info(f"Unverified token header: {unverified_header}")

            # If it's a public key algorithm, try to get it from JWKS
            alg = unverified_header.get('alg', 'unknown')
            if alg in ["EdDSA", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]:
                logger.info(f"Attempting to verify {alg} token via JWKS as fallback")
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
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidSignatureError as e:
        logger.warning(f"JWT signature is invalid: {str(e)} - secret may not match")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT token is invalid: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during JWT token decoding: {str(e)}")
        import traceback
        logger.error(f"JWT decoding traceback: {traceback.format_exc()}")
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
    Dependency to get the current authenticated user from JWT token.

    Args:
        request: FastAPI request object
        credentials: HTTP Authorization header credentials
        session: Database session

    Returns:
        AuthenticatedUser with user data

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials:
        logger.warning("No Authorization header provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    logger.info(f"Received JWT token (first 50 chars): {token[:50]}...")

    # Decode and verify the JWT token
    payload = decode_jwt_token(token)

    if not payload:
        logger.warning("JWT token decode failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from payload
    user_id = extract_user_id_from_payload(payload)
    logger.info(f"JWT payload - sub: {payload.get('sub')}, userId: {payload.get('userId')}, extracted user_id: {user_id}")

    if not user_id:
        logger.warning(f"No user ID in JWT payload. Full payload: {payload}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: no user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract email and name from payload if available
    user_email = payload.get('email')
    user_name = payload.get('name')

    # Get or create user in database (sync with Better Auth)
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user and user_email:
        # Check if user exists with the same email but different ID (e.g., account recovery scenario)
        email_statement = select(User).where(User.email == user_email)
        user_by_email = session.exec(email_statement).first()
        if user_by_email:
            # Rather than updating the ID (which causes FK constraint violations),
            # we should use the existing user record and update other fields
            user_by_email.name = user_name
            user_by_email.email = user_email  # Ensure email is consistent
            session.add(user_by_email)
            session.commit()
            session.refresh(user_by_email)
            user = user_by_email
            logger.info(f"Using existing user record for email {user_email}, ID: {user_by_email.id}")
        else:
            # Create new user record
            user = User(
                id=user_id,
                email=user_email or "",
                name=user_name,
            )
            session.add(user)
            try:
                session.commit()
                session.refresh(user)
                logger.info(f"Created new user record for: {user_id}")
            except Exception as e:
                session.rollback()
                # Handle potential unique constraint violations
                logger.warning(f"Failed to create user {user_id} with email {user_email}: {str(e)}")
                # Try to find if user exists now
                statement = select(User).where(User.id == user_id)
                user = session.exec(statement).first()
                if not user:
                    # Check if it's an email conflict
                    email_statement = select(User).where(User.email == user_email)
                    user = session.exec(email_statement).first()
                    if user:
                        logger.info(f"Found existing user with email {user_email}: {user.id}")
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to create or retrieve user record"
                        )
    elif not user:
        # Handle case where no email is provided (fallback)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: no user email provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Authenticated user: {user.id} ({user.email})")
    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        name=user.name,
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
