"""Unit tests for TaskService."""

import os
import tempfile

import pytest

from todo_app.models import Priority, Status, Task
from todo_app.services import TaskService
from todo_app.storage import JsonStore


@pytest.fixture
def temp_store():
    """Create a TaskService with a temporary file."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    store = JsonStore(path)
    service = TaskService(store)
    yield service
    if os.path.exists(path):
        os.unlink(path)


class TestTaskServiceAddTask:
    """Tests for TaskService.add_task."""

    def test_add_task_with_minimal_fields(self, temp_store):
        """Test adding a task with only title."""
        task = temp_store.add_task(title="Test Task")

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.due_date is None
        assert task.priority == Priority.MEDIUM
        assert task.categories == []
        assert task.status == Status.INCOMPLETE

    def test_add_task_with_all_fields(self, temp_store):
        """Test adding a task with all fields."""
        task = temp_store.add_task(
            title="Full Task",
            description="A complete task",
            due_date="2024-12-31",
            priority=Priority.HIGH,
            categories=["work", "urgent"],
        )

        assert task.id == 1
        assert task.title == "Full Task"
        assert task.description == "A complete task"
        assert task.due_date == "2024-12-31"
        assert task.priority == Priority.HIGH
        assert task.categories == ["work", "urgent"]
        assert task.status == Status.INCOMPLETE

    def test_add_multiple_tasks_increments_id(self, temp_store):
        """Test that IDs are incremented correctly."""
        task1 = temp_store.add_task(title="Task 1")
        task2 = temp_store.add_task(title="Task 2")
        task3 = temp_store.add_task(title="Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3


class TestTaskServiceGetTask:
    """Tests for TaskService.get_task_by_id."""

    def test_get_existing_task(self, temp_store):
        """Test getting an existing task."""
        temp_store.add_task(title="Test Task")

        task = temp_store.get_task_by_id(1)

        assert task is not None
        assert task.title == "Test Task"

    def test_get_nonexistent_task(self, temp_store):
        """Test getting a task that doesn't exist."""
        task = temp_store.get_task_by_id(999)

        assert task is None


class TestTaskServiceGetAllTasks:
    """Tests for TaskService.get_all_tasks."""

    def test_get_all_tasks_empty(self, temp_store):
        """Test getting all tasks when store is empty."""
        tasks = temp_store.get_all_tasks()

        assert tasks == []

    def test_get_all_tasks_with_tasks(self, temp_store):
        """Test getting all tasks."""
        temp_store.add_task(title="Task 1")
        temp_store.add_task(title="Task 2")
        temp_store.add_task(title="Task 3")

        tasks = temp_store.get_all_tasks()

        assert len(tasks) == 3
        assert [t.title for t in tasks] == ["Task 1", "Task 2", "Task 3"]


class TestTaskServiceUpdateTask:
    """Tests for TaskService.update_task."""

    def test_update_single_field(self, temp_store):
        """Test updating a single field."""
        temp_store.add_task(title="Original Title")

        result = temp_store.update_task(1, title="Updated Title")

        assert result is True
        task = temp_store.get_task_by_id(1)
        assert task.title == "Updated Title"

    def test_update_multiple_fields(self, temp_store):
        """Test updating multiple fields."""
        temp_store.add_task(title="Original", priority=Priority.LOW)

        result = temp_store.update_task(
            1,
            title="Updated",
            description="New description",
            priority=Priority.HIGH,
        )

        assert result is True
        task = temp_store.get_task_by_id(1)
        assert task.title == "Updated"
        assert task.description == "New description"
        assert task.priority == Priority.HIGH

    def test_update_preserves_unchanged_fields(self, temp_store):
        """Test that unchanged fields are preserved."""
        temp_store.add_task(
            title="Original",
            description="Original desc",
            priority=Priority.HIGH,
        )

        temp_store.update_task(1, title="New Title")

        task = temp_store.get_task_by_id(1)
        assert task.title == "New Title"
        assert task.description == "Original desc"
        assert task.priority == Priority.HIGH

    def test_update_nonexistent_task(self, temp_store):
        """Test updating a task that doesn't exist."""
        result = temp_store.update_task(999, title="New Title")

        assert result is False


class TestTaskServiceToggleStatus:
    """Tests for TaskService.toggle_status."""

    def test_toggle_incomplete_to_complete(self, temp_store):
        """Test toggling from incomplete to complete."""
        temp_store.add_task(title="Test Task")

        result = temp_store.toggle_status(1)

        assert result is True
        task = temp_store.get_task_by_id(1)
        assert task.status == Status.COMPLETE

    def test_toggle_complete_to_incomplete(self, temp_store):
        """Test toggling from complete to incomplete."""
        temp_store.add_task(title="Test Task")
        temp_store.toggle_status(1)  # Now complete

        result = temp_store.toggle_status(1)

        assert result is True
        task = temp_store.get_task_by_id(1)
        assert task.status == Status.INCOMPLETE

    def test_toggle_nonexistent_task(self, temp_store):
        """Test toggling a task that doesn't exist."""
        result = temp_store.toggle_status(999)

        assert result is False


class TestTaskServiceDeleteTask:
    """Tests for TaskService.delete_task."""

    def test_delete_existing_task(self, temp_store):
        """Test deleting an existing task."""
        temp_store.add_task(title="To Delete")

        result = temp_store.delete_task(1)

        assert result is True
        assert temp_store.get_task_by_id(1) is None
        assert temp_store.count() == 0

    def test_delete_nonexistent_task(self, temp_store):
        """Test deleting a task that doesn't exist."""
        result = temp_store.delete_task(999)

        assert result is False


class TestTaskServiceCount:
    """Tests for TaskService.count."""

    def test_count_empty(self, temp_store):
        """Test counting when store is empty."""
        assert temp_store.count() == 0

    def test_count_with_tasks(self, temp_store):
        """Test counting with tasks."""
        temp_store.add_task(title="Task 1")
        temp_store.add_task(title="Task 2")

        assert temp_store.count() == 2
