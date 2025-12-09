"""Input prompts for the Todo application."""

from typing import Optional

from ..models import Priority, RecurrenceFrequency, RecurrencePattern, ReminderOffset
from ..services.validators import (
    ValidationError,
    validate_categories,
    validate_description,
    validate_due_date,
    validate_priority,
    validate_recurrence,
    validate_task_id,
    validate_time,
    validate_title,
)
from .console import Console


class Prompts:
    """
    Input prompts with validation for the Todo application.

    All prompts handle validation and retry on invalid input.
    """

    def __init__(self, console: Console):
        """
        Initialize prompts with a console instance.

        Args:
            console: The console to use for input/output.
        """
        self._console = console

    def prompt_title(self, current: Optional[str] = None) -> str:
        """
        Prompt for a task title.

        Args:
            current: Current value to show (for updates). If provided, empty input keeps current.

        Returns:
            The validated title.
        """
        hint = f" (current: {current})" if current else ""
        prompt = f"Title{hint}: "

        while True:
            value = self._console.input(prompt).strip()

            # Allow keeping current value on update
            if not value and current:
                return current

            try:
                return validate_title(value)
            except ValidationError as e:
                self._console.error(str(e))

    def prompt_description(self, current: Optional[str] = None) -> str:
        """
        Prompt for a task description (optional).

        Args:
            current: Current value to show (for updates).

        Returns:
            The validated description (may be empty).
        """
        hint = f" (current: {current[:30]}...)" if current and len(current) > 30 else f" (current: {current})" if current else ""
        prompt = f"Description (optional){hint}: "

        while True:
            value = self._console.input(prompt)

            # Allow keeping current value on update (press Enter to keep)
            if not value and current is not None:
                return current

            try:
                return validate_description(value)
            except ValidationError as e:
                self._console.error(str(e))

    def prompt_due_date(self, current: Optional[str] = None) -> Optional[str]:
        """
        Prompt for a due date (optional).

        Args:
            current: Current value to show (for updates).

        Returns:
            The validated due date or None.
        """
        hint = f" (current: {current})" if current else ""
        prompt = f"Due date (YYYY-MM-DD, optional){hint}: "

        while True:
            value = self._console.input(prompt).strip()

            # Allow keeping current value on update
            if not value and current is not None:
                return current

            try:
                return validate_due_date(value)
            except ValidationError as e:
                self._console.error(str(e))

    def prompt_due_time(self, current: Optional[str] = None) -> Optional[str]:
        """
        Prompt for a due time (optional).

        Accepts flexible formats like "2:30pm", "14:30", "2:30 PM".

        Args:
            current: Current value to show (for updates).

        Returns:
            The validated due time in HH:MM:SS format, or None.
        """
        hint = f" (current: {current})" if current else ""
        prompt = f"Due time (e.g., 2:30pm or 14:30, optional){hint}: "

        while True:
            value = self._console.input(prompt).strip()

            # Allow keeping current value on update
            if not value and current is not None:
                return current

            # Empty input means no time
            if not value:
                return None

            try:
                return validate_time(value)
            except ValidationError as e:
                self._console.error(str(e))

    def prompt_priority(self, current: Optional[Priority] = None) -> Priority:
        """
        Prompt for a task priority.

        Args:
            current: Current value to show (for updates).

        Returns:
            The validated Priority enum value.
        """
        current_str = current.value if current else None
        hint = f" (current: {current_str})" if current_str else ""
        prompt = f"Priority (high/medium/low){hint}: "

        while True:
            value = self._console.input(prompt).strip()

            # Allow keeping current value on update
            if not value and current:
                return current

            # Default to medium if empty on new task
            if not value:
                return Priority.MEDIUM

            try:
                return validate_priority(value)
            except ValidationError as e:
                self._console.error(str(e))

    def prompt_categories(self, current: Optional[list[str]] = None) -> list[str]:
        """
        Prompt for task categories (comma-separated).

        Args:
            current: Current categories to show (for updates).

        Returns:
            A list of validated category names.
        """
        current_str = ", ".join(current) if current else None
        hint = f" (current: {current_str})" if current_str else ""
        prompt = f"Categories (comma-separated, optional){hint}: "

        value = self._console.input(prompt)

        # Allow keeping current value on update
        if not value and current is not None:
            return current

        return validate_categories(value)

    def prompt_task_id(self, action: str = "select") -> int:
        """
        Prompt for a task ID.

        Args:
            action: The action being performed (for prompt text).

        Returns:
            The validated task ID.
        """
        prompt = f"Enter task ID to {action}: "

        while True:
            value = self._console.input(prompt).strip()

            try:
                return validate_task_id(value)
            except ValidationError as e:
                self._console.error(str(e))

    def prompt_confirmation(self, message: str, default: bool = False) -> bool:
        """
        Prompt for confirmation.

        Args:
            message: The confirmation message.
            default: Default value if user just presses Enter.

        Returns:
            True if confirmed, False otherwise.
        """
        return self._console.confirm(message, default)

    def prompt_search_keyword(self) -> str:
        """
        Prompt for a search keyword.

        Returns:
            The search keyword (may be empty to cancel).
        """
        return self._console.input("Enter search keyword: ").strip()

    def prompt_update_field(self) -> Optional[str]:
        """
        Prompt for which field to update.

        Returns:
            The field name or None to cancel.
        """
        self._console.print("\nWhich field would you like to update?")
        self._console.print("  1. Title")
        self._console.print("  2. Description")
        self._console.print("  3. Due date")
        self._console.print("  4. Priority")
        self._console.print("  5. Categories")
        self._console.print("  6. All fields")
        self._console.print("  0. Cancel")
        self._console.blank()

        choice = self._console.input("Enter choice: ").strip()

        field_map = {
            "1": "title",
            "2": "description",
            "3": "due_date",
            "4": "priority",
            "5": "categories",
            "6": "all",
            "0": None,
        }

        return field_map.get(choice, None)

    def prompt_filter_choice(self) -> Optional[str]:
        """
        Prompt for filter criteria.

        Returns:
            The filter type or None to cancel.
        """
        self._console.print("\nFilter by:")
        self._console.print("  1. Status (complete/incomplete)")
        self._console.print("  2. Priority (high/medium/low)")
        self._console.print("  3. Category")
        self._console.print("  4. Due date range")
        self._console.print("  5. Recurring tasks only")
        self._console.print("  0. Cancel")
        self._console.blank()

        choice = self._console.input("Enter choice: ").strip()

        filter_map = {
            "1": "status",
            "2": "priority",
            "3": "category",
            "4": "date_range",
            "5": "recurrence",
            "0": None,
        }

        return filter_map.get(choice, None)

    def prompt_sort_choice(self) -> Optional[str]:
        """
        Prompt for sort criteria.

        Returns:
            The sort field or None to cancel.
        """
        self._console.print("\nSort by:")
        self._console.print("  1. Due date")
        self._console.print("  2. Priority")
        self._console.print("  3. Title")
        self._console.print("  4. Created date")
        self._console.print("  0. Cancel")
        self._console.blank()

        choice = self._console.input("Enter choice: ").strip()

        sort_map = {
            "1": "due_date",
            "2": "priority",
            "3": "title",
            "4": "created_at",
            "0": None,
        }

        return sort_map.get(choice, None)

    def prompt_date_range(self) -> tuple[Optional[str], Optional[str]]:
        """
        Prompt for a date range.

        Returns:
            A tuple of (start_date, end_date), either may be None.
        """
        self._console.info("Leave empty to skip that bound")

        start = self._console.input("Start date (YYYY-MM-DD): ").strip()
        end = self._console.input("End date (YYYY-MM-DD): ").strip()

        try:
            start = validate_due_date(start)
        except ValidationError:
            start = None

        try:
            end = validate_due_date(end)
        except ValidationError:
            end = None

        return start, end

    def prompt_recurrence(self) -> Optional[RecurrencePattern]:
        """
        Prompt for a recurrence pattern.

        Returns:
            A RecurrencePattern if user wants recurrence, None otherwise.
        """
        self._console.print("\nMake this a recurring task?")
        self._console.print("  1. No (one-time task)")
        self._console.print("  2. Daily")
        self._console.print("  3. Weekly")
        self._console.print("  4. Monthly")
        self._console.print("  5. Custom interval")
        self._console.blank()

        choice = self._console.input("Enter choice (default 1): ").strip()

        if choice in ("", "1"):
            return None

        if choice == "2":
            # Daily recurrence
            interval = self._prompt_interval("days")
            end_date = self._prompt_end_date()
            return validate_recurrence("daily", interval=interval, end_date=end_date)

        elif choice == "3":
            # Weekly recurrence
            interval = self._prompt_interval("weeks")
            days = self._prompt_days_of_week()
            end_date = self._prompt_end_date()
            return validate_recurrence(
                "weekly",
                interval=interval,
                day_of_week=days or None,
                end_date=end_date,
            )

        elif choice == "4":
            # Monthly recurrence
            interval = self._prompt_interval("months")
            day_of_month = self._prompt_day_of_month()
            end_date = self._prompt_end_date()
            return validate_recurrence(
                "monthly",
                interval=interval,
                day_of_month=day_of_month,
                end_date=end_date,
            )

        elif choice == "5":
            # Custom interval
            interval = self._prompt_interval("days")
            end_date = self._prompt_end_date()
            return validate_recurrence("custom", interval=interval, end_date=end_date)

        else:
            self._console.error("Invalid choice. No recurrence set.")
            return None

    def _prompt_interval(self, unit: str) -> int:
        """Prompt for recurrence interval."""
        while True:
            value = self._console.input(f"Repeat every N {unit} (default 1): ").strip()
            if not value:
                return 1
            try:
                interval = int(value)
                if interval < 1:
                    self._console.error("Interval must be at least 1.")
                    continue
                return interval
            except ValueError:
                self._console.error("Please enter a number.")

    def _prompt_days_of_week(self) -> list[int]:
        """Prompt for days of week selection."""
        self._console.print("\nSelect days of week (comma-separated):")
        self._console.print("  0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun")
        self._console.print("  Example: 0,2,4 for Mon, Wed, Fri")
        self._console.print("  Leave empty to repeat on the same weekday")

        value = self._console.input("Days: ").strip()
        if not value:
            return []

        days = []
        for part in value.split(","):
            try:
                day = int(part.strip())
                if 0 <= day <= 6 and day not in days:
                    days.append(day)
            except ValueError:
                pass

        return sorted(days)

    def _prompt_day_of_month(self) -> Optional[int]:
        """Prompt for day of month."""
        value = self._console.input("Day of month (1-31, or empty for same day): ").strip()
        if not value:
            return None
        try:
            day = int(value)
            if 1 <= day <= 31:
                return day
            self._console.error("Day must be 1-31.")
        except ValueError:
            self._console.error("Please enter a number.")
        return None

    def _prompt_end_date(self) -> Optional[str]:
        """Prompt for recurrence end date."""
        value = self._console.input("End date (YYYY-MM-DD, or empty for no end): ").strip()
        if not value:
            return None
        try:
            return validate_due_date(value)
        except ValidationError as e:
            self._console.error(str(e))
            return None

    def prompt_reminder(self) -> Optional[tuple[ReminderOffset, Optional[int]]]:
        """
        Prompt for a reminder setting.

        Returns:
            Tuple of (ReminderOffset, custom_minutes) or None if no reminder.
        """
        self._console.print("\nSet a reminder?")
        self._console.print("  1. No reminder")
        self._console.print("  2. At due time")
        self._console.print("  3. 15 minutes before")
        self._console.print("  4. 30 minutes before")
        self._console.print("  5. 1 hour before")
        self._console.print("  6. 2 hours before")
        self._console.print("  7. 1 day before")
        self._console.print("  8. Custom time before")
        self._console.blank()

        choice = self._console.input("Enter choice (default 1): ").strip()

        if choice in ("", "1"):
            return None

        offset_map = {
            "2": ReminderOffset.AT_TIME,
            "3": ReminderOffset.MINUTES_15,
            "4": ReminderOffset.MINUTES_30,
            "5": ReminderOffset.HOUR_1,
            "6": ReminderOffset.HOURS_2,
            "7": ReminderOffset.DAY_1,
        }

        if choice in offset_map:
            return (offset_map[choice], None)

        if choice == "8":
            # Custom time
            custom_minutes = self._prompt_custom_reminder_minutes()
            if custom_minutes:
                return (ReminderOffset.CUSTOM, custom_minutes)
            return None

        self._console.error("Invalid choice. No reminder set.")
        return None

    def _prompt_custom_reminder_minutes(self) -> Optional[int]:
        """Prompt for custom reminder minutes."""
        while True:
            value = self._console.input("Minutes before due time: ").strip()
            if not value:
                return None
            try:
                minutes = int(value)
                if minutes < 1:
                    self._console.error("Minutes must be at least 1.")
                    continue
                if minutes > 10080:  # Max 1 week
                    self._console.error("Maximum is 10080 minutes (1 week).")
                    continue
                return minutes
            except ValueError:
                self._console.error("Please enter a number.")

    def prompt_series_scope(self, action: str = "edit") -> Optional[str]:
        """
        Prompt for whether to apply action to single instance or entire series.

        Args:
            action: The action being performed ("edit" or "delete").

        Returns:
            "single" for this instance only, "series" for all future, or None to cancel.
        """
        self._console.print(f"\nThis is a recurring task. How would you like to {action}?")
        self._console.print("  1. This instance only")
        self._console.print("  2. All future instances")
        self._console.print("  0. Cancel")
        self._console.blank()

        choice = self._console.input("Enter choice: ").strip()

        scope_map = {
            "1": "single",
            "2": "series",
            "0": None,
        }

        return scope_map.get(choice, None)

    def prompt_stop_recurrence(self) -> bool:
        """
        Prompt whether to stop recurrence for a task.

        Returns:
            True to stop recurrence, False to keep it.
        """
        return self._console.confirm("Stop recurrence for this task?")
