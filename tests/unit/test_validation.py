"""Unit tests for validation functions."""

import pytest

from todo_app.models import Priority
from todo_app.services.validators import (
    ValidationError,
    validate_categories,
    validate_description,
    validate_due_date,
    validate_priority,
    validate_task_id,
    validate_title,
)


class TestValidateTitle:
    """Tests for validate_title."""

    def test_valid_title(self):
        """Test valid title."""
        assert validate_title("Valid Title") == "Valid Title"

    def test_title_trimmed(self):
        """Test that title is trimmed."""
        assert validate_title("  Trimmed  ") == "Trimmed"

    def test_empty_title_raises(self):
        """Test empty title raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_title("")

    def test_whitespace_title_raises(self):
        """Test whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_title("   ")

    def test_title_too_long_raises(self):
        """Test title exceeding 100 characters raises ValidationError."""
        long_title = "x" * 101
        with pytest.raises(ValidationError, match="cannot exceed 100"):
            validate_title(long_title)

    def test_title_exactly_100_chars(self):
        """Test title with exactly 100 characters is valid."""
        title = "x" * 100
        assert validate_title(title) == title


class TestValidateDescription:
    """Tests for validate_description."""

    def test_valid_description(self):
        """Test valid description."""
        assert validate_description("Valid description") == "Valid description"

    def test_empty_description_valid(self):
        """Test empty description is valid."""
        assert validate_description("") == ""

    def test_description_trimmed(self):
        """Test description is trimmed."""
        assert validate_description("  Trimmed  ") == "Trimmed"

    def test_description_too_long_raises(self):
        """Test description exceeding 500 characters raises ValidationError."""
        long_desc = "x" * 501
        with pytest.raises(ValidationError, match="cannot exceed 500"):
            validate_description(long_desc)


class TestValidateDueDate:
    """Tests for validate_due_date."""

    def test_valid_date(self):
        """Test valid date format."""
        assert validate_due_date("2024-12-31") == "2024-12-31"

    def test_empty_date_returns_none(self):
        """Test empty date returns None."""
        assert validate_due_date("") is None

    def test_whitespace_date_returns_none(self):
        """Test whitespace date returns None."""
        assert validate_due_date("   ") is None

    def test_invalid_format_raises(self):
        """Test invalid format raises ValidationError."""
        with pytest.raises(ValidationError, match="YYYY-MM-DD"):
            validate_due_date("12-31-2024")

    def test_invalid_date_raises(self):
        """Test invalid date (Feb 30) raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid date"):
            validate_due_date("2024-02-30")


class TestValidatePriority:
    """Tests for validate_priority."""

    def test_valid_high(self):
        """Test 'high' is valid."""
        assert validate_priority("high") == Priority.HIGH

    def test_valid_medium(self):
        """Test 'medium' is valid."""
        assert validate_priority("medium") == Priority.MEDIUM

    def test_valid_low(self):
        """Test 'low' is valid."""
        assert validate_priority("low") == Priority.LOW

    def test_case_insensitive(self):
        """Test priority is case-insensitive."""
        assert validate_priority("HIGH") == Priority.HIGH
        assert validate_priority("Medium") == Priority.MEDIUM
        assert validate_priority("LOW") == Priority.LOW

    def test_trimmed(self):
        """Test priority is trimmed."""
        assert validate_priority("  high  ") == Priority.HIGH

    def test_invalid_priority_raises(self):
        """Test invalid priority raises ValidationError."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_priority("urgent")


class TestValidateCategories:
    """Tests for validate_categories."""

    def test_valid_categories(self):
        """Test valid comma-separated categories."""
        result = validate_categories("work, personal, urgent")
        assert result == ["work", "personal", "urgent"]

    def test_empty_string_returns_empty_list(self):
        """Test empty string returns empty list."""
        assert validate_categories("") == []

    def test_whitespace_returns_empty_list(self):
        """Test whitespace returns empty list."""
        assert validate_categories("   ") == []

    def test_categories_normalized_to_lowercase(self):
        """Test categories are normalized to lowercase."""
        result = validate_categories("Work, PERSONAL, Urgent")
        assert result == ["work", "personal", "urgent"]

    def test_duplicates_removed(self):
        """Test duplicate categories are removed."""
        result = validate_categories("work, Work, WORK")
        assert result == ["work"]

    def test_empty_entries_filtered(self):
        """Test empty entries are filtered out."""
        result = validate_categories("work,, personal, ,urgent")
        assert result == ["work", "personal", "urgent"]


class TestValidateTaskId:
    """Tests for validate_task_id."""

    def test_valid_id(self):
        """Test valid ID."""
        assert validate_task_id("1") == 1
        assert validate_task_id("123") == 123

    def test_id_trimmed(self):
        """Test ID is trimmed."""
        assert validate_task_id("  5  ") == 5

    def test_empty_id_raises(self):
        """Test empty ID raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_task_id("")

    def test_non_numeric_raises(self):
        """Test non-numeric ID raises ValidationError."""
        with pytest.raises(ValidationError, match="must be a number"):
            validate_task_id("abc")

    def test_zero_raises(self):
        """Test zero raises ValidationError."""
        with pytest.raises(ValidationError, match="must be a positive number"):
            validate_task_id("0")

    def test_negative_raises(self):
        """Test negative ID raises ValidationError."""
        with pytest.raises(ValidationError, match="must be a positive number"):
            validate_task_id("-5")
