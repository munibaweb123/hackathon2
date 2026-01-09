"""NotificationPreference model for user notification settings."""

from datetime import datetime, time
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class NotificationPreference(SQLModel, table=True):
    """User settings for notification delivery."""

    __tablename__ = "notification_preferences"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(
        foreign_key="users.id",
        unique=True,
        nullable=False,
        index=True
    )

    # Notification channels
    in_app_enabled: bool = Field(default=True)  # WebSocket/browser notifications
    email_enabled: bool = Field(default=True)  # Email notifications

    # Reminder timing
    reminder_lead_time: int = Field(default=60, ge=0)  # Minutes before due date

    # Quiet hours (no notifications during this period)
    quiet_hours_start: Optional[time] = Field(default=None)
    quiet_hours_end: Optional[time] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-123",
                "in_app_enabled": True,
                "email_enabled": True,
                "reminder_lead_time": 60,
                "quiet_hours_start": "22:00:00",
                "quiet_hours_end": "08:00:00",
                "created_at": "2024-12-10T10:00:00Z",
                "updated_at": "2024-12-10T10:00:00Z"
            }
        }
