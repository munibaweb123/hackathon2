"""JSON file storage for the Todo application."""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models import Priority, Status, Task


class JsonStore:
    """
    JSON file-based storage for tasks with atomic writes and corruption recovery.

    Features:
        - Atomic writes using temp file + rename
        - Automatic backup of corrupted files
        - max_id tracking to ensure unique, never-reused IDs
        - Automatic file creation if missing
    """

    DEFAULT_FILE = "tasks.json"
    SCHEMA_VERSION = "1.1"  # Updated for recurring tasks and reminders

    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize the JSON store.

        Args:
            file_path: Path to the JSON file. Defaults to tasks.json in current directory.
        """
        self.file_path = Path(file_path) if file_path else Path(self.DEFAULT_FILE)
        self._tasks: dict[int, Task] = {}
        self._max_id: int = 0
        self._load()

    def _load(self) -> None:
        """Load tasks from the JSON file."""
        if not self.file_path.exists():
            self._tasks = {}
            self._max_id = 0
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load metadata
            metadata = data.get("metadata", {})
            self._max_id = metadata.get("max_id", 0)

            # Load tasks
            self._tasks = {}
            for task_data in data.get("tasks", []):
                try:
                    task = Task.from_dict(task_data)
                    self._tasks[task.id] = task
                    # Ensure max_id is at least as high as the highest task ID
                    if task.id > self._max_id:
                        self._max_id = task.id
                except (KeyError, ValueError) as e:
                    # Skip invalid tasks but log warning
                    print(f"Warning: Skipping invalid task data: {e}")

        except json.JSONDecodeError:
            # Corrupted JSON - backup and start fresh
            self._backup_corrupted_file()
            self._tasks = {}
            self._max_id = 0
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self._tasks = {}
            self._max_id = 0

    def _backup_corrupted_file(self) -> None:
        """Backup a corrupted JSON file before starting fresh."""
        if self.file_path.exists():
            backup_path = self.file_path.with_suffix(
                f".corrupted.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                shutil.copy2(self.file_path, backup_path)
                print(f"Warning: Corrupted file backed up to {backup_path}")
            except Exception as e:
                print(f"Warning: Could not backup corrupted file: {e}")

    def _save(self) -> None:
        """Save tasks to the JSON file using atomic write."""
        data = {
            "metadata": {
                "version": self.SCHEMA_VERSION,
                "max_id": self._max_id,
                "last_modified": datetime.now().isoformat(),
            },
            "tasks": [task.to_dict() for task in self._tasks.values()],
        }

        # Atomic write: write to temp file, then rename
        dir_path = self.file_path.parent
        if dir_path and not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Always use the same directory as the target file for atomic rename to work
        # This is critical for cross-device scenarios (e.g., WSL accessing Windows mounts)
        temp_dir = str(self.file_path.parent.resolve())
        fd, temp_path = tempfile.mkstemp(
            suffix=".tmp",
            prefix="tasks_",
            dir=temp_dir,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic rename
            os.replace(temp_path, self.file_path)
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def get_next_id(self) -> int:
        """Get the next available task ID (never reused)."""
        self._max_id += 1
        return self._max_id

    def add_task(self, task: Task) -> Task:
        """
        Add a new task to the store.

        Args:
            task: The task to add. If id is 0, a new ID will be assigned.

        Returns:
            The task with its assigned ID.
        """
        if task.id == 0:
            task.id = self.get_next_id()
        else:
            # Ensure max_id is at least as high as the task ID
            if task.id > self._max_id:
                self._max_id = task.id

        self._tasks[task.id] = task
        self._save()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The task if found, None otherwise.
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """
        Get all tasks.

        Returns:
            A list of all tasks sorted by ID.
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update_task(self, task: Task) -> bool:
        """
        Update an existing task.

        Args:
            task: The task with updated data.

        Returns:
            True if the task was updated, False if not found.
        """
        if task.id not in self._tasks:
            return False

        self._tasks[task.id] = task
        self._save()
        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if the task was deleted, False if not found.
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        self._save()
        return True

    def count(self) -> int:
        """Get the number of tasks in the store."""
        return len(self._tasks)

    def clear(self) -> None:
        """Remove all tasks from the store."""
        self._tasks = {}
        self._save()
