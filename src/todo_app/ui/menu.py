"""Main menu system for the Todo application."""

from typing import Optional

from ..models import Priority
from ..services.task_service import TaskService
from ..services.validators import ValidationError
from .console import Console
from .display import display_task_detail, display_tasks
from .prompts import Prompts


class Menu:
    """
    Main menu for the Todo application.

    Provides the main interaction loop and menu options.
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        service: Optional[TaskService] = None,
    ):
        """
        Initialize the menu.

        Args:
            console: The console to use. Defaults to a new Console.
            service: The task service to use. Defaults to a new TaskService.
        """
        self._console = console if console is not None else Console()
        self._service = service if service is not None else TaskService()
        self._prompts = Prompts(self._console)
        self._running = True

    def run(self) -> None:
        """Run the main menu loop."""
        self._console.header("=== Todo Application ===")

        while self._running:
            try:
                self._show_menu()
                choice = self._console.input("Enter choice: ").strip()
                self._handle_choice(choice)
            except KeyboardInterrupt:
                self._console.blank()
                self._handle_exit()

    def _show_menu(self) -> None:
        """Display the main menu options."""
        self._console.blank()
        self._console.print("1. Add new task")
        self._console.print("2. View all tasks")
        self._console.print("3. Update task")
        self._console.print("4. Delete task")
        self._console.print("5. Mark task complete/incomplete")
        self._console.print("6. Search tasks")
        self._console.print("7. Filter tasks")
        self._console.print("8. Sort tasks")
        self._console.print("9. Exit")
        self._console.blank()

    def _handle_choice(self, choice: str) -> None:
        """Handle a menu choice."""
        handlers = {
            "1": self._add_task_flow,
            "2": self._view_tasks_flow,
            "3": self._update_task_flow,
            "4": self._delete_task_flow,
            "5": self._toggle_status_flow,
            "6": self._search_tasks_flow,
            "7": self._filter_tasks_flow,
            "8": self._sort_tasks_flow,
            "9": self._handle_exit,
        }

        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            self._console.error("Invalid choice. Please enter a number 1-9.")

    def _handle_exit(self) -> None:
        """Handle exit request."""
        if self._prompts.prompt_confirmation("Are you sure you want to exit?"):
            self._console.success("Goodbye!")
            self._running = False

    # ========== User Story 1: Add Task ==========

    def _add_task_flow(self) -> None:
        """Handle adding a new task."""
        self._console.header("Add New Task")

        title = self._prompts.prompt_title()
        description = self._prompts.prompt_description()
        due_date = self._prompts.prompt_due_date()
        priority = self._prompts.prompt_priority()
        categories = self._prompts.prompt_categories()

        task = self._service.add_task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            categories=categories,
        )

        self._console.blank()
        self._console.success(f"Task #{task.id} created successfully!")
        display_task_detail(self._console, task)

    # ========== User Story 2: View Tasks ==========

    def _view_tasks_flow(self) -> None:
        """Handle viewing all tasks."""
        self._console.header("All Tasks")

        tasks = self._service.get_all_tasks()
        display_tasks(self._console, tasks)

    # ========== User Story 3: Toggle Status ==========

    def _toggle_status_flow(self) -> None:
        """Handle toggling task status."""
        self._console.header("Toggle Task Status")

        # Show current tasks
        tasks = self._service.get_all_tasks()
        if not tasks:
            self._console.info("No tasks available.")
            return

        display_tasks(self._console, tasks)

        # Get task ID
        task_id = self._prompts.prompt_task_id("toggle")

        # Get the task first to show what will happen
        task = self._service.get_task_by_id(task_id)
        if task is None:
            self._console.error(f"Task #{task_id} not found.")
            return

        new_status = "complete" if task.status.value == "incomplete" else "incomplete"

        if self._service.toggle_status(task_id):
            self._console.success(f"Task #{task_id} marked as {new_status}.")
        else:
            self._console.error(f"Failed to toggle task #{task_id}.")

    # ========== User Story 4: Update Task ==========

    def _update_task_flow(self) -> None:
        """Handle updating a task."""
        self._console.header("Update Task")

        # Show current tasks
        tasks = self._service.get_all_tasks()
        if not tasks:
            self._console.info("No tasks available.")
            return

        display_tasks(self._console, tasks)

        # Get task ID
        task_id = self._prompts.prompt_task_id("update")

        # Get the task
        task = self._service.get_task_by_id(task_id)
        if task is None:
            self._console.error(f"Task #{task_id} not found.")
            return

        # Show current values
        display_task_detail(self._console, task)

        # Get field to update
        field = self._prompts.prompt_update_field()
        if field is None:
            self._console.info("Update cancelled.")
            return

        # Collect updates based on field choice
        updates = {}

        if field in ("title", "all"):
            updates["title"] = self._prompts.prompt_title(task.title)

        if field in ("description", "all"):
            updates["description"] = self._prompts.prompt_description(task.description)

        if field in ("due_date", "all"):
            updates["due_date"] = self._prompts.prompt_due_date(task.due_date)

        if field in ("priority", "all"):
            updates["priority"] = self._prompts.prompt_priority(task.priority)

        if field in ("categories", "all"):
            updates["categories"] = self._prompts.prompt_categories(task.categories)

        # Apply updates
        if self._service.update_task(task_id, **updates):
            self._console.success(f"Task #{task_id} updated successfully!")
            updated_task = self._service.get_task_by_id(task_id)
            if updated_task:
                display_task_detail(self._console, updated_task)
        else:
            self._console.error(f"Failed to update task #{task_id}.")

    # ========== User Story 5: Delete Task ==========

    def _delete_task_flow(self) -> None:
        """Handle deleting a task."""
        self._console.header("Delete Task")

        # Show current tasks
        tasks = self._service.get_all_tasks()
        if not tasks:
            self._console.info("No tasks available.")
            return

        display_tasks(self._console, tasks)

        # Get task ID
        task_id = self._prompts.prompt_task_id("delete")

        # Get the task to show what will be deleted
        task = self._service.get_task_by_id(task_id)
        if task is None:
            self._console.error(f"Task #{task_id} not found.")
            return

        # Confirm deletion
        if not self._prompts.prompt_confirmation(f"Delete task '{task.title}'?"):
            self._console.info("Deletion cancelled.")
            return

        if self._service.delete_task(task_id):
            self._console.success(f"Task #{task_id} deleted successfully!")
        else:
            self._console.error(f"Failed to delete task #{task_id}.")

    # ========== User Story 6: Search Tasks ==========

    def _search_tasks_flow(self) -> None:
        """Handle searching tasks."""
        self._console.header("Search Tasks")

        keyword = self._prompts.prompt_search_keyword()
        if not keyword:
            self._console.info("Search cancelled.")
            return

        # Import search function
        from ..services.search import search_tasks

        tasks = self._service.get_all_tasks()
        results = search_tasks(tasks, keyword)

        display_tasks(self._console, results, f"Search Results for '{keyword}'")

    # ========== User Story 7: Filter Tasks ==========

    def _filter_tasks_flow(self) -> None:
        """Handle filtering tasks."""
        self._console.header("Filter Tasks")

        filter_type = self._prompts.prompt_filter_choice()
        if filter_type is None:
            self._console.info("Filter cancelled.")
            return

        from ..models import Status
        from ..services.filter import (
            combine_filters,
            filter_by_category,
            filter_by_date_range,
            filter_by_priority,
            filter_by_status,
        )

        tasks = self._service.get_all_tasks()

        if filter_type == "status":
            status_str = self._console.input("Status (complete/incomplete): ").strip().lower()
            if status_str in ("complete", "c"):
                results = filter_by_status(tasks, Status.COMPLETE)
                title = "Complete Tasks"
            else:
                results = filter_by_status(tasks, Status.INCOMPLETE)
                title = "Incomplete Tasks"

        elif filter_type == "priority":
            priority_str = self._console.input("Priority (high/medium/low): ").strip().lower()
            try:
                from ..services.validators import validate_priority
                priority = validate_priority(priority_str)
                results = filter_by_priority(tasks, priority)
                title = f"{priority.value.capitalize()} Priority Tasks"
            except ValidationError as e:
                self._console.error(str(e))
                return

        elif filter_type == "category":
            category = self._console.input("Category: ").strip().lower()
            if not category:
                self._console.info("Filter cancelled.")
                return
            results = filter_by_category(tasks, category)
            title = f"Tasks in '{category}'"

        elif filter_type == "date_range":
            start_date, end_date = self._prompts.prompt_date_range()
            results = filter_by_date_range(tasks, start_date, end_date)
            title = "Tasks by Date Range"

        else:
            self._console.error("Invalid filter type.")
            return

        display_tasks(self._console, results, title)

    # ========== User Story 8: Sort Tasks ==========

    def _sort_tasks_flow(self) -> None:
        """Handle sorting tasks."""
        self._console.header("Sort Tasks")

        sort_field = self._prompts.prompt_sort_choice()
        if sort_field is None:
            self._console.info("Sort cancelled.")
            return

        from ..services.sort import (
            sort_by_created_at,
            sort_by_due_date,
            sort_by_priority,
            sort_by_title,
        )

        tasks = self._service.get_all_tasks()

        if sort_field == "due_date":
            asc = self._console.input("Ascending? (y/n, default y): ").strip().lower()
            ascending = asc != "n"
            results = sort_by_due_date(tasks, ascending)
            title = "Tasks by Due Date"

        elif sort_field == "priority":
            results = sort_by_priority(tasks)
            title = "Tasks by Priority"

        elif sort_field == "title":
            results = sort_by_title(tasks)
            title = "Tasks by Title"

        elif sort_field == "created_at":
            results = sort_by_created_at(tasks)
            title = "Tasks by Created Date"

        else:
            self._console.error("Invalid sort field.")
            return

        display_tasks(self._console, results, title)
