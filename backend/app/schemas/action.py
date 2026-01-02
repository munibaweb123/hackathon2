"""Schema definitions for Action model."""
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class ActionBase(BaseModel):
    """Base schema for Action with shared attributes."""
    thread_id: UUID
    type: str
    payload: str


class ActionCreate(ActionBase):
    """Schema for creating a new Action."""
    widget_id: Optional[str] = None


class ActionUpdate(BaseModel):
    """Schema for updating an existing Action."""
    widget_id: Optional[str] = None
    processed_at: Optional[datetime] = None
    result: Optional[str] = None


class ActionPublic(ActionBase):
    """Public schema for Action with essential information."""
    id: UUID
    widget_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    result: Optional[str] = None