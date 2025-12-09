"""Unit tests for JSON storage layer."""

import json
import os
import tempfile

import pytest

from todo_app.models import Priority, Status, Task
from todo_app.storage import JsonStore


class TestJsonStoreInit:
    """Tests for JsonStore initialization."""

    def test_init_creates_empty_store_for_missing_file(self, temp_json_file):
        """Test that missing file results in empty store."""
        os.unlink(temp_json_file)  # Remove the file

        store = JsonStore(temp_json_file)

        assert store.count() == 0
        assert store.get_all_tasks() == []

    def test_init_loads_existing_file(self, temp_json_file):
        """Test that existing file is loaded correctly."""
        data = {
            "metadata": {"version": "1.0", "max_id": 2},
            "tasks": [
                {"id": 1, "title": "Task 1", "priority": "high", "status": "incomplete"},
                {"id": 2, "title": "Task 2", "priority": "low", "status": "complete"},
            ],
        }
        with open(temp_json_file, "w") as f:
            json.dump(data, f)

        store = JsonStore(temp_json_file)

        assert store.count() == 2
        assert store.get_task(1).title == "Task 1"
        assert store.get_task(2).title == "Task 2"

    def test_init_handles_corrupted_json(self, temp_json_file):
        """Test that corrupted JSON is handled gracefully."""
        with open(temp_json_file, "w") as f:
            f.write("not valid json {{{")

        store = JsonStore(temp_json_file)

        assert store.count() == 0


class TestJsonStoreAddTask:
    """Tests for adding tasks."""

    def test_add_task_assigns_id(self, json_store):
        """Test that adding a task assigns an ID."""
        task = Task(id=0, title="New Task")

        result = json_store.add_task(task)

        assert result.id == 1

    def test_add_task_increments_id(self, json_store):
        """Test that IDs are incremented correctly."""
        task1 = Task(id=0, title="Task 1")
        task2 = Task(id=0, title="Task 2")

        result1 = json_store.add_task(task1)
        result2 = json_store.add_task(task2)

        assert result1.id == 1
        assert result2.id == 2

    def test_add_task_persists_to_file(self, temp_json_file):
        """Test that added tasks are persisted to file."""
        store = JsonStore(temp_json_file)
        task = Task(id=0, title="Test Task")

        store.add_task(task)

        # Read from file directly
        with open(temp_json_file) as f:
            data = json.load(f)

        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test Task"

    def test_add_task_with_explicit_id(self, json_store):
        """Test adding a task with an explicit ID."""
        task = Task(id=5, title="Task with ID")

        result = json_store.add_task(task)

        assert result.id == 5
        assert json_store.get_task(5) is not None


class TestJsonStoreGetTask:
    """Tests for getting tasks."""

    def test_get_task_existing(self, json_store):
        """Test getting an existing task."""
        task = Task(id=0, title="Test Task")
        json_store.add_task(task)

        result = json_store.get_task(1)

        assert result is not None
        assert result.title == "Test Task"

    def test_get_task_nonexistent(self, json_store):
        """Test getting a non-existent task returns None."""
        result = json_store.get_task(999)

        assert result is None


class TestJsonStoreGetAllTasks:
    """Tests for getting all tasks."""

    def test_get_all_tasks_empty(self, json_store):
        """Test getting all tasks from empty store."""
        result = json_store.get_all_tasks()

        assert result == []

    def test_get_all_tasks_sorted_by_id(self, json_store):
        """Test that tasks are returned sorted by ID."""
        json_store.add_task(Task(id=3, title="Task 3"))
        json_store.add_task(Task(id=1, title="Task 1"))
        json_store.add_task(Task(id=2, title="Task 2"))

        result = json_store.get_all_tasks()

        assert [t.id for t in result] == [1, 2, 3]


class TestJsonStoreUpdateTask:
    """Tests for updating tasks."""

    def test_update_task_existing(self, json_store):
        """Test updating an existing task."""
        task = Task(id=0, title="Original")
        json_store.add_task(task)

        updated = Task(id=1, title="Updated")
        result = json_store.update_task(updated)

        assert result is True
        assert json_store.get_task(1).title == "Updated"

    def test_update_task_nonexistent(self, json_store):
        """Test updating a non-existent task."""
        task = Task(id=999, title="Does not exist")

        result = json_store.update_task(task)

        assert result is False

    def test_update_task_persists_to_file(self, temp_json_file):
        """Test that updates are persisted to file."""
        store = JsonStore(temp_json_file)
        store.add_task(Task(id=0, title="Original"))

        store.update_task(Task(id=1, title="Updated", priority=Priority.HIGH))

        # Read from file directly
        with open(temp_json_file) as f:
            data = json.load(f)

        assert data["tasks"][0]["title"] == "Updated"
        assert data["tasks"][0]["priority"] == "high"


class TestJsonStoreDeleteTask:
    """Tests for deleting tasks."""

    def test_delete_task_existing(self, json_store):
        """Test deleting an existing task."""
        json_store.add_task(Task(id=0, title="To Delete"))

        result = json_store.delete_task(1)

        assert result is True
        assert json_store.get_task(1) is None
        assert json_store.count() == 0

    def test_delete_task_nonexistent(self, json_store):
        """Test deleting a non-existent task."""
        result = json_store.delete_task(999)

        assert result is False

    def test_delete_task_persists_to_file(self, temp_json_file):
        """Test that deletion is persisted to file."""
        store = JsonStore(temp_json_file)
        store.add_task(Task(id=0, title="To Delete"))

        store.delete_task(1)

        # Read from file directly
        with open(temp_json_file) as f:
            data = json.load(f)

        assert len(data["tasks"]) == 0


class TestJsonStoreAtomicWrite:
    """Tests for atomic write functionality."""

    def test_file_not_corrupted_on_write(self, temp_json_file):
        """Test that file is written atomically."""
        store = JsonStore(temp_json_file)

        # Add many tasks
        for i in range(50):
            store.add_task(Task(id=0, title=f"Task {i}"))

        # File should always be valid JSON
        with open(temp_json_file) as f:
            data = json.load(f)

        assert len(data["tasks"]) == 50


class TestJsonStoreMaxId:
    """Tests for max_id tracking."""

    def test_max_id_never_reused(self, json_store):
        """Test that IDs are never reused after deletion."""
        json_store.add_task(Task(id=0, title="Task 1"))
        json_store.add_task(Task(id=0, title="Task 2"))

        json_store.delete_task(1)
        json_store.delete_task(2)

        new_task = json_store.add_task(Task(id=0, title="Task 3"))

        assert new_task.id == 3  # Not 1, even though 1 is now free

    def test_max_id_preserved_across_loads(self, temp_json_file):
        """Test that max_id is preserved when reloading."""
        store1 = JsonStore(temp_json_file)
        store1.add_task(Task(id=0, title="Task 1"))
        store1.add_task(Task(id=0, title="Task 2"))
        store1.delete_task(2)

        # Reload the store
        store2 = JsonStore(temp_json_file)
        new_task = store2.add_task(Task(id=0, title="Task 3"))

        assert new_task.id == 3


class TestJsonStoreMissingFileHandling:
    """Tests for handling missing files."""

    def test_missing_file_creates_empty_store(self):
        """Test that a missing file results in an empty store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "nonexistent.json")

            store = JsonStore(file_path)

            assert store.count() == 0

    def test_first_add_creates_file(self):
        """Test that adding first task creates the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "new.json")
            store = JsonStore(file_path)

            store.add_task(Task(id=0, title="First Task"))

            assert os.path.exists(file_path)
