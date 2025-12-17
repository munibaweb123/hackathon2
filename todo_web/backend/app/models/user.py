"""User model for SQLModel/PostgreSQL - aligned with Better Auth schema."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid


class User(SQLModel, table=True):
    """User model - aligned with Better Auth schema."""

    __tablename__ = "users"

    # Better Auth standard fields - only include fields that actually exist in Better Auth's schema
    id: str = Field(sa_column_kwargs={"name": "id"}, primary_key=True)  # Better Auth uses its own ID format
    email: str = Field(sa_column_kwargs={"name": "email"}, unique=True, index=True)
    name: Optional[str] = Field(sa_column_kwargs={"name": "name"}, default=None)  # Full name from Better Auth
    email_verified: Optional[datetime] = Field(sa_column_kwargs={"name": "email_verified", "nullable": True}, default=None)  # Better Auth field
    image: Optional[str] = Field(sa_column_kwargs={"name": "image"}, default=None)  # Profile image URL from Better Auth
    created_at: datetime = Field(sa_column_kwargs={"name": "created_at"}, default_factory=datetime.utcnow)
    updated_at: datetime = Field(sa_column_kwargs={"name": "updated_at"}, default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user-123",
                "email": "user@example.com",
                "name": "John Doe",
                "email_verified": "2024-12-10T10:00:00Z",
                "image": "https://example.com/avatar.jpg",
                "created_at": "2024-12-10T10:00:00Z",
                "updated_at": "2024-12-10T10:00:00Z",
            }
        }
