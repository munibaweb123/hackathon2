"""Input prompts for the Todo application."""

from typing import Optional

from ..models import Priority
from ..services.validators import (
    ValidationError,
    validate_categories,
    validate_description,
    validate_due_date,
    validate_priority,
    validate_task_id,
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
        self._console.print("  0. Cancel")
        self._console.blank()

        choice = self._console.input("Enter choice: ").strip()

        filter_map = {
            "1": "status",
            "2": "priority",
            "3": "category",
            "4": "date_range",
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
