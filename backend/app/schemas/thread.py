"""Schema definitions for Thread model."""
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class ThreadBase(BaseModel):
    """Base schema for Thread with shared attributes."""
    user_id: UUID
    title: str


class ThreadCreate(ThreadBase):
    """Schema for creating a new Thread."""
    pass


class ThreadUpdate(BaseModel):
    """Schema for updating an existing Thread."""
    title: Optional[str] = None
    metadata: Optional[str] = None


class ThreadPublic(ThreadBase):
    """Public schema for Thread with essential information."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    metadata: Optional[str] = None