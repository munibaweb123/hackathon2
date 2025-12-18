"""Authentication schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserRegistrationRequest(BaseModel):
    """Request schema for user registration."""
    email: EmailStr
    password: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength based on requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')

        if not any(c in '@$!%*?&' for c in v):
            raise ValueError('Password must contain at least one special character (@$!%*?&)')

        return v

    @field_validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if v is not None:
            if len(v) < 3 or len(v) > 30:
                raise ValueError('Username must be between 3 and 30 characters')

            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain alphanumeric characters, underscores, and hyphens')

        return v


class UserRegistrationResponse(BaseModel):
    """Response schema for user registration."""
    success: bool
    user: dict
    message: Optional[str] = "User registered successfully"


class UserLoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Response schema for user login."""
    success: bool
    user: dict
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Response schema for token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Request schema for password reset request."""
    email: EmailStr


class PasswordResetResponse(BaseModel):
    """Response schema for password reset request."""
    success: bool
    message: str


class PasswordResetConfirmRequest(BaseModel):
    """Request schema for password reset confirmation."""
    token: str
    new_password: str

    @field_validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength based on requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')

        if not any(c in '@$!%*?&' for c in v):
            raise ValueError('Password must contain at least one special character (@$!%*?&)')

        return v


class UserProfileUpdateRequest(BaseModel):
    """Request schema for user profile update."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

    @field_validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if v is not None:
            if len(v) < 3 or len(v) > 30:
                raise ValueError('Username must be between 3 and 30 characters')

            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain alphanumeric characters, underscores, and hyphens')

        return v


class UserProfileResponse(BaseModel):
    """Response schema for user profile."""
    id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class AuthErrorResponse(BaseModel):
    """Response schema for authentication errors."""
    success: bool = False
    error: dict


class LogoutResponse(BaseModel):
    """Response schema for logout."""
    success: bool
    message: str