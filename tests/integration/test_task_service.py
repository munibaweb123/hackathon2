import pytest
from src.todo_app.services.task_service import TaskList
from src.todo_app.models.task import Task


class TestTaskServiceIntegration:
    def setup_method(self):
        """Set up a fresh task list for each test."""
        self.task_list = TaskList()

    def test_complete_workflow(self):
        """Test a complete workflow: add, list, update, complete, delete."""
        # Add tasks
        task1 = self.task_list.add_task("First task")
        task2 = self.task_list.add_task("Second task")

        assert task1 is not None
        assert task2 is not None
        assert task1.id == "TSK-001"
        assert task2.id == "TSK-002"
        assert len(self.task_list.tasks) == 2

        # List all tasks
        all_tasks = self.task_list.list_all_tasks()
        assert len(all_tasks) == 2

        # Update a task
        result = self.task_list.update_task_description("TSK-001", "Updated first task")
        assert result == True

        # Verify update
        updated_task = self.task_list.get_task("TSK-001")
        assert updated_task.description == "Updated first task"

        # Mark task as complete
        result = self.task_list.mark_task_complete("TSK-001")
        assert result == True
        completed_task = self.task_list.get_task("TSK-001")
        assert completed_task.completed == True

        # Find by status
        completed_tasks = self.task_list.find_tasks_by_status(completed=True)
        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == "TSK-001"

        pending_tasks = self.task_list.find_tasks_by_status(completed=False)
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == "TSK-002"

        # Delete a task
        result = self.task_list.remove_task("TSK-001")
        assert result == True
        assert len(self.task_list.tasks) == 1

        # Verify deletion
        remaining_task = self.task_list.get_task("TSK-002")
        assert remaining_task is not None
        missing_task = self.task_list.get_task("TSK-001")
        assert missing_task is None

    def test_id_generation_sequential(self):
        """Test that task IDs are generated sequentially."""
        task1 = self.task_list.add_task("First task")
        task2 = self.task_list.add_task("Second task")
        task3 = self.task_list.add_task("Third task")

        assert task1.id == "TSK-001"
        assert task2.id == "TSK-002"
        assert task3.id == "TSK-003"

    def test_task_validation_before_adding(self):
        """Test that tasks are validated before being added."""
        # Try to add a task with empty description
        result = self.task_list.add_task("")
        assert result is None
        assert len(self.task_list.tasks) == 0

        # Add a valid task
        result = self.task_list.add_task("Valid task")
        assert result is not None
        assert len(self.task_list.tasks) == 1