"""User model for SQLModel/PostgreSQL - aligned with Better Auth schema."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid


class User(SQLModel, table=True):
    """User model - aligned with Better Auth schema.

    Better Auth is configured to use the 'users' table with snake_case field mappings.
    """

    __tablename__ = "users"

    # Better Auth standard fields
    id: str = Field(sa_column_kwargs={"name": "id"}, primary_key=True)  # Better Auth uses its own ID format
    email: str = Field(sa_column_kwargs={"name": "email"}, unique=True, index=True)
    name: Optional[str] = Field(sa_column_kwargs={"name": "name"}, default=None)  # Full name from Better Auth
    # Note: Better Auth uses boolean for emailVerified, mapped to email_verified column
    email_verified: Optional[bool] = Field(sa_column_kwargs={"name": "email_verified", "nullable": True}, default=False)
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
