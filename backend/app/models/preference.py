"""User preferences model for todo app settings."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from enum import Enum
import uuid
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


class UserPreference(SQLModel, table=True):
    """User preferences model for todo app settings."""

    __tablename__ = "user_preferences"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True, index=True)

    # UI preferences
    theme: Theme = Field(default=Theme.AUTO)
    language: str = Field(default="en", max_length=10)

    # Notification preferences
    task_notifications: NotificationPreference = Field(default=NotificationPreference.ALL)
    reminder_notifications: NotificationPreference = Field(default=NotificationPreference.ALL)
    email_notifications: bool = Field(default=True)

    # Task display preferences
    default_view: str = Field(default="list", max_length=20)  # list, grid, calendar
    show_completed_tasks: bool = Field(default=True)
    group_by: str = Field(default="none", max_length=20)  # none, priority, due_date, category

    # Advanced preferences
    auto_archive_completed: bool = Field(default=False)
    auto_snooze_time: Optional[int] = Field(default=None)  # minutes
    work_hours_start: str = Field(default="09:00", max_length=5)  # HH:MM format
    work_hours_end: str = Field(default="17:00", max_length=5)    # HH:MM format

    # Custom settings as JSON
    custom_settings: Optional[str] = Field(default=None)  # JSON string for additional settings

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def set_custom_setting(self, key: str, value: Any) -> None:
        """Set a custom preference setting."""
        settings_dict = json.loads(self.custom_settings) if self.custom_settings else {}
        settings_dict[key] = value
        self.custom_settings = json.dumps(settings_dict)

    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """Get a custom preference setting."""
        if not self.custom_settings:
            return default
        settings_dict = json.loads(self.custom_settings)
        return settings_dict.get(key, default)