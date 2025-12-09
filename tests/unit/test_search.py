"""Unit tests for search functionality."""

import pytest

from todo_app.models import Priority, Status, Task
from todo_app.services.search import search_tasks


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    return [
        Task(id=1, title="Buy groceries", description="Get milk and eggs"),
        Task(id=2, title="Write report", description="Quarterly review"),
        Task(id=3, title="Call mom", description="Birthday wishes"),
        Task(id=4, title="Review code", description="Check pull requests"),
    ]


class TestSearchTasks:
    """Tests for search_tasks function."""

    def test_search_matches_title(self, sample_tasks):
        """Test search matches title."""
        results = search_tasks(sample_tasks, "groceries")

        assert len(results) == 1
        assert results[0].id == 1

    def test_search_matches_description(self, sample_tasks):
        """Test search matches description."""
        results = search_tasks(sample_tasks, "quarterly")

        assert len(results) == 1
        assert results[0].id == 2

    def test_search_case_insensitive(self, sample_tasks):
        """Test search is case-insensitive."""
        results = search_tasks(sample_tasks, "GROCERIES")

        assert len(results) == 1
        assert results[0].id == 1

    def test_search_no_matches(self, sample_tasks):
        """Test search with no matches."""
        results = search_tasks(sample_tasks, "xyz123")

        assert results == []

    def test_search_multiple_matches(self, sample_tasks):
        """Test search with multiple matches."""
        results = search_tasks(sample_tasks, "review")

        assert len(results) == 2
        assert {r.id for r in results} == {2, 4}

    def test_search_empty_keyword_returns_all(self, sample_tasks):
        """Test empty keyword returns all tasks."""
        results = search_tasks(sample_tasks, "")

        assert len(results) == 4

    def test_search_partial_match(self, sample_tasks):
        """Test partial word match."""
        results = search_tasks(sample_tasks, "code")

        assert len(results) == 1
        assert results[0].id == 4
