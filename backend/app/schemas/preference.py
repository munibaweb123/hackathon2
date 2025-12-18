"""User preference schemas for API requests/responses."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import json


class Theme(str, Enum):
    """UI theme options."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class NotificationPreference(str, Enum):
    """Notification preference options."""
    ALL = "all"
    MUTE = "mute"
    SCHEDULED = "scheduled"


class UserPreferenceCreate(BaseModel):
    """Schema for creating user preferences."""

    # UI preferences
    theme: Optional[Theme] = Theme.AUTO
    language: Optional[str] = Field(default="en", max_length=10)

    # Notification preferences
    task_notifications: Optional[NotificationPreference] = NotificationPreference.ALL
    reminder_notifications: Optional[NotificationPreference] = NotificationPreference.ALL
    email_notifications: Optional[bool] = True

    # Task display preferences
    default_view: Optional[str] = Field(default="list", max_length=20)
    show_completed_tasks: Optional[bool] = True
    group_by: Optional[str] = Field(default="none", max_length=20)

    # Advanced preferences
    auto_archive_completed: Optional[bool] = False
    auto_snooze_time: Optional[int] = Field(default=None, ge=1, le=1440)  # 1 minute to 24 hours
    work_hours_start: Optional[str] = Field(default="09:00", max_length=5)  # HH:MM format
    work_hours_end: Optional[str] = Field(default="17:00", max_length=5)    # HH:MM format

    # Custom settings as JSON
    custom_settings: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "auto",
                "language": "en",
                "task_notifications": "all",
                "default_view": "list",
                "show_completed_tasks": True,
                "auto_archive_completed": False
            }
        }


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences."""

    # UI preferences
    theme: Optional[Theme] = None
    language: Optional[str] = Field(None, max_length=10)

    # Notification preferences
    task_notifications: Optional[NotificationPreference] = None
    reminder_notifications: Optional[NotificationPreference] = None
    email_notifications: Optional[bool] = None

    # Task display preferences
    default_view: Optional[str] = Field(None, max_length=20)
    show_completed_tasks: Optional[bool] = None
    group_by: Optional[str] = Field(None, max_length=20)

    # Advanced preferences
    auto_archive_completed: Optional[bool] = None
    auto_snooze_time: Optional[int] = Field(None, ge=1, le=1440)  # 1 minute to 24 hours
    work_hours_start: Optional[str] = Field(None, max_length=5)  # HH:MM format
    work_hours_end: Optional[str] = Field(None, max_length=5)    # HH:MM format

    # Custom settings as JSON
    custom_settings: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "show_completed_tasks": False,
                "auto_archive_completed": True
            }
        }


class UserPreferenceResponse(BaseModel):
    """Schema for user preference response."""

    id: str
    user_id: str

    # UI preferences
    theme: Theme
    language: str

    # Notification preferences
    task_notifications: NotificationPreference
    reminder_notifications: NotificationPreference
    email_notifications: bool

    # Task display preferences
    default_view: str
    show_completed_tasks: bool
    group_by: str

    # Advanced preferences
    auto_archive_completed: bool
    auto_snooze_time: Optional[int]
    work_hours_start: str
    work_hours_end: str

    # Custom settings as JSON
    custom_settings: Optional[Dict[str, Any]]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def validate_time_format(cls, time_str: str) -> bool:
        """Validate HH:MM format."""
        if not time_str or len(time_str) != 5 or time_str[2] != ':':
            return False
        try:
            hours, minutes = time_str.split(':')
            h, m = int(hours), int(minutes)
            return 0 <= h <= 23 and 0 <= m <= 59
        except ValueError:
            return False