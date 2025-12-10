"""Reminder model for task reminders and notifications."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
import uuid


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


class Reminder(SQLModel, table=True):
    """Reminder model for task notifications."""

    __tablename__ = "reminders"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    reminder_time: datetime = Field(index=True)
    reminder_type: ReminderType = Field(default=ReminderType.PUSH)
    status: ReminderStatus = Field(default=ReminderStatus.PENDING)
    message: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to task
    task: "Task" = Relationship(back_populates="reminders")