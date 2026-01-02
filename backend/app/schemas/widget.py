"""Schema definitions for Widget model."""
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class WidgetBase(BaseModel):
    """Base schema for Widget with shared attributes."""
    id: str
    message_id: UUID
    type: str
    payload: str


class WidgetCreate(WidgetBase):
    """Schema for creating a new Widget."""
    pass


class WidgetUpdate(BaseModel):
    """Schema for updating an existing Widget."""
    payload: Optional[str] = None
    action_handler: Optional[str] = None


class WidgetPublic(WidgetBase):
    """Public schema for Widget with essential information."""
    created_at: datetime
    action_handler: Optional[str] = None