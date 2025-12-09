"""Unit tests for Task model and related enums."""

import pytest

from todo_app.models import Priority, Status, Task


class TestPriorityEnum:
    """Tests for Priority enum."""

    def test_priority_values(self):
        """Test that Priority enum has correct values."""
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"

    def test_priority_from_string(self):
        """Test creating Priority from string."""
        assert Priority("high") == Priority.HIGH
        assert Priority("medium") == Priority.MEDIUM
        assert Priority("low") == Priority.LOW

    def test_priority_invalid_value(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            Priority("invalid")


class TestStatusEnum:
    """Tests for Status enum."""

    def test_status_values(self):
        """Test that Status enum has correct values."""
        assert Status.INCOMPLETE.value == "incomplete"
        assert Status.COMPLETE.value == "complete"

    def test_status_from_string(self):
        """Test creating Status from string."""
        assert Status("incomplete") == Status.INCOMPLETE
        assert Status("complete") == Status.COMPLETE

    def test_status_invalid_value(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            Status("invalid")


class TestTaskCreation:
    """Tests for Task dataclass creation."""

    def test_task_with_required_fields_only(self):
        """Test creating a task with only required fields."""
        task = Task(id=1, title="Test Task")

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.priority == Priority.MEDIUM  # default
        assert task.status == Status.INCOMPLETE  # default
        assert task.description == ""  # default
        assert task.due_date is None  # default
        assert task.categories == []  # default
        assert task.created_at is not None  # auto-generated

    def test_task_with_all_fields(self):
        """Test creating a task with all fields."""
        task = Task(
            id=1,
            title="Test Task",
            description="A test description",
            due_date="2024-12-31",
            priority=Priority.HIGH,
            categories=["work", "urgent"],
            status=Status.COMPLETE,
            created_at="2024-12-09T10:00:00",
        )

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "A test description"
        assert task.due_date == "2024-12-31"
        assert task.priority == Priority.HIGH
        assert task.categories == ["work", "urgent"]
        assert task.status == Status.COMPLETE
        assert task.created_at == "2024-12-09T10:00:00"

    def test_task_categories_are_independent(self):
        """Test that each task has its own categories list."""
        task1 = Task(id=1, title="Task 1")
        task2 = Task(id=2, title="Task 2")

        task1.categories.append("work")

        assert task1.categories == ["work"]
        assert task2.categories == []


class TestTaskMethods:
    """Tests for Task methods."""

    def test_toggle_status_incomplete_to_complete(self):
        """Test toggling from incomplete to complete."""
        task = Task(id=1, title="Test", status=Status.INCOMPLETE)

        task.toggle_status()

        assert task.status == Status.COMPLETE

    def test_toggle_status_complete_to_incomplete(self):
        """Test toggling from complete to incomplete."""
        task = Task(id=1, title="Test", status=Status.COMPLETE)

        task.toggle_status()

        assert task.status == Status.INCOMPLETE

    def test_is_complete_when_complete(self):
        """Test is_complete returns True for complete task."""
        task = Task(id=1, title="Test", status=Status.COMPLETE)

        assert task.is_complete() is True

    def test_is_complete_when_incomplete(self):
        """Test is_complete returns False for incomplete task."""
        task = Task(id=1, title="Test", status=Status.INCOMPLETE)

        assert task.is_complete() is False


class TestTaskSerialization:
    """Tests for Task serialization."""

    def test_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(
            id=1,
            title="Test Task",
            description="Description",
            due_date="2024-12-31",
            priority=Priority.HIGH,
            categories=["work"],
            status=Status.COMPLETE,
            created_at="2024-12-09T10:00:00",
        )

        result = task.to_dict()

        assert result == {
            "id": 1,
            "title": "Test Task",
            "description": "Description",
            "due_date": "2024-12-31",
            "priority": "high",
            "categories": ["work"],
            "status": "complete",
            "created_at": "2024-12-09T10:00:00",
        }

    def test_from_dict_full(self):
        """Test creating task from dictionary with all fields."""
        data = {
            "id": 1,
            "title": "Test Task",
            "description": "Description",
            "due_date": "2024-12-31",
            "priority": "high",
            "categories": ["work"],
            "status": "complete",
            "created_at": "2024-12-09T10:00:00",
        }

        task = Task.from_dict(data)

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Description"
        assert task.due_date == "2024-12-31"
        assert task.priority == Priority.HIGH
        assert task.categories == ["work"]
        assert task.status == Status.COMPLETE
        assert task.created_at == "2024-12-09T10:00:00"

    def test_from_dict_minimal(self):
        """Test creating task from dictionary with minimal fields."""
        data = {
            "id": 1,
            "title": "Test Task",
        }

        task = Task.from_dict(data)

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.due_date is None
        assert task.priority == Priority.MEDIUM
        assert task.categories == []
        assert task.status == Status.INCOMPLETE

    def test_roundtrip_serialization(self):
        """Test that to_dict and from_dict are inverse operations."""
        original = Task(
            id=1,
            title="Test Task",
            description="Description",
            due_date="2024-12-31",
            priority=Priority.LOW,
            categories=["home", "garden"],
            status=Status.INCOMPLETE,
            created_at="2024-12-09T10:00:00",
        )

        data = original.to_dict()
        restored = Task.from_dict(data)

        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.due_date == original.due_date
        assert restored.priority == original.priority
        assert restored.categories == original.categories
        assert restored.status == original.status
        assert restored.created_at == original.created_at
