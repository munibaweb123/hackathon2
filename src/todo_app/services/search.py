"""Search functionality for the Todo application."""

from ..models import Task


def search_tasks(tasks: list[Task], keyword: str) -> list[Task]:
    """
    Search tasks by keyword in title or description.

    Args:
        tasks: List of tasks to search.
        keyword: Keyword to search for (case-insensitive).

    Returns:
        List of tasks matching the keyword.
    """
    if not keyword:
        return tasks

    keyword = keyword.lower()

    return [
        task for task in tasks
        if keyword in task.title.lower() or keyword in task.description.lower()
    ]
