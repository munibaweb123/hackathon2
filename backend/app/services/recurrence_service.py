"""Recurrence service for handling recurring task logic."""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from app.models.recurrence import RecurrencePattern
from app.models.enums import RecurrenceFrequency, RecurrenceStatus
from app.schemas.recurrence import RecurrencePatternCreate, RecurrencePatternUpdate


class RecurrenceService:
    """Service for managing recurrence patterns."""

    def __init__(self, session: Session):
        self.session = session

    def create_recurrence_pattern(
        self,
        recurrence_data: RecurrencePatternCreate,
        user_id: str
    ) -> RecurrencePattern:
        """Create a new recurrence pattern."""
        from app.models.task import Task  # Import here to avoid circular import

        pattern = RecurrencePattern(
            frequency=RecurrenceFrequency(recurrence_data.frequency),
            interval=recurrence_data.interval,
            day_of_week=recurrence_data.day_of_week,
            day_of_month=recurrence_data.day_of_month,
            month_of_year=recurrence_data.month_of_year,
            start_date=recurrence_data.start_date,
            end_date=recurrence_data.end_date,
            count=recurrence_data.count,
            status=RecurrenceStatus.ACTIVE
        )

        self.session.add(pattern)
        self.session.commit()
        self.session.refresh(pattern)

        return pattern

    def get_recurrence_pattern(self, pattern_id: str, user_id: str) -> Optional[RecurrencePattern]:
        """Get a recurrence pattern by ID."""
        statement = select(RecurrencePattern).where(RecurrencePattern.id == pattern_id)
        return self.session.exec(statement).first()

    def update_recurrence_pattern(
        self,
        pattern_id: str,
        recurrence_data: RecurrencePatternUpdate
    ) -> Optional[RecurrencePattern]:
        """Update a recurrence pattern."""
        statement = select(RecurrencePattern).where(RecurrencePattern.id == pattern_id)
        pattern = self.session.exec(statement).first()

        if not pattern:
            return None

        # Update fields that are provided
        for field, value in recurrence_data.model_dump(exclude_unset=True).items():
            if value is not None:
                if field == "frequency":
                    setattr(pattern, field, RecurrenceFrequency(value))
                elif field == "status":
                    setattr(pattern, field, RecurrenceStatus(value))
                else:
                    setattr(pattern, field, value)

        self.session.add(pattern)
        self.session.commit()
        self.session.refresh(pattern)

        return pattern

    def cancel_recurrence_pattern(self, pattern_id: str) -> Optional[RecurrencePattern]:
        """Cancel a recurrence pattern by setting its status to cancelled."""
        statement = select(RecurrencePattern).where(RecurrencePattern.id == pattern_id)
        pattern = self.session.exec(statement).first()

        if not pattern:
            return None

        pattern.status = RecurrenceStatus.CANCELLED
        self.session.add(pattern)
        self.session.commit()
        self.session.refresh(pattern)

        return pattern

    def is_recurrence_active(self, pattern: RecurrencePattern, current_date: Optional[datetime] = None) -> bool:
        """Check if a recurrence pattern is still active."""
        if pattern.status != RecurrenceStatus.ACTIVE:
            return False

        if current_date is None:
            current_date = datetime.utcnow()

        # Check if end date has been reached
        if pattern.end_date and current_date.date() > pattern.end_date:
            # Update status to completed
            pattern.status = RecurrenceStatus.COMPLETED
            self.session.add(pattern)
            self.session.commit()
            return False

        return True

    def calculate_next_occurrence(
        self,
        pattern: RecurrencePattern,
        current_date: datetime
    ) -> Optional[datetime]:
        """Calculate the next occurrence based on the recurrence pattern."""
        from app.utils.recurrence import calculate_next_occurrence

        # Use the existing utility function
        return calculate_next_occurrence(
            start_date=pattern.start_date,
            pattern=pattern.frequency,
            interval=pattern.interval,
            current_date=current_date
        )


def get_recurrence_service(session: Session) -> RecurrenceService:
    """Factory function to get a RecurrenceService instance."""
    return RecurrenceService(session)