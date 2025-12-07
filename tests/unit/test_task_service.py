import pytest
from src.todo_app.services.task_service import TaskList
from src.todo_app.models.task import Task


class TestTaskList:
    def test_add_task_success(self):
        """Test adding a task successfully."""
        task_list = TaskList()

        result = task_list.add_task("Test task description")

        assert result is not None
        assert result.id == "TSK-001"
        assert result.description == "Test task description"
        assert len(task_list.tasks) == 1

    def test_add_task_empty_description(self):
        """Test adding a task with empty description."""
        task_list = TaskList()

        result = task_list.add_task("")

        assert result is None
        assert len(task_list.tasks) == 0

    def test_add_task_whitespace_description(self):
        """Test adding a task with whitespace-only description."""
        task_list = TaskList()

        result = task_list.add_task("   ")

        assert result is None
        assert len(task_list.tasks) == 0

    def test_get_task_found(self):
        """Test getting an existing task."""
        task_list = TaskList()
        task_list.add_task("Test task")

        task = task_list.get_task("TSK-001")

        assert task is not None
        assert task.id == "TSK-001"
        assert task.description == "Test task"

    def test_get_task_not_found(self):
        """Test getting a non-existing task."""
        task_list = TaskList()
        task_list.add_task("Test task")

        task = task_list.get_task("TSK-999")

        assert task is None

    def test_list_all_tasks(self):
        """Test listing all tasks."""
        task_list = TaskList()
        task_list.add_task("Task 1")
        task_list.add_task("Task 2")

        tasks = task_list.list_all_tasks()

        assert len(tasks) == 2
        assert tasks[0].id == "TSK-001"
        assert tasks[1].id == "TSK-002"

    def test_find_tasks_by_status_completed(self):
        """Test finding tasks by completed status."""
        task_list = TaskList()
        task1 = task_list.add_task("Task 1")
        task2 = task_list.add_task("Task 2")

        # Mark one task as complete
        task_list.mark_task_complete("TSK-001")

        completed_tasks = task_list.find_tasks_by_status(completed=True)

        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == "TSK-001"
        assert completed_tasks[0].completed == True

    def test_find_tasks_by_status_pending(self):
        """Test finding tasks by pending status."""
        task_list = TaskList()
        task_list.add_task("Task 1")
        task_list.add_task("Task 2")

        # Mark one task as complete
        task_list.mark_task_complete("TSK-001")

        pending_tasks = task_list.find_tasks_by_status(completed=False)

        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == "TSK-002"
        assert pending_tasks[0].completed == False

    def test_update_task_description_success(self):
        """Test updating a task description successfully."""
        task_list = TaskList()
        task_list.add_task("Original description")

        result = task_list.update_task_description("TSK-001", "Updated description")

        assert result == True
        task = task_list.get_task("TSK-001")
        assert task.description == "Updated description"

    def test_update_task_description_not_found(self):
        """Test updating a non-existing task description."""
        task_list = TaskList()
        task_list.add_task("Original description")

        result = task_list.update_task_description("TSK-999", "Updated description")

        assert result == False

    def test_update_task_description_empty(self):
        """Test updating a task description with empty string."""
        task_list = TaskList()
        task_list.add_task("Original description")

        result = task_list.update_task_description("TSK-001", "")

        assert result == False
        task = task_list.get_task("TSK-001")
        assert task.description == "Original description"

    def test_mark_task_complete(self):
        """Test marking a task as complete."""
        task_list = TaskList()
        task_list.add_task("Test task")

        result = task_list.mark_task_complete("TSK-001")

        assert result == True
        task = task_list.get_task("TSK-001")
        assert task.completed == True

    def test_mark_task_incomplete(self):
        """Test marking a task as incomplete."""
        task_list = TaskList()
        task_list.add_task("Test task")
        task_list.mark_task_complete("TSK-001")  # First mark as complete

        result = task_list.mark_task_incomplete("TSK-001")

        assert result == True
        task = task_list.get_task("TSK-001")
        assert task.completed == False

    def test_remove_task_success(self):
        """Test removing a task successfully."""
        task_list = TaskList()
        task_list.add_task("Test task")

        result = task_list.remove_task("TSK-001")

        assert result == True
        assert len(task_list.tasks) == 0

    def test_remove_task_not_found(self):
        """Test removing a non-existing task."""
        task_list = TaskList()
        task_list.add_task("Test task")

        result = task_list.remove_task("TSK-999")

        assert result == False
        assert len(task_list.tasks) == 1