"""Shared test fixtures for the Todo application."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from todo_app.models import Priority, Status, Task
from todo_app.storage import JsonStore


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        id=1,
        title="Test Task",
        description="This is a test task",
        due_date="2024-12-31",
        priority=Priority.MEDIUM,
        categories=["test", "sample"],
        status=Status.INCOMPLETE,
    )


@pytest.fixture
def sample_tasks():
    """Create a list of sample tasks for testing."""
    return [
        Task(
            id=1,
            title="High Priority Task",
            description="Urgent task",
            due_date="2024-12-15",
            priority=Priority.HIGH,
            categories=["work"],
            status=Status.INCOMPLETE,
        ),
        Task(
            id=2,
            title="Medium Priority Task",
            description="Regular task",
            due_date="2024-12-20",
            priority=Priority.MEDIUM,
            categories=["personal"],
            status=Status.COMPLETE,
        ),
        Task(
            id=3,
            title="Low Priority Task",
            description="Can wait",
            due_date=None,
            priority=Priority.LOW,
            categories=["home", "shopping"],
            status=Status.INCOMPLETE,
        ),
    ]


@pytest.fixture
def json_store(temp_json_file):
    """Create a JsonStore instance with a temporary file."""
    return JsonStore(temp_json_file)


@pytest.fixture
def populated_json_store(temp_json_file, sample_tasks):
    """Create a JsonStore instance with sample tasks."""
    store = JsonStore(temp_json_file)
    for task in sample_tasks:
        store.add_task(task)
    return store
