"""Preferences service for managing user settings."""

from typing import Optional

from ..models import ReminderOffset
from ..storage.preferences import PreferencesStore, UserPreferences


class PreferencesService:
    """
    Service layer for user preferences.

    Provides business logic for getting and updating user settings,
    with type-safe access to preference values.
    """

    def __init__(self, store: Optional[PreferencesStore] = None):
        """
        Initialize the preferences service.

        Args:
            store: The preferences store to use. Defaults to a new PreferencesStore.
        """
        self._store = store if store is not None else PreferencesStore()

    def get_preferences(self) -> UserPreferences:
        """
        Get current user preferences.

        Returns:
            Current UserPreferences.
        """
        return self._store.load()

    def update_preferences(
        self,
        default_reminder: Optional[str] = None,
        default_reminder_custom: Optional[int] = None,
        notifications_enabled: Optional[bool] = None,
    ) -> UserPreferences:
        """
        Update user preferences.

        Only non-None values will be updated.

        Args:
            default_reminder: ReminderOffset value string or None to clear.
            default_reminder_custom: Custom minutes for CUSTOM offset.
            notifications_enabled: Whether notifications are enabled.

        Returns:
            Updated UserPreferences.
        """
        updates = {}

        if default_reminder is not None:
            updates["default_reminder"] = default_reminder

        if default_reminder_custom is not None:
            updates["default_reminder_custom"] = default_reminder_custom

        if notifications_enabled is not None:
            updates["notifications_enabled"] = notifications_enabled

        if updates:
            return self._store.update(**updates)

        return self._store.load()

    def clear_default_reminder(self) -> UserPreferences:
        """
        Clear the default reminder setting.

        Returns:
            Updated UserPreferences.
        """
        return self._store.update(
            default_reminder=None,
            default_reminder_custom=None,
        )

    def get_default_reminder_offset(self) -> Optional[tuple[ReminderOffset, Optional[int]]]:
        """
        Get the default reminder as a typed tuple.

        Returns:
            Tuple of (ReminderOffset, custom_minutes) or None if not set.
        """
        prefs = self._store.load()

        if not prefs.default_reminder:
            return None

        try:
            offset = ReminderOffset(prefs.default_reminder)
            return (offset, prefs.default_reminder_custom)
        except ValueError:
            return None

    def set_default_reminder(
        self,
        offset: ReminderOffset,
        custom_minutes: Optional[int] = None,
    ) -> UserPreferences:
        """
        Set the default reminder.

        Args:
            offset: The ReminderOffset to use.
            custom_minutes: Custom minutes for CUSTOM offset.

        Returns:
            Updated UserPreferences.
        """
        return self._store.update(
            default_reminder=offset.value,
            default_reminder_custom=custom_minutes,
        )
