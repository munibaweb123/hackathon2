"""User model for SQLModel/PostgreSQL."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid


class User(SQLModel, table=True):
    """User model - synced with Better Auth users."""

    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    username: Optional[str] = Field(default=None, unique=True, index=True)  # Optional, unique if provided
    password_hash: Optional[str] = Field(default=None)  # Will be stored by Better Auth, but referenced here
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = Field(default=True)  # Whether the account is active
    is_verified: bool = Field(default=False)  # Whether the email is verified
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None  # Last login timestamp
    password_reset_token: Optional[str] = Field(default=None, sa_column_kwargs={"unique": True})  # Token for password reset
    password_reset_expires: Optional[datetime] = None  # When reset token expires
    verification_token: Optional[str] = Field(default=None, sa_column_kwargs={"unique": True})  # Token for email verification
    verification_expires: Optional[datetime] = None  # When verification token expires
    image: Optional[str] = None  # Profile image URL (from Better Auth)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user-123",
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-12-10T10:00:00Z",
                "updated_at": "2024-12-10T10:00:00Z",
            }
        }
