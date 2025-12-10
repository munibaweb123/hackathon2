"""Reminder API endpoints - CRUD operations for task reminders."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..core.database import get_session
from ..core.auth import get_current_user, verify_user_access, AuthenticatedUser
from ..models.reminder import Reminder, ReminderStatus
from ..models.task import Task
from ..schemas.reminder import ReminderCreate, ReminderUpdate, ReminderResponse, ReminderListResponse

router = APIRouter()


@router.get("/{user_id}/reminders", response_model=ReminderListResponse)
async def list_reminders(
    user_id: str,
    status_filter: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReminderListResponse:
    """
    List all reminders for a user with optional filtering.

    - **status**: Filter by 'pending', 'sent', or 'cancelled'
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Build query
    statement = select(Reminder).where(Reminder.user_id == user_id)

    # Apply status filter
    if status_filter:
        try:
            status_enum = ReminderStatus(status_filter)
            statement = statement.where(Reminder.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}. Valid values are: pending, sent, cancelled"
            )

    # Execute query
    reminders = session.exec(statement).all()

    # Get total count
    total = len(reminders)

    return ReminderListResponse(
        reminders=[ReminderResponse.model_validate(reminder) for reminder in reminders],
        total=total,
        page=1,
        page_size=len(reminders),
    )


@router.post("/{user_id}/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    user_id: str,
    reminder_data: ReminderCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReminderResponse:
    """
    Create a new reminder for a task.

    - **task_id**: The ID of the task to create a reminder for
    - **reminder_time**: When to send the reminder
    - **reminder_type**: Type of reminder (email, push, etc.)
    - **message**: Optional custom message for the reminder
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Check if the task belongs to the user
    task_statement = select(Task).where(Task.id == reminder_data.task_id, Task.user_id == user_id)
    task = session.exec(task_statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user",
        )

    # Check if a reminder already exists for this task at this time
    existing_reminder_statement = select(Reminder).where(
        Reminder.task_id == reminder_data.task_id,
        Reminder.reminder_time == reminder_data.reminder_time,
        Reminder.status == ReminderStatus.PENDING
    )
    existing_reminder = session.exec(existing_reminder_statement).first()

    if existing_reminder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A reminder already exists for this task at the specified time",
        )

    # Create reminder
    reminder = Reminder(
        task_id=reminder_data.task_id,
        user_id=user_id,
        reminder_time=reminder_data.reminder_time,
        reminder_type=reminder_data.reminder_type,
        message=reminder_data.message,
    )

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return ReminderResponse.model_validate(reminder)


@router.get("/{user_id}/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    user_id: str,
    reminder_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReminderResponse:
    """Get a specific reminder by ID."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get reminder
    statement = select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    reminder = session.exec(statement).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    return ReminderResponse.model_validate(reminder)


@router.put("/{user_id}/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    user_id: str,
    reminder_id: str,
    reminder_data: ReminderUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReminderResponse:
    """
    Update an existing reminder.

    Only provided fields will be updated.
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get reminder
    statement = select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    reminder = session.exec(statement).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    # Update only provided fields
    update_data = reminder_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "reminder_type" and value is not None:
            from ..models.reminder import ReminderType
            setattr(reminder, key, ReminderType(value))
        elif key == "status" and value is not None:
            from ..models.reminder import ReminderStatus
            setattr(reminder, key, ReminderStatus(value))
        else:
            setattr(reminder, key, value)

    reminder.updated_at = datetime.utcnow()

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return ReminderResponse.model_validate(reminder)


@router.delete("/{user_id}/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    user_id: str,
    reminder_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a reminder."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get reminder
    statement = select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    reminder = session.exec(statement).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    session.delete(reminder)
    session.commit()


@router.patch("/{user_id}/reminders/{reminder_id}/cancel", response_model=ReminderResponse)
async def cancel_reminder(
    user_id: str,
    reminder_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReminderResponse:
    """Cancel a reminder by setting its status to cancelled."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get reminder
    statement = select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    reminder = session.exec(statement).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    # Update status to cancelled
    reminder.status = ReminderStatus.CANCELLED
    reminder.updated_at = datetime.utcnow()

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return ReminderResponse.model_validate(reminder)