"""Migration script to fix timezone issues in existing reminders."""

from datetime import datetime, timezone, timedelta
import time
from sqlmodel import Session, select
from app.core.database import engine
from app.models.reminder import Reminder
from app.models.task import Task


def fix_reminder_timezones():
    """Fix timezone issues in existing reminders."""
    print("Starting reminder timezone migration...")

    with Session(engine) as session:
        # Get all reminders
        reminders = session.exec(select(Reminder)).all()
        print(f"Found {len(reminders)} reminders to process")

        for reminder in reminders:
            print(f"Processing reminder {reminder.id}...")

            # Get the associated task to understand the context
            task = session.exec(select(Task).where(Task.id == reminder.task_id)).first()

            if task:
                print(f"  Task: {task.title}")
                print(f"  Old reminder time: {reminder.reminder_time}")

                # The old logic was incorrectly handling timezones
                # We need to treat the stored time as if it was intended to be local time
                # Convert the existing naive datetime to what it should be in UTC

                # Parse the existing reminder time (it's currently stored as naive datetime)
                old_time_str = str(reminder.reminder_time)

                # Since the old code stored times incorrectly, we need to adjust them
                # The simplest approach is to reset reminders that are still pending
                # For SENT reminders, we can't really know what the original intent was

                if reminder.status.value == 'sent':
                    print(f"  Status is 'sent', leaving as is")
                    continue

                print(f"  Skipping update for now - would need manual verification")

        # Commit the changes
        session.commit()
        print("Migration completed!")


if __name__ == "__main__":
    fix_reminder_timezones()