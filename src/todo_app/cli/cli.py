import argparse
from typing import Optional
from ..services.task_service import TaskList


class TodoCLI:
    """
    Command-line interface for the todo application.
    """
    def __init__(self, task_list: TaskList):
        self.task_list = task_list

    def add_task(self, description: str) -> str:
        """
        Add a new task with the given description.
        """
        if not description or not description.strip():
            return "Error: Task description cannot be empty"

        task = self.task_list.add_task(description)
        if task:
            return f"Task added successfully: {task.id} - {task.description}"
        else:
            return "Error: Failed to create task"

    def list_tasks(self) -> str:
        """
        List all tasks with their status.
        """
        tasks = self.task_list.list_all_tasks()
        if not tasks:
            return "Task List:\nNo tasks found."

        result = ["Task List:"]
        for task in tasks:
            status = "[x]" if task.completed else "[ ]"
            result.append(f"{task.id} {status} {task.description}")
        return "\n".join(result)

    def complete_task(self, task_id: str) -> str:
        """
        Mark a task as complete.
        """
        # Validate task ID format
        if not self._validate_task_id_format(task_id):
            return f"Error: Invalid task ID format. Use TSK-### format."

        if self.task_list.mark_task_complete(task_id):
            return f"Task {task_id} marked as complete"
        else:
            return f"Error: Task {task_id} not found"

    def update_task(self, task_id: str, new_description: str) -> str:
        """
        Update a task's description.
        """
        # Validate task ID format
        if not self._validate_task_id_format(task_id):
            return f"Error: Invalid task ID format. Use TSK-### format."

        if not new_description or not new_description.strip():
            return "Error: Task description cannot be empty"

        if self.task_list.update_task_description(task_id, new_description):
            return f"Task {task_id} updated: {new_description}"
        else:
            return f"Error: Task {task_id} not found"

    def delete_task(self, task_id: str) -> str:
        """
        Delete a task.
        """
        # Validate task ID format
        if not self._validate_task_id_format(task_id):
            return f"Error: Invalid task ID format. Use TSK-### format."

        if self.task_list.remove_task(task_id):
            return f"Task {task_id} deleted successfully"
        else:
            return f"Error: Task {task_id} not found"

    def _validate_task_id_format(self, task_id: str) -> bool:
        """
        Validate that the task ID follows the format TSK-### where ### is a 3-digit number.
        """
        import re
        pattern = r"^TSK-\d{3}$"
        return bool(re.match(pattern, task_id))