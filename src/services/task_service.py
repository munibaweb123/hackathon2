"""Task service for managing todo operations."""

from src.models.task import Task


class TaskService:
    """Service class for CRUD operations on tasks.

    Provides in-memory storage for tasks using a dictionary
    with auto-incrementing IDs.
    """

    def __init__(self) -> None:
        """Initialize the task service with empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Add a new task with auto-generated ID.

        Args:
            title: The task title (required, non-empty).
            description: Optional task description.

        Returns:
            The created Task with assigned ID.

        Raises:
            ValueError: If title is empty.
        """
        task = Task(title=title, description=description)
        task.id = self._next_id
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: The task ID to look up.

        Returns:
            The Task if found, None otherwise.
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks as a list.

        Returns:
            List of all tasks in storage.
        """
        return list(self._tasks.values())

    def update_task(
        self, task_id: int, title: str | None = None, description: str | None = None
    ) -> bool:
        """Update a task's title and/or description.

        Args:
            task_id: The task ID to update.
            title: New title (None to keep current).
            description: New description (None to keep current).

        Returns:
            True if task was updated, False if not found.
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = title

        if description is not None:
            task.description = description

        return True

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task ID to delete.

        Returns:
            True if task was deleted, False if not found.
        """
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as complete.

        Args:
            task_id: The task ID to mark complete.

        Returns:
            True if task was marked complete, False if not found.
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.mark_complete()
        return True

    def mark_incomplete(self, task_id: int) -> bool:
        """Mark a task as incomplete.

        Args:
            task_id: The task ID to mark incomplete.

        Returns:
            True if task was marked incomplete, False if not found.
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.mark_incomplete()
        return True
