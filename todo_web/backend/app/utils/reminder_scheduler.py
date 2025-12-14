"""Background scheduler for checking and sending reminder notifications."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Set
import json

from sqlmodel import Session, select
from fastapi import WebSocket, WebSocketDisconnect

from ..core.database import engine
from ..models.reminder import Reminder, ReminderStatus
from ..models.task import Task


# Global WebSocket connections storage
websocket_connections: Dict[str, Set[WebSocket]] = {}


class ReminderNotificationManager:
    """Manages reminder notifications and WebSocket connections."""

    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}

    def connect(self, websocket: WebSocket, user_id: str):
        """Add a WebSocket connection for a user."""
        if user_id not in self.connections:
            self.connections[user_id] = set()
        self.connections[user_id].add(websocket)
        logging.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection for a user."""
        if user_id in self.connections:
            self.connections[user_id].discard(websocket)
            logging.info(f"WebSocket disconnected for user {user_id}. Remaining: {len(self.connections[user_id])}")
            if not self.connections[user_id]:
                del self.connections[user_id]

    async def send_reminder_to_user(self, user_id: str, reminder_data: dict):
        """Send a reminder notification to a specific user."""
        if user_id in self.connections:
            disconnected = set()
            for connection in self.connections[user_id].copy():
                try:
                    await connection.send_text(json.dumps(reminder_data))
                except WebSocketDisconnect:
                    disconnected.add(connection)
                except Exception as e:
                    logging.error(f"Error sending reminder to user {user_id}: {str(e)}")
                    disconnected.add(connection)

            # Clean up disconnected connections
            for connection in disconnected:
                self.connections[user_id].discard(connection)
            if user_id in self.connections and not self.connections[user_id]:
                del self.connections[user_id]

    async def broadcast_reminder(self, reminder_data: dict):
        """Send a reminder notification to all connected users."""
        disconnected_users = []
        for user_id, connections in self.connections.items():
            disconnected = set()
            for connection in connections.copy():
                try:
                    await connection.send_text(json.dumps(reminder_data))
                except WebSocketDisconnect:
                    disconnected.add(connection)
                except Exception as e:
                    logging.error(f"Error broadcasting reminder to user {user_id}: {str(e)}")
                    disconnected.add(connection)

            # Clean up disconnected connections for this user
            for connection in disconnected:
                connections.discard(connection)
            if not connections:
                disconnected_users.append(user_id)

        # Clean up users with no connections
        for user_id in disconnected_users:
            if user_id in self.connections:
                del self.connections[user_id]


# Global instance
notification_manager = ReminderNotificationManager()


async def check_and_send_due_reminders():
    """
    Check for reminders that are due and send notifications.

    This function should be run periodically by a background scheduler.
    """
    logging.info("Checking for due reminders...")

    try:
        with Session(engine) as session:
            # Get all pending reminders that are due (trigger time <= now)
            now = datetime.now(timezone.utc)
            statement = select(Reminder).where(
                Reminder.status == ReminderStatus.PENDING,
                Reminder.reminder_time <= now
            )

            due_reminders = session.exec(statement).all()

            if not due_reminders:
                logging.info("No due reminders found.")
                return

            logging.info(f"Found {len(due_reminders)} due reminders to process.")

            # Process each due reminder
            for reminder in due_reminders:
                logging.info(f"Processing reminder {reminder.id} for task {reminder.task_id}")

                # Get the associated task to include in the notification
                task_statement = select(Task).where(Task.id == reminder.task_id)
                task = session.exec(task_statement).first()

                if task:
                    # Prepare notification data
                    reminder_data = {
                        "type": "reminder",
                        "reminder_id": str(reminder.id),
                        "task_id": str(reminder.task_id),
                        "user_id": str(reminder.user_id),
                        "title": task.title,
                        "description": task.description,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "message": reminder.message or f"Reminder for task: {task.title}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }

                    # Send the notification via WebSocket
                    await notification_manager.send_reminder_to_user(reminder.user_id, reminder_data)

                    # Update reminder status to 'sent'
                    reminder.status = ReminderStatus.SENT
                    reminder.updated_at = datetime.now(timezone.utc)

                    session.add(reminder)

            session.commit()
            logging.info(f"Successfully processed {len(due_reminders)} reminders.")

    except Exception as e:
        logging.error(f"Error processing due reminders: {str(e)}")
        # Don't commit if there was an error
        raise


async def run_scheduler(interval: int = 60):
    """
    Run the reminder scheduler continuously.

    Args:
        interval: How often to check for due reminders (in seconds)
    """
    logging.info(f"Starting reminder scheduler with {interval}s interval")

    while True:
        try:
            await check_and_send_due_reminders()
        except Exception as e:
            logging.error(f"Scheduler error: {str(e)}")

        # Wait for the specified interval before next check
        await asyncio.sleep(interval)


def start_scheduler(interval: int = 60):
    """
    Start the reminder scheduler in the background.

    Args:
        interval: How often to check for due reminders (in seconds)
    """
    import threading

    def run_scheduler_thread():
        # Create a new event loop for the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_scheduler(interval))

    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=run_scheduler_thread, daemon=True)
    scheduler_thread.start()

    logging.info("Reminder scheduler started in background thread")


def get_notification_manager():
    """Get the global notification manager instance."""
    return notification_manager


if __name__ == "__main__":
    # For testing purposes
    import time

    logging.basicConfig(level=logging.INFO)

    # Test the function manually
    asyncio.run(check_and_send_due_reminders())