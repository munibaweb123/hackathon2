"""User model for SQLModel/PostgreSQL."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid


class User(SQLModel, table=True):
    """User model - synced with Better Auth users."""

    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    email_verified: bool = Field(default=False)
    image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user-123",
                "email": "user@example.com",
                "name": "John Doe",
                "email_verified": True,
                "created_at": "2024-12-10T10:00:00Z",
                "updated_at": "2024-12-10T10:00:00Z",
            }
        }
