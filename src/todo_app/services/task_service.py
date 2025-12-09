"""Task service layer for the Todo application."""

from typing import Optional

from ..models import Priority, Status, Task
from ..storage import JsonStore


class TaskService:
    """
    Service layer for task operations.

    Provides business logic for CRUD operations on tasks,
    delegating storage to JsonStore.
    """

    def __init__(self, store: Optional[JsonStore] = None):
        """
        Initialize the task service.

        Args:
            store: The JSON store to use. Defaults to a new JsonStore with default file.
        """
        self._store = store if store is not None else JsonStore()

    def add_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        categories: Optional[list[str]] = None,
    ) -> Task:
        """
        Create and add a new task.

        Args:
            title: The task title.
            description: Optional description.
            due_date: Optional due date in YYYY-MM-DD format.
            priority: Task priority (defaults to MEDIUM).
            categories: Optional list of category tags.

        Returns:
            The created task with assigned ID.
        """
        task = Task(
            id=0,  # Will be assigned by store
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            categories=categories or [],
            status=Status.INCOMPLETE,
        )
        return self._store.add_task(task)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: The task ID.

        Returns:
            The task if found, None otherwise.
        """
        return self._store.get_task(task_id)

    def get_all_tasks(self) -> list[Task]:
        """
        Get all tasks.

        Returns:
            A list of all tasks sorted by ID.
        """
        return self._store.get_all_tasks()

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[Priority] = None,
        categories: Optional[list[str]] = None,
    ) -> bool:
        """
        Update a task's properties.

        Only non-None values will be updated.

        Args:
            task_id: The task ID.
            title: New title (if provided).
            description: New description (if provided).
            due_date: New due date (if provided). Use empty string to clear.
            priority: New priority (if provided).
            categories: New categories (if provided).

        Returns:
            True if updated, False if task not found.
        """
        task = self._store.get_task(task_id)
        if task is None:
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date if due_date else None
        if priority is not None:
            task.priority = priority
        if categories is not None:
            task.categories = categories

        return self._store.update_task(task)

    def toggle_status(self, task_id: int) -> bool:
        """
        Toggle a task's completion status.

        Args:
            task_id: The task ID.

        Returns:
            True if toggled, False if task not found.
        """
        task = self._store.get_task(task_id)
        if task is None:
            return False

        task.toggle_status()
        return self._store.update_task(task)

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task.

        Args:
            task_id: The task ID.

        Returns:
            True if deleted, False if task not found.
        """
        return self._store.delete_task(task_id)

    def count(self) -> int:
        """Get the number of tasks."""
        return self._store.count()
