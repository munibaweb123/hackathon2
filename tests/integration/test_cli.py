import pytest
from src.todo_app.services.task_service import TaskList
from src.todo_app.cli.cli import TodoCLI


class TestCLIFunctionality:
    def setup_method(self):
        """Set up a fresh task list and CLI for each test."""
        self.task_list = TaskList()
        self.cli = TodoCLI(self.task_list)

    def test_add_and_list_tasks(self):
        """Test adding a task and then listing it."""
        # Add a task
        add_result = self.cli.add_task("Complete project documentation")
        assert "Task added successfully" in add_result
        assert "TSK-001" in add_result

        # List tasks
        list_result = self.cli.list_tasks()
        assert "TSK-001" in list_result
        assert "[ ]" in list_result  # Task should be pending
        assert "Complete project documentation" in list_result

    def test_complete_task(self):
        """Test adding a task, completing it, and verifying the status."""
        # Add a task
        self.cli.add_task("Review code changes")

        # Complete the task
        complete_result = self.cli.complete_task("TSK-001")
        assert "Task TSK-001 marked as complete" in complete_result

        # Verify in list
        list_result = self.cli.list_tasks()
        assert "TSK-001" in list_result
        assert "[x]" in list_result  # Task should be complete

    def test_update_task_description(self):
        """Test updating a task's description."""
        # Add a task
        self.cli.add_task("Original task description")

        # Update the task
        update_result = self.cli.update_task("TSK-001", "Updated task description")
        assert "Task TSK-001 updated" in update_result
        assert "Updated task description" in update_result

        # Verify in list
        list_result = self.cli.list_tasks()
        assert "Updated task description" in list_result
        assert "Original task description" not in list_result

    def test_delete_task(self):
        """Test deleting a task."""
        # Add a task
        self.cli.add_task("Task to be deleted")

        # Delete the task
        delete_result = self.cli.delete_task("TSK-001")
        assert "Task TSK-001 deleted successfully" in delete_result

        # Verify task is gone from list
        list_result = self.cli.list_tasks()
        assert "TSK-001" not in list_result

    def test_invalid_task_operations(self):
        """Test operations on non-existing tasks."""
        # Try to complete a non-existing task
        complete_result = self.cli.complete_task("TSK-999")
        assert "Error: Task TSK-999 not found" in complete_result

        # Try to update a non-existing task
        update_result = self.cli.update_task("TSK-999", "New description")
        assert "Error: Task TSK-999 not found" in update_result

        # Try to delete a non-existing task
        delete_result = self.cli.delete_task("TSK-999")
        assert "Error: Task TSK-999 not found" in delete_result

    def test_empty_task_list(self):
        """Test listing an empty task list."""
        list_result = self.cli.list_tasks()
        assert "No tasks found" in list_result