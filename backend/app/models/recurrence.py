"""RecurrencePattern model for defining how tasks repeat."""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, Integer

from .enums import RecurrenceFrequency, RecurrenceStatus


class RecurrencePattern(SQLModel, table=True):
    """Defines how a task repeats."""

    __tablename__ = "recurrence_patterns"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    frequency: RecurrenceFrequency = Field(nullable=False)
    interval: int = Field(default=1, ge=1)  # Every N frequency units

    # For weekly recurrence: 0-6 (Monday-Sunday)
    day_of_week: Optional[List[int]] = Field(
        default=None,
        sa_column=Column(ARRAY(Integer), nullable=True)
    )

    # For monthly recurrence: 1-31
    day_of_month: Optional[List[int]] = Field(
        default=None,
        sa_column=Column(ARRAY(Integer), nullable=True)
    )

    # For yearly recurrence: 1-12
    month_of_year: Optional[List[int]] = Field(
        default=None,
        sa_column=Column(ARRAY(Integer), nullable=True)
    )

    start_date: date = Field(nullable=False)
    end_date: Optional[date] = Field(default=None)  # NULL = never ends
    count: Optional[int] = Field(default=None, ge=1)  # Max occurrences, NULL = unlimited

    status: RecurrenceStatus = Field(default=RecurrenceStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "frequency": "weekly",
                "interval": 1,
                "day_of_week": [0, 2, 4],  # Monday, Wednesday, Friday
                "day_of_month": None,
                "month_of_year": None,
                "start_date": "2024-12-01",
                "end_date": "2025-12-01",
                "count": None,
                "status": "active",
                "created_at": "2024-12-10T10:00:00Z"
            }
        }
