"""Reminder scheduling service for managing task reminders.

This service handles:
- Scheduling reminders for tasks with due dates
- Checking for upcoming reminders that need to be triggered
- Publishing reminder events to the notification service
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, col

from ..models.task import Task
from ..models.enums import TaskStatus
from ..models.notification_preference import NotificationPreference
from .event_publisher import get_event_publisher

logger = logging.getLogger(__name__)

# Default reminder lead time (minutes before due_date)
DEFAULT_REMINDER_LEAD_TIME = 60


class ReminderScheduler:
    """Service for scheduling and triggering task reminders."""

    def __init__(self, session: Session):
        self.session = session
        self._publisher = None

    @property
    def publisher(self):
        """Lazy-load the event publisher."""
        if self._publisher is None:
            self._publisher = get_event_publisher()
        return self._publisher

    def get_upcoming_reminders(
        self,
        window_minutes: int = 5
    ) -> List[Task]:
        """
        Get tasks with reminders due within the specified time window.

        Args:
            window_minutes: How many minutes ahead to look for reminders

        Returns:
            List of tasks with reminders due within the window
        """
        now = datetime.utcnow()
        window_end = now + timedelta(minutes=window_minutes)

        statement = (
            select(Task)
            .where(
                Task.reminder_at.isnot(None),
                Task.reminder_at >= now,
                Task.reminder_at <= window_end,
                Task.status != TaskStatus.COMPLETED,
            )
            .order_by(col(Task.reminder_at).asc())
        )

        return list(self.session.exec(statement).all())

    def get_overdue_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        """
        Get all tasks that are past their due date but not completed.

        Args:
            user_id: Optional filter by user

        Returns:
            List of overdue tasks
        """
        now = datetime.utcnow()

        statement = select(Task).where(
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status != TaskStatus.COMPLETED,
        )

        if user_id:
            statement = statement.where(Task.user_id == user_id)

        return list(self.session.exec(statement).all())

    def get_user_notification_preferences(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get notification preferences for a user.

        Args:
            user_id: The user ID

        Returns:
            Dictionary of notification preferences
        """
        statement = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        )
        prefs = self.session.exec(statement).first()

        if prefs:
            return {
                "in_app": prefs.in_app_enabled,
                "email": prefs.email_enabled,
                "reminder_lead_time": prefs.reminder_lead_time,
                "quiet_hours_start": prefs.quiet_hours_start.isoformat() if prefs.quiet_hours_start else None,
                "quiet_hours_end": prefs.quiet_hours_end.isoformat() if prefs.quiet_hours_end else None,
            }

        # Return defaults if no preferences are set
        return {
            "in_app": True,
            "email": True,
            "reminder_lead_time": DEFAULT_REMINDER_LEAD_TIME,
            "quiet_hours_start": None,
            "quiet_hours_end": None,
        }

    def is_within_quiet_hours(
        self,
        prefs: Dict[str, Any],
        check_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if the given time falls within the user's quiet hours.

        Args:
            prefs: User notification preferences
            check_time: Time to check (defaults to now)

        Returns:
            True if within quiet hours, False otherwise
        """
        if not prefs.get("quiet_hours_start") or not prefs.get("quiet_hours_end"):
            return False

        check_time = check_time or datetime.utcnow()
        current_time = check_time.time()

        from datetime import time as dt_time
        start = dt_time.fromisoformat(prefs["quiet_hours_start"])
        end = dt_time.fromisoformat(prefs["quiet_hours_end"])

        # Handle overnight quiet hours (e.g., 22:00 to 07:00)
        if start <= end:
            return start <= current_time <= end
        else:
            return current_time >= start or current_time <= end

    async def process_pending_reminders(self) -> int:
        """
        Process all pending reminders and publish events for immediate ones.

        This method is designed to be called periodically by a cron job
        or scheduled task (e.g., every minute).

        Returns:
            Number of reminders processed
        """
        tasks = self.get_upcoming_reminders(window_minutes=1)
        processed = 0

        for task in tasks:
            try:
                prefs = self.get_user_notification_preferences(task.user_id)

                # Skip if within quiet hours
                if self.is_within_quiet_hours(prefs, task.reminder_at):
                    logger.info(
                        f"Skipping reminder for task {task.id} - within quiet hours"
                    )
                    continue

                # Publish reminder event
                success = await self.publisher.publish_reminder_event(
                    task_id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    due_at=task.due_date,
                    remind_at=task.reminder_at,
                    notification_preferences={
                        "in_app": prefs["in_app"],
                        "email": prefs["email"],
                    },
                    description=task.description,
                )

                if success:
                    processed += 1
                    logger.info(f"Published reminder for task {task.id}")
                else:
                    logger.error(f"Failed to publish reminder for task {task.id}")

            except Exception as e:
                logger.exception(f"Error processing reminder for task {task.id}: {e}")

        return processed

    def calculate_auto_reminder_time(
        self,
        due_date: datetime,
        lead_time_minutes: Optional[int] = None
    ) -> datetime:
        """
        Calculate the automatic reminder time based on due date and lead time.

        Args:
            due_date: The task's due date
            lead_time_minutes: Minutes before due date (uses user preference or default)

        Returns:
            The calculated reminder time
        """
        lead_time = lead_time_minutes or DEFAULT_REMINDER_LEAD_TIME
        return due_date - timedelta(minutes=lead_time)


def get_reminder_scheduler(session: Session) -> ReminderScheduler:
    """Factory function to get a ReminderScheduler instance."""
    return ReminderScheduler(session)
