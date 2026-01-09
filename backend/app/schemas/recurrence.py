"""Recurrence pattern schemas for API requests/responses."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class RecurrenceFrequency(str, Enum):
    """Recurrence frequency options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"  # Every two weeks
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurrenceStatus(str, Enum):
    """Recurrence status options."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecurrencePatternCreate(BaseModel):
    """Schema for creating a recurrence pattern."""

    frequency: RecurrenceFrequency = Field(..., description="How often the task repeats")
    interval: int = Field(1, ge=1, description="Every N frequency units (e.g., every 2 weeks)")

    # For weekly recurrence: 0-6 (Monday-Sunday)
    day_of_week: Optional[List[int]] = Field(
        None,
        description="Days of the week for weekly recurrence (0=Monday, 6=Sunday)"
    )

    # For monthly recurrence: 1-31
    day_of_month: Optional[List[int]] = Field(
        None,
        description="Days of the month for monthly recurrence (1-31)"
    )

    # For yearly recurrence: 1-12
    month_of_year: Optional[List[int]] = Field(
        None,
        description="Months of the year for yearly recurrence (1=January, 12=December)"
    )

    start_date: date = Field(..., description="When recurrence begins")
    end_date: Optional[date] = Field(None, description="When recurrence ends (NULL = never)")
    count: Optional[int] = Field(None, ge=1, description="Max occurrences (NULL = unlimited)")

    class Config:
        json_schema_extra = {
            "example": {
                "frequency": "weekly",
                "interval": 1,
                "day_of_week": [0, 2, 4],  # Monday, Wednesday, Friday
                "start_date": "2024-12-01",
                "end_date": "2025-12-01",
                "count": None,
            }
        }


class RecurrencePatternUpdate(BaseModel):
    """Schema for updating a recurrence pattern."""

    frequency: Optional[RecurrenceFrequency] = Field(None, description="How often the task repeats")
    interval: Optional[int] = Field(None, ge=1, description="Every N frequency units (e.g., every 2 weeks)")

    # For weekly recurrence: 0-6 (Monday-Sunday)
    day_of_week: Optional[List[int]] = Field(
        None,
        description="Days of the week for weekly recurrence (0=Monday, 6=Sunday)"
    )

    # For monthly recurrence: 1-31
    day_of_month: Optional[List[int]] = Field(
        None,
        description="Days of the month for monthly recurrence (1-31)"
    )

    # For yearly recurrence: 1-12
    month_of_year: Optional[List[int]] = Field(
        None,
        description="Months of the year for yearly recurrence (1=January, 12=December)"
    )

    end_date: Optional[date] = Field(None, description="When recurrence ends (NULL = never)")
    count: Optional[int] = Field(None, ge=1, description="Max occurrences (NULL = unlimited)")
    status: Optional[RecurrenceStatus] = Field(None, description="Current status of the recurrence pattern")


class RecurrencePatternResponse(BaseModel):
    """Schema for recurrence pattern response."""

    id: str  # UUID as string
    frequency: RecurrenceFrequency
    interval: int

    # For weekly recurrence: 0-6 (Monday-Sunday)
    day_of_week: Optional[List[int]] = None

    # For monthly recurrence: 1-31
    day_of_month: Optional[List[int]] = None

    # For yearly recurrence: 1-12
    month_of_year: Optional[List[int]] = None

    start_date: date
    end_date: Optional[date] = None
    count: Optional[int] = None
    status: RecurrenceStatus
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "frequency": "weekly",
                "interval": 1,
                "day_of_week": [0, 2, 4],  # Monday, Wednesday, Friday
                "start_date": "2024-12-01",
                "end_date": "2025-12-01",
                "count": None,
                "status": "active",
                "created_at": "2024-12-10T10:00:00Z"
            }
        }