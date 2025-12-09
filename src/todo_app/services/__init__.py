"""Business logic services for the Todo application."""

from .filter import (
    combine_filters,
    filter_by_category,
    filter_by_date_range,
    filter_by_priority,
    filter_by_recurrence,
    filter_by_status,
)
from .recurrence_service import (
    calculate_next_date,
    create_next_instance,
    delete_series,
    generate_series_id,
    get_series_tasks,
    stop_recurrence,
    update_series,
)
from .preferences_service import PreferencesService
from .reminder_service import (
    add_reminder,
    check_due_reminders,
    mark_as_shown,
    recalculate_reminders,
    remove_reminder,
    get_upcoming_reminders,
    create_reminders_for_new_instance,
)
from .search import search_tasks
from .sort import sort_by_created_at, sort_by_due_date, sort_by_priority, sort_by_title
from .task_service import TaskService
from .validators import ValidationError

__all__ = [
    "PreferencesService",
    "TaskService",
    "ValidationError",
    "add_reminder",
    "calculate_next_date",
    "check_due_reminders",
    "combine_filters",
    "create_next_instance",
    "create_reminders_for_new_instance",
    "delete_series",
    "filter_by_category",
    "filter_by_date_range",
    "filter_by_priority",
    "filter_by_recurrence",
    "filter_by_status",
    "generate_series_id",
    "get_series_tasks",
    "get_upcoming_reminders",
    "mark_as_shown",
    "recalculate_reminders",
    "remove_reminder",
    "search_tasks",
    "sort_by_created_at",
    "sort_by_due_date",
    "sort_by_priority",
    "sort_by_title",
    "stop_recurrence",
    "update_series",
]
