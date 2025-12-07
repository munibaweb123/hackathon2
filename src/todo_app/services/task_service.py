from typing import List, Optional
from ..models.task import Task


class TaskList:
    """
    A collection of tasks stored in memory during the application session.
    """
    def __init__(self):
        self.tasks: List[Task] = []
        self.next_id: int = 1

    def add_task(self, description: str) -> Optional[Task]:
        """
        Creates a new task and adds it to the collection.
        Returns the created task or None if validation fails.
        """
        if not description or not description.strip():
            return None

        # Generate unique ID in TSK-### format
        task_id = f"TSK-{self.next_id:03d}"
        self.next_id += 1

        task = Task(id=task_id, description=description.strip())

        # Validate the task before adding
        if task.validate_id_format() and task.validate_description():
            self.tasks.append(task)
            return task
        return None

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Retrieves a task by ID.
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def list_all_tasks(self) -> List[Task]:
        """
        Returns all tasks in the collection.
        """
        return self.tasks.copy()

    def find_tasks_by_status(self, completed: bool) -> List[Task]:
        """
        Returns tasks matching a specific completion status.
        """
        return [task for task in self.tasks if task.completed == completed]

    def update_task_description(self, task_id: str, new_description: str) -> bool:
        """
        Modifies an existing task's description.
        Returns True if successful, False otherwise.
        """
        if not new_description or not new_description.strip():
            return False

        task = self.get_task(task_id)
        if task:
            task.description = new_description.strip()
            return True
        return False

    def mark_task_complete(self, task_id: str) -> bool:
        """
        Updates a task's completion status to complete.
        Returns True if successful, False otherwise.
        """
        task = self.get_task(task_id)
        if task:
            task.completed = True
            return True
        return False

    def mark_task_incomplete(self, task_id: str) -> bool:
        """
        Updates a task's completion status to incomplete.
        Returns True if successful, False otherwise.
        """
        task = self.get_task(task_id)
        if task:
            task.completed = False
            return True
        return False

    def remove_task(self, task_id: str) -> bool:
        """
        Removes a task from the collection by ID.
        Returns True if successful, False otherwise.
        """
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False