import pytest
from datetime import datetime
from src.todo_app.models.task import Task


class TestTask:
    def test_task_creation_with_valid_data(self):
        """Test creating a task with valid data."""
        task = Task(id="TSK-001", description="Test task")

        assert task.id == "TSK-001"
        assert task.description == "Test task"
        assert task.completed == False
        assert isinstance(task.created_at, datetime)

    def test_task_creation_with_completed_status(self):
        """Test creating a task with completed status."""
        task = Task(id="TSK-002", description="Completed task", completed=True)

        assert task.id == "TSK-002"
        assert task.description == "Completed task"
        assert task.completed == True

    def test_validate_id_format_valid(self):
        """Test ID format validation with valid format."""
        task = Task(id="TSK-123", description="Test task")

        assert task.validate_id_format() == True

    def test_validate_id_format_invalid(self):
        """Test ID format validation with invalid format."""
        task = Task(id="TASK-123", description="Test task")

        assert task.validate_id_format() == False

    def test_validate_description_valid(self):
        """Test description validation with valid description."""
        task = Task(id="TSK-001", description="Valid description")

        assert task.validate_description() == True

    def test_validate_description_invalid_empty(self):
        """Test description validation with empty description."""
        task = Task(id="TSK-001", description="")

        assert task.validate_description() == False

    def test_validate_description_invalid_whitespace(self):
        """Test description validation with whitespace-only description."""
        task = Task(id="TSK-001", description="   ")

        assert task.validate_description() == False