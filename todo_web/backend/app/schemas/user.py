"""User schemas for API requests/responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a user (synced from Better Auth)."""

    id: str
    email: EmailStr
    username: Optional[str] = None
    name: Optional[str] = None  # Keeping the existing name field for compatibility
    email_verified: bool = False
    image: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None  # Keeping for compatibility
    is_active: bool
    is_verified: bool
    email_verified: bool
    image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Schema for updating user profile."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None  # For compatibility


class UserUpdateResponse(BaseModel):
    """Schema for user update response."""

    id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserPublicResponse(BaseModel):
    """Public schema for user response (for other users to see)."""

    id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    is_verified: bool
    created_at: datetime
