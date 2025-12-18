"""Security utilities for authentication including password hashing and validation."""

import re
from typing import Optional
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import BaseModel


class TokenData(BaseModel):
    """Data contained in JWT token."""
    user_id: str
    email: str
    exp: Optional[int] = None


# Password validation patterns
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength based on requirements:
    - At least 8 characters
    - Contains uppercase, lowercase, number, and special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    if not re.search(r"[@$!%*?&]", password):
        return False, "Password must contain at least one special character (@$!%*?&)"

    return True, "Password is valid"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    from .config import settings  # Import here to avoid circular imports

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
    from .config import settings  # Import here to avoid circular imports

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default to 7 days if no expiration is provided
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, secret_key: str) -> Optional[TokenData]:
    """Verify a JWT token and return the token data."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None or email is None:
            return None

        token_data = TokenData(user_id=user_id, email=email, exp=payload.get("exp"))
        return token_data
    except JWTError:
        return None


def generate_verification_token() -> str:
    """Generate a verification token."""
    import secrets
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Generate a password reset token."""
    import secrets
    return secrets.token_urlsafe(32)


def is_token_expired(expiration_time: datetime) -> bool:
    """Check if a token has expired."""
    return datetime.utcnow() > expiration_time