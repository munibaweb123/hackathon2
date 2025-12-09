"""User preferences storage for the Todo application."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Import will be available after models are set up
# For now, we use string values and convert later


@dataclass
class UserPreferences:
    """
    User settings stored in preferences.json.

    Attributes:
        default_reminder: Auto-add reminder to new tasks (offset value string)
        default_reminder_custom: Custom minutes if default is CUSTOM
        notifications_enabled: Whether to show notifications
    """
    default_reminder: Optional[str] = None
    default_reminder_custom: Optional[int] = None
    notifications_enabled: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "default_reminder": self.default_reminder,
            "default_reminder_custom": self.default_reminder_custom,
            "notifications_enabled": self.notifications_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """Create UserPreferences from a dictionary."""
        return cls(
            default_reminder=data.get("default_reminder"),
            default_reminder_custom=data.get("default_reminder_custom"),
            notifications_enabled=data.get("notifications_enabled", True),
        )


class PreferencesStore:
    """
    JSON file-based storage for user preferences.

    Features:
        - Auto-creates file if missing
        - Returns defaults if file doesn't exist
        - Atomic writes using temp file + rename
    """

    DEFAULT_FILE = "preferences.json"

    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize the preferences store.

        Args:
            file_path: Path to the preferences file. Defaults to preferences.json.
        """
        self.file_path = Path(file_path) if file_path else Path(self.DEFAULT_FILE)
        self._preferences: Optional[UserPreferences] = None

    def load(self) -> UserPreferences:
        """
        Load preferences from the JSON file.

        Returns:
            UserPreferences: Current preferences or defaults if file doesn't exist.
        """
        if self._preferences is not None:
            return self._preferences

        if not self.file_path.exists():
            self._preferences = UserPreferences()
            return self._preferences

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._preferences = UserPreferences.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted file - return defaults
            self._preferences = UserPreferences()

        return self._preferences

    def save(self, preferences: UserPreferences) -> None:
        """
        Save preferences to the JSON file.

        Args:
            preferences: The preferences to save.
        """
        self._preferences = preferences
        data = preferences.to_dict()

        # Atomic write
        temp_dir = str(self.file_path.parent.resolve())
        import tempfile
        import os

        fd, temp_path = tempfile.mkstemp(
            suffix=".tmp",
            prefix="prefs_",
            dir=temp_dir if temp_dir != "." else None,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.file_path)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def update(self, **kwargs) -> UserPreferences:
        """
        Update specific preference values.

        Args:
            **kwargs: Preference fields to update.

        Returns:
            UserPreferences: Updated preferences.
        """
        prefs = self.load()
        for key, value in kwargs.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        self.save(prefs)
        return prefs
