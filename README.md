# Todo Console App

A feature-rich command-line todo application built with Python 3.13+ and UV package manager. Supports recurring tasks, reminders, due dates with times, and persistent JSON storage.

## Features

### Core Features
- Add, view, update, and delete tasks
- Mark tasks as complete/incomplete
- Set priority levels (high/medium/low)
- Organize tasks with categories
- Search tasks by keyword
- Filter tasks by status, priority, category, date range, or recurrence
- Sort tasks by due date, priority, title, or creation date

### Advanced Features
- **Recurring Tasks**: Create daily, weekly, monthly, or custom recurring tasks that auto-regenerate when completed
- **Due Time Support**: Set specific due times (e.g., "2:30pm" or "14:30") alongside dates
- **Reminder Notifications**: Get console notifications before task deadlines
- **Series Management**: Edit or delete entire recurring series or single instances
- **Default Preferences**: Configure default reminder settings that auto-apply to new tasks
- **Persistent Storage**: Tasks are saved to `tasks.json` and persist between sessions

## Prerequisites

- Python 3.13 or higher
- UV package manager ([install instructions](https://docs.astral.sh/uv/getting-started/installation/))

## Installation

```bash
# Clone the repository
git clone https://github.com/munibaweb123/hackathon2.git
cd hackathon_2

# Install dependencies with UV
uv sync

# For development (includes pytest):
uv sync --dev
```

## Usage

### Start the Application

```bash
uv run python -m todo_app
```

### Main Menu

```
=== Todo Application ===

1. Add new task
2. View all tasks
3. Update task
4. Delete task
5. Mark task complete/incomplete
6. Search tasks
7. Filter tasks
8. Sort tasks
9. Settings
0. Exit
```

### Example: Create a Recurring Task

```
Enter choice: 1

Add New Task
Title: Weekly team meeting
Description (optional): Discuss project progress
Due date (YYYY-MM-DD, optional): 2025-12-15
Due time (e.g., 2:30pm or 14:30, optional): 10:00am
Priority (high/medium/low): high
Categories (comma-separated, optional): work, meetings

Make this a recurring task?
  1. No (one-time task)
  2. Daily
  3. Weekly
  4. Monthly
  5. Custom interval

Enter choice (default 1): 3
Repeat every N weeks (default 1): 1

Set a reminder?
  1. No reminder
  2. At due time
  3. 15 minutes before
  4. 30 minutes before
  5. 1 hour before
  ...

Enter choice (default 1): 5

Task #1 created successfully!
Repeats: weekly (every 1 week)
Reminder set: 1 hour before
```

### Example: Complete a Recurring Task

When you mark a recurring task as complete, the next instance is automatically created:

```
Enter choice: 5

Toggle Task Status
Enter task ID to toggle: 1

Task #1 marked as complete.
Next recurring instance created: Task #2 (due: 2025-12-22)
```

### Filter Options

```
Filter by:
  1. Status (complete/incomplete)
  2. Priority (high/medium/low)
  3. Category
  4. Due date range
  5. Recurring tasks only
  0. Cancel
```

### Settings Menu

```
Settings

Current Settings:
  Default Reminder: 1 hour before
  Notifications: Enabled

What would you like to configure?
  1. Set default reminder for new tasks
  2. Clear default reminder
  3. Toggle notifications
  0. Back to main menu
```

## Project Structure

```
hackathon_2/
├── src/
│   └── todo_app/
│       ├── __init__.py
│       ├── __main__.py           # Entry point
│       ├── models/
│       │   ├── __init__.py
│       │   ├── task.py           # Task model with recurrence & reminders
│       │   ├── recurrence.py     # RecurrencePattern, RecurrenceFrequency
│       │   └── reminder.py       # Reminder, ReminderOffset
│       ├── services/
│       │   ├── __init__.py
│       │   ├── task_service.py   # Core task operations
│       │   ├── recurrence_service.py  # Recurring task logic
│       │   ├── reminder_service.py    # Reminder notifications
│       │   ├── preferences_service.py # User preferences
│       │   ├── filter.py         # Task filtering
│       │   ├── sort.py           # Task sorting
│       │   ├── search.py         # Task search
│       │   └── validators.py     # Input validation
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── json_store.py     # JSON file persistence
│       │   └── preferences.py    # Preferences storage
│       └── ui/
│           ├── __init__.py
│           ├── menu.py           # Main menu system
│           ├── display.py        # Task display formatting
│           ├── prompts.py        # User input prompts
│           └── console.py        # Console utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── specs/                        # Feature specifications
├── tasks.json                    # Task storage (auto-created)
├── preferences.json              # User preferences (auto-created)
├── pyproject.toml
└── README.md
```

## Data Storage

### tasks.json
Tasks are automatically saved to `tasks.json` in the working directory:

```json
{
  "version": "1.1",
  "tasks": [
    {
      "id": 1,
      "title": "Weekly team meeting",
      "description": "Discuss project progress",
      "status": "incomplete",
      "priority": "high",
      "categories": ["work", "meetings"],
      "due_date": "2025-12-15",
      "due_time": "10:00:00",
      "recurrence": {
        "frequency": "weekly",
        "interval": 1
      },
      "series_id": "abc123-...",
      "reminders": [
        {
          "offset": "1_hour",
          "trigger_time": "2025-12-15T09:00:00"
        }
      ],
      "created_at": "2025-12-09T10:30:00",
      "updated_at": "2025-12-09T10:30:00"
    }
  ]
}
```

### preferences.json
User preferences are stored in `preferences.json`:

```json
{
  "default_reminder": "1_hour",
  "notifications_enabled": true
}
```

## Development

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test types
uv run pytest tests/unit/
uv run pytest tests/integration/
```

## Technology Stack

- **Language**: Python 3.13+
- **Package Manager**: UV
- **Console UI**: Rich (tables, panels, formatting)
- **Date Handling**: python-dateutil
- **Storage**: JSON files
- **Testing**: pytest

## License

MIT License
