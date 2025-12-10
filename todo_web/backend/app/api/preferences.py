"""User preference API endpoints - CRUD operations for user settings."""

from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import json

from ..core.database import get_session
from ..core.auth import get_current_user, verify_user_access, AuthenticatedUser
from ..models.preference import UserPreference
from ..schemas.preference import UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse

router = APIRouter()


@router.get("/{user_id}/preferences", response_model=UserPreferenceResponse)
async def get_user_preferences(
    user_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserPreferenceResponse:
    """Get user preferences. Creates default preferences if they don't exist."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get existing preferences or create default
    statement = select(UserPreference).where(UserPreference.user_id == user_id)
    user_pref = session.exec(statement).first()

    if not user_pref:
        # Create default preferences for the user
        user_pref = UserPreference(user_id=user_id)
        session.add(user_pref)
        session.commit()
        session.refresh(user_pref)

    return UserPreferenceResponse.model_validate(user_pref)


@router.post("/{user_id}/preferences", response_model=UserPreferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_user_preferences(
    user_id: str,
    preferences_data: UserPreferenceCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserPreferenceResponse:
    """Create user preferences. If preferences already exist, update them instead."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Check if preferences already exist
    statement = select(UserPreference).where(UserPreference.user_id == user_id)
    existing_pref = session.exec(statement).first()

    if existing_pref:
        # If preferences exist, update them instead of creating new ones
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User preferences already exist. Use PUT to update them.",
        )

    # Validate time format if provided
    if preferences_data.work_hours_start and not UserPreferenceResponse.validate_time_format(preferences_data.work_hours_start):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_hours_start must be in HH:MM format (24-hour)",
        )

    if preferences_data.work_hours_end and not UserPreferenceResponse.validate_time_format(preferences_data.work_hours_end):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_hours_end must be in HH:MM format (24-hour)",
        )

    # Convert custom_settings dict to JSON string
    custom_settings_json = None
    if preferences_data.custom_settings:
        custom_settings_json = json.dumps(preferences_data.custom_settings)

    # Create preferences
    user_pref = UserPreference(
        user_id=user_id,
        theme=preferences_data.theme,
        language=preferences_data.language,
        task_notifications=preferences_data.task_notifications,
        reminder_notifications=preferences_data.reminder_notifications,
        email_notifications=preferences_data.email_notifications,
        default_view=preferences_data.default_view,
        show_completed_tasks=preferences_data.show_completed_tasks,
        group_by=preferences_data.group_by,
        auto_archive_completed=preferences_data.auto_archive_completed,
        auto_snooze_time=preferences_data.auto_snooze_time,
        work_hours_start=preferences_data.work_hours_start,
        work_hours_end=preferences_data.work_hours_end,
        custom_settings=custom_settings_json,
    )

    session.add(user_pref)
    session.commit()
    session.refresh(user_pref)

    return UserPreferenceResponse.model_validate(user_pref)


@router.put("/{user_id}/preferences", response_model=UserPreferenceResponse)
async def update_user_preferences(
    user_id: str,
    preferences_data: UserPreferenceUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserPreferenceResponse:
    """Update user preferences. Creates default preferences if they don't exist."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get existing preferences or create default
    statement = select(UserPreference).where(UserPreference.user_id == user_id)
    user_pref = session.exec(statement).first()

    if not user_pref:
        # Create default preferences for the user
        user_pref = UserPreference(user_id=user_id)
        session.add(user_pref)
        session.commit()
        session.refresh(user_pref)

    # Validate time format if provided
    if preferences_data.work_hours_start and not UserPreferenceResponse.validate_time_format(preferences_data.work_hours_start):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_hours_start must be in HH:MM format (24-hour)",
        )

    if preferences_data.work_hours_end and not UserPreferenceResponse.validate_time_format(preferences_data.work_hours_end):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_hours_end must be in HH:MM format (24-hour)",
        )

    # Update only provided fields
    update_data = preferences_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "custom_settings" and value is not None:
            # Convert dict to JSON string for custom settings
            setattr(user_pref, key, json.dumps(value))
        elif value is not None:
            setattr(user_pref, key, value)

    user_pref.updated_at = datetime.utcnow()

    session.add(user_pref)
    session.commit()
    session.refresh(user_pref)

    return UserPreferenceResponse.model_validate(user_pref)


@router.patch("/{user_id}/preferences", response_model=UserPreferenceResponse)
async def patch_user_preferences(
    user_id: str,
    preferences_data: UserPreferenceUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserPreferenceResponse:
    """Partially update user preferences."""
    # Verify user access
    verify_user_access(user_id, current_user)

    # Get existing preferences
    statement = select(UserPreference).where(UserPreference.user_id == user_id)
    user_pref = session.exec(statement).first()

    if not user_pref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )

    # Validate time format if provided
    if preferences_data.work_hours_start and not UserPreferenceResponse.validate_time_format(preferences_data.work_hours_start):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_hours_start must be in HH:MM format (24-hour)",
        )

    if preferences_data.work_hours_end and not UserPreferenceResponse.validate_time_format(preferences_data.work_hours_end):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_hours_end must be in HH:MM format (24-hour)",
        )

    # Update only provided fields
    update_data = preferences_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "custom_settings" and value is not None:
            # Convert dict to JSON string for custom settings
            setattr(user_pref, key, json.dumps(value))
        elif value is not None:
            setattr(user_pref, key, value)

    user_pref.updated_at = datetime.utcnow()

    session.add(user_pref)
    session.commit()
    session.refresh(user_pref)

    return UserPreferenceResponse.model_validate(user_pref)