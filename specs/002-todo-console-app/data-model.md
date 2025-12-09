# Data Model: Professional Todo Console Application

**Feature**: 002-todo-console-app
**Date**: 2025-12-09
**Version**: 1.0

## Entities

### Task

The primary entity representing a todo item.

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| id | int | Yes | Auto-generated | Positive integer, unique, sequential, never reused | Unique identifier for the task |
| title | str | Yes | - | 1-100 characters, non-empty | Short description of the task |
| description | str | No | "" | 0-500 characters | Detailed information about the task |
| due_date | str \| None | No | None | YYYY-MM-DD format or None | Target completion date |
| priority | Priority | Yes | medium | One of: high, medium, low | Importance level |
| categories | list[str] | No | [] | Case-insensitive, duplicates merged | Organization tags |
| status | Status | Yes | incomplete | One of: incomplete, complete | Completion state |
| created_at | str | Yes | Auto-generated | ISO 8601 datetime | When task was created |

### Priority (Enum)

| Value | Display | Color |
|-------|---------|-------|
| high | High | Red |
| medium | Medium | Yellow |
| low | Low | Green |

### Status (Enum)

| Value | Display | Indicator |
|-------|---------|-----------|
| incomplete | Incomplete | [ ] (empty checkbox) |
| complete | Complete | [✓] (checkmark) |

## Data Structures

### Task (Python Dataclass)

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Status(str, Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"

@dataclass
class Task:
    id: int
    title: str
    priority: Priority = Priority.MEDIUM
    status: Status = Status.INCOMPLETE
    description: str = ""
    due_date: Optional[str] = None
    categories: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

### TaskStore (JSON Structure)

```json
{
  "metadata": {
    "version": "1.0",
    "max_id": 5,
    "last_modified": "2024-12-09T10:30:00"
  },
  "tasks": [
    {
      "id": 1,
      "title": "Complete project documentation",
      "description": "Write README and API docs",
      "due_date": "2024-12-15",
      "priority": "high",
      "categories": ["work", "documentation"],
      "status": "incomplete",
      "created_at": "2024-12-09T09:00:00"
    }
  ]
}
```

## Validation Rules

### Title Validation
- Must not be empty or whitespace-only
- Must be 1-100 characters after trimming
- All printable characters allowed

### Description Validation
- Optional (can be empty string)
- Maximum 500 characters
- All printable characters allowed

### Due Date Validation
- Optional (can be None)
- If provided, must match YYYY-MM-DD format
- Date must be parseable (valid day/month)
- Past dates are allowed (overdue tasks)

### Priority Validation
- Must be one of: "high", "medium", "low"
- Case-insensitive input accepted
- Stored as lowercase

### Categories Validation
- Optional (can be empty list)
- Each category trimmed of whitespace
- Case-insensitive (stored as lowercase)
- Duplicates automatically removed
- Empty strings filtered out

## State Transitions

### Task Status

```
┌─────────────┐     toggle()     ┌───────────┐
│  incomplete │ ◄──────────────► │  complete │
└─────────────┘                  └───────────┘
     ▲                                 ▲
     │                                 │
     └─────── initial state ───────────┘
                  (add)
```

### Task Lifecycle

```
┌─────────┐     add()      ┌──────────┐    update()    ┌──────────┐
│ (none)  │ ──────────────►│  Active  │ ◄─────────────►│  Active  │
└─────────┘                └──────────┘                └──────────┘
                                │
                                │ delete()
                                ▼
                           ┌──────────┐
                           │ Deleted  │
                           └──────────┘
```

## Relationships

This is a single-entity model with no relationships between tasks.

Future considerations (out of scope):
- Task dependencies (blocked_by, blocks)
- Subtasks (parent_id)
- Projects (project_id)

## Indexes (Conceptual)

For efficient operations on up to 500 tasks:

| Index | Purpose | Implementation |
|-------|---------|----------------|
| by_id | Task lookup for update/delete/toggle | dict[int, Task] in memory |
| by_status | Filter by complete/incomplete | list comprehension |
| by_priority | Filter/sort by priority | list comprehension with enum ordering |
| by_due_date | Filter by date range, sort by date | list comprehension with date parsing |
| by_category | Filter by category | list comprehension with `in` check |

## Data Integrity

### Constraints

1. **ID Uniqueness**: max_id in metadata ensures no ID reuse
2. **Required Fields**: title, priority, status always present
3. **Format Validation**: due_date format checked before storage
4. **Type Safety**: Enums prevent invalid priority/status values

### Corruption Recovery

1. On JSON parse error: backup corrupted file, start fresh
2. On missing required field: log warning, use defaults
3. On invalid enum value: log warning, use default (medium/incomplete)
4. On missing metadata: rebuild from task list

## Migration Strategy

Version 1.0 is the initial schema. Future migrations:

| From | To | Changes | Migration |
|------|----|---------|-----------|
| - | 1.0 | Initial schema | N/A |

Future version changes would:
1. Bump metadata.version
2. Add migration function in storage layer
3. Run migration on load if version mismatch
