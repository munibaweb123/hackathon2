# Data Model: Todo In-Memory Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-09
**Source**: [spec.md](./spec.md) - Key Entities section

## Entity: Task

A Task represents a single todo item in the application.

### Attributes

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | int | Yes (auto) | Auto-increment from 1 | Unique numeric identifier, never reused after deletion |
| `title` | str | Yes | - | Short description of the task (non-empty) |
| `description` | str | No | "" | Detailed information about the task |
| `completed` | bool | No | False | Completion state (False = incomplete, True = complete) |

### Validation Rules

1. **ID Generation**:
   - IDs are sequential integers starting from 1
   - Each new task gets the next available ID (max existing ID + 1)
   - Deleted task IDs are NOT reused

2. **Title Validation**:
   - Must be a non-empty string
   - Whitespace-only strings are considered empty (invalid)
   - No maximum length enforced (spec allows >200 chars)

3. **Description Validation**:
   - Can be empty string
   - No validation required

4. **Completed State**:
   - Boolean only (True/False)
   - New tasks default to False (incomplete)
   - Can be toggled between True and False

### State Transitions

```
┌─────────────────────────────────────────────────────┐
│                     LIFECYCLE                        │
└─────────────────────────────────────────────────────┘

    [Created]                    [Deleted]
        │                            ▲
        ▼                            │
   ┌─────────┐    toggle()     ┌─────────┐
   │Incomplete│◄──────────────►│Complete │
   │completed │                │completed│
   │ = False  │                │ = True  │
   └─────────┘                 └─────────┘
        │                            │
        └────────► delete() ◄────────┘
```

### Relationships

None - Task is a standalone entity with no foreign keys or references.

### Python Implementation

```python
from dataclasses import dataclass, field


@dataclass
class Task:
    """Represents a single todo item."""

    title: str
    description: str = ""
    completed: bool = False
    id: int = field(default=0)

    def __post_init__(self) -> None:
        """Validate title is non-empty."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

    def mark_complete(self) -> None:
        """Mark task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark task as incomplete."""
        self.completed = False

    def toggle_status(self) -> None:
        """Toggle between complete and incomplete."""
        self.completed = not self.completed
```

### Storage Model

```python
class TaskStorage:
    """In-memory storage for tasks using dictionary."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> Task:
        """Add task with auto-generated ID."""
        task.id = self._next_id
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        """Get task by ID, returns None if not found."""
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Get all tasks as list."""
        return list(self._tasks.values())

    def update(self, task: Task) -> bool:
        """Update existing task, returns False if not found."""
        if task.id not in self._tasks:
            return False
        self._tasks[task.id] = task
        return True

    def delete(self, task_id: int) -> bool:
        """Delete task by ID, returns False if not found."""
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    def exists(self, task_id: int) -> bool:
        """Check if task exists."""
        return task_id in self._tasks
```

## Service Layer Operations

| Operation | Input | Output | Error Cases |
|-----------|-------|--------|-------------|
| `add_task` | title, description | Task (with ID) | Empty title |
| `get_task` | id | Task or None | Invalid ID format |
| `get_all_tasks` | - | list[Task] | - |
| `update_task` | id, title?, description? | bool | Task not found |
| `delete_task` | id | bool | Task not found |
| `mark_complete` | id | bool | Task not found |
| `mark_incomplete` | id | bool | Task not found |
