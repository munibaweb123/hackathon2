"""Unit tests for filter functionality."""

import pytest

from todo_app.models import Priority, Status, Task
from todo_app.services.filter import (
    combine_filters,
    filter_by_category,
    filter_by_date_range,
    filter_by_priority,
    filter_by_status,
)


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    return [
        Task(id=1, title="Task 1", priority=Priority.HIGH, status=Status.INCOMPLETE,
             due_date="2024-12-15", categories=["work"]),
        Task(id=2, title="Task 2", priority=Priority.MEDIUM, status=Status.COMPLETE,
             due_date="2024-12-20", categories=["personal"]),
        Task(id=3, title="Task 3", priority=Priority.LOW, status=Status.INCOMPLETE,
             due_date=None, categories=["work", "urgent"]),
        Task(id=4, title="Task 4", priority=Priority.HIGH, status=Status.COMPLETE,
             due_date="2024-12-25", categories=["personal"]),
    ]


class TestFilterByStatus:
    """Tests for filter_by_status function."""

    def test_filter_complete(self, sample_tasks):
        """Test filtering for complete tasks."""
        results = filter_by_status(sample_tasks, Status.COMPLETE)

        assert len(results) == 2
        assert all(t.status == Status.COMPLETE for t in results)

    def test_filter_incomplete(self, sample_tasks):
        """Test filtering for incomplete tasks."""
        results = filter_by_status(sample_tasks, Status.INCOMPLETE)

        assert len(results) == 2
        assert all(t.status == Status.INCOMPLETE for t in results)


class TestFilterByPriority:
    """Tests for filter_by_priority function."""

    def test_filter_high_priority(self, sample_tasks):
        """Test filtering for high priority tasks."""
        results = filter_by_priority(sample_tasks, Priority.HIGH)

        assert len(results) == 2
        assert all(t.priority == Priority.HIGH for t in results)

    def test_filter_medium_priority(self, sample_tasks):
        """Test filtering for medium priority tasks."""
        results = filter_by_priority(sample_tasks, Priority.MEDIUM)

        assert len(results) == 1
        assert results[0].id == 2

    def test_filter_low_priority(self, sample_tasks):
        """Test filtering for low priority tasks."""
        results = filter_by_priority(sample_tasks, Priority.LOW)

        assert len(results) == 1
        assert results[0].id == 3


class TestFilterByCategory:
    """Tests for filter_by_category function."""

    def test_filter_by_category(self, sample_tasks):
        """Test filtering by category."""
        results = filter_by_category(sample_tasks, "work")

        assert len(results) == 2
        assert {r.id for r in results} == {1, 3}

    def test_filter_category_case_insensitive(self, sample_tasks):
        """Test category filter is case-insensitive."""
        results = filter_by_category(sample_tasks, "WORK")

        assert len(results) == 2

    def test_filter_category_no_matches(self, sample_tasks):
        """Test category filter with no matches."""
        results = filter_by_category(sample_tasks, "shopping")

        assert results == []


class TestFilterByDateRange:
    """Tests for filter_by_date_range function."""

    def test_filter_start_date_only(self, sample_tasks):
        """Test filtering with only start date."""
        results = filter_by_date_range(sample_tasks, start_date="2024-12-18")

        assert len(results) == 2
        assert {r.id for r in results} == {2, 4}

    def test_filter_end_date_only(self, sample_tasks):
        """Test filtering with only end date."""
        results = filter_by_date_range(sample_tasks, end_date="2024-12-18")

        assert len(results) == 1
        assert results[0].id == 1

    def test_filter_date_range(self, sample_tasks):
        """Test filtering with both start and end dates."""
        results = filter_by_date_range(
            sample_tasks, start_date="2024-12-16", end_date="2024-12-22"
        )

        assert len(results) == 1
        assert results[0].id == 2

    def test_filter_excludes_tasks_without_due_date(self, sample_tasks):
        """Test that tasks without due dates are excluded."""
        results = filter_by_date_range(sample_tasks, start_date="2024-01-01")

        assert all(t.due_date is not None for t in results)


class TestCombineFilters:
    """Tests for combine_filters function."""

    def test_combine_status_and_priority(self, sample_tasks):
        """Test combining status and priority filters."""
        results = combine_filters(
            sample_tasks,
            status=Status.INCOMPLETE,
            priority=Priority.HIGH,
        )

        assert len(results) == 1
        assert results[0].id == 1

    def test_combine_all_filters(self, sample_tasks):
        """Test combining all filter types."""
        results = combine_filters(
            sample_tasks,
            status=Status.COMPLETE,
            priority=Priority.HIGH,
            category="personal",
        )

        assert len(results) == 1
        assert results[0].id == 4

    def test_combine_filters_no_matches(self, sample_tasks):
        """Test combining filters with no matches."""
        results = combine_filters(
            sample_tasks,
            status=Status.INCOMPLETE,
            priority=Priority.LOW,
            category="personal",  # Task 3 is low priority but has work category
        )

        assert results == []
