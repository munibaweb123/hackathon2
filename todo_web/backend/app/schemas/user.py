"""User schemas for API requests/responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a user (synced from Better Auth)."""

    id: str
    email: EmailStr
    name: Optional[str] = None
    email_verified: bool = False
    image: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str
    name: Optional[str] = None
    email_verified: bool
    image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
