"""Reminder schemas for API requests/responses."""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer
from enum import Enum


class ReminderType(str, Enum):
    """Types of reminders."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"  # Future extension


class ReminderStatus(str, Enum):
    """Status of reminders."""
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"


class ReminderCreate(BaseModel):
    """Schema for creating a new reminder."""

    task_id: int
    reminder_time: datetime
    reminder_type: ReminderType = ReminderType.PUSH
    message: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "reminder_time": "2024-12-15T17:00:00Z",
                "reminder_type": "push",
                "message": "Time to complete your task!"
            }
        }


class ReminderUpdate(BaseModel):
    """Schema for updating an existing reminder."""

    reminder_time: Optional[datetime] = None
    reminder_type: Optional[ReminderType] = None
    status: Optional[ReminderStatus] = None
    message: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "reminder_time": "2024-12-15T18:00:00Z",
                "status": "cancelled"
            }
        }


class ReminderResponse(BaseModel):
    """Schema for reminder response."""

    id: str
    task_id: int
    user_id: str
    reminder_time: datetime
    reminder_type: ReminderType
    status: ReminderStatus
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer('reminder_time', 'created_at', 'updated_at')
    def serialize_datetime(self, v: datetime) -> str:
        """Serialize datetime to ISO format with Z suffix for UTC."""
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.isoformat()

    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    """Schema for paginated reminder list response."""

    reminders: List[ReminderResponse]
    total: int
    page: int = 1
    page_size: int = 50

    class Config:
        json_schema_extra = {
            "example": {
                "reminders": [],
                "total": 0,
                "page": 1,
                "page_size": 50,
            }
        }