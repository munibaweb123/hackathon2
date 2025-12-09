"""Unit tests for sort functionality."""

import pytest

from todo_app.models import Priority, Status, Task
from todo_app.services.sort import (
    sort_by_created_at,
    sort_by_due_date,
    sort_by_priority,
    sort_by_title,
)


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    return [
        Task(id=1, title="Zebra task", priority=Priority.LOW,
             due_date="2024-12-25", created_at="2024-12-09T10:00:00"),
        Task(id=2, title="Apple task", priority=Priority.HIGH,
             due_date="2024-12-15", created_at="2024-12-09T12:00:00"),
        Task(id=3, title="Banana task", priority=Priority.MEDIUM,
             due_date=None, created_at="2024-12-09T08:00:00"),
        Task(id=4, title="Cherry task", priority=Priority.HIGH,
             due_date="2024-12-20", created_at="2024-12-09T14:00:00"),
    ]


class TestSortByDueDate:
    """Tests for sort_by_due_date function."""

    def test_sort_ascending(self, sample_tasks):
        """Test sorting by due date ascending."""
        results = sort_by_due_date(sample_tasks, ascending=True)

        # Task 2 (Dec 15), Task 4 (Dec 20), Task 1 (Dec 25), Task 3 (None - at end)
        assert [r.id for r in results] == [2, 4, 1, 3]

    def test_sort_descending(self, sample_tasks):
        """Test sorting by due date descending."""
        results = sort_by_due_date(sample_tasks, ascending=False)

        # Task 1 (Dec 25), Task 4 (Dec 20), Task 2 (Dec 15), Task 3 (None - at end)
        assert [r.id for r in results] == [1, 4, 2, 3]

    def test_none_dates_at_end(self, sample_tasks):
        """Test that None dates are placed at the end."""
        results = sort_by_due_date(sample_tasks, ascending=True)

        assert results[-1].id == 3  # Task with no due date is last


class TestSortByPriority:
    """Tests for sort_by_priority function."""

    def test_sort_by_priority(self, sample_tasks):
        """Test sorting by priority (high first)."""
        results = sort_by_priority(sample_tasks)

        priorities = [r.priority for r in results]
        assert priorities == [Priority.HIGH, Priority.HIGH, Priority.MEDIUM, Priority.LOW]


class TestSortByTitle:
    """Tests for sort_by_title function."""

    def test_sort_alphabetically(self, sample_tasks):
        """Test sorting alphabetically by title."""
        results = sort_by_title(sample_tasks)

        assert [r.title for r in results] == [
            "Apple task", "Banana task", "Cherry task", "Zebra task"
        ]

    def test_sort_case_insensitive(self):
        """Test that sorting is case-insensitive."""
        tasks = [
            Task(id=1, title="zebra"),
            Task(id=2, title="Apple"),
            Task(id=3, title="BANANA"),
        ]

        results = sort_by_title(tasks)

        assert [r.id for r in results] == [2, 3, 1]


class TestSortByCreatedAt:
    """Tests for sort_by_created_at function."""

    def test_sort_ascending(self, sample_tasks):
        """Test sorting by created_at ascending (oldest first)."""
        results = sort_by_created_at(sample_tasks, ascending=True)

        # Task 3 (08:00), Task 1 (10:00), Task 2 (12:00), Task 4 (14:00)
        assert [r.id for r in results] == [3, 1, 2, 4]

    def test_sort_descending(self, sample_tasks):
        """Test sorting by created_at descending (newest first)."""
        results = sort_by_created_at(sample_tasks, ascending=False)

        # Task 4 (14:00), Task 2 (12:00), Task 1 (10:00), Task 3 (08:00)
        assert [r.id for r in results] == [4, 2, 1, 3]
