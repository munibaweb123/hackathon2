# Quickstart: Advanced Todo Features

**Feature**: 003-advanced-todo-features
**Date**: 2025-12-09

## Prerequisites

- Python 3.13+
- uv package manager
- Existing todo app from Phase 1/2

## Setup

### 1. Install New Dependency

```bash
cd /mnt/c/Users/YOusuf\ Traders/Documents/quarter-4/hackathon_2

# Add python-dateutil to pyproject.toml dependencies
uv add python-dateutil
```

### 2. Verify Installation

```bash
uv run python -c "from dateutil.rrule import rrule; print('dateutil OK')"
```

## Development Order

Follow this order to implement the feature incrementally:

### Phase A: Core Models (Day 1)

1. **RecurrencePattern model** (`src/todo_app/models/recurrence.py`)
   - Create `RecurrenceFrequency` enum
   - Create `RecurrencePattern` dataclass
   - Add `to_dict()` and `from_dict()` methods

2. **Reminder model** (`src/todo_app/models/reminder.py`)
   - Create `ReminderOffset` enum
   - Create `Reminder` dataclass
   - Add `to_dict()` and `from_dict()` methods

3. **Extend Task model** (`src/todo_app/models/task.py`)
   - Add `due_time: Optional[str]`
   - Add `recurrence: Optional[RecurrencePattern]`
   - Add `series_id: Optional[str]`
   - Add `reminders: list[Reminder]`
   - Update `to_dict()` and `from_dict()`

### Phase B: Services (Day 1-2)

4. **RecurrenceService** (`src/todo_app/services/recurrence_service.py`)
   - `calculate_next_date(task)` - date calculation logic
   - `create_next_instance(task)` - new task generation

5. **ReminderService** (`src/todo_app/services/reminder_service.py`)
   - `add_reminder(task_id, offset, custom)` - reminder creation
   - `check_due_reminders()` - find due reminders
   - `mark_as_shown(reminder_id)` - mark triggered

6. **Extend TaskService** (`src/todo_app/services/task_service.py`)
   - Update `add_task()` for recurrence support
   - Update `complete_task()` to auto-create next instance

### Phase C: Validators (Day 2)

7. **Extend Validators** (`src/todo_app/services/validators.py`)
   - `validate_time(time_str)` - parse flexible time formats
   - `validate_recurrence(pattern)` - validate recurrence input

### Phase D: Storage (Day 2)

8. **Extend JsonStore** (`src/todo_app/storage/json_store.py`)
   - Update schema version to 1.1
   - Handle new Task fields in serialization

9. **UserPreferences storage** (`src/todo_app/storage/preferences.py`)
   - Load/save preferences.json
   - Default reminder settings

### Phase E: UI (Day 2-3)

10. **Extend Prompts** (`src/todo_app/ui/prompts.py`)
    - `prompt_due_time()` - time input
    - `prompt_recurrence()` - recurrence pattern input
    - `prompt_reminder()` - reminder offset selection

11. **Extend Display** (`src/todo_app/ui/display.py`)
    - Show recurrence pattern on task view
    - Show reminders on task view
    - Display reminder alerts

12. **Extend Menu** (`src/todo_app/ui/menu.py`)
    - Add recurrence to add task flow
    - Add reminder management options
    - Add settings menu for preferences

## Quick Test Commands

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_recurrence.py -v

# Run the app
uv run python -m todo_app
```

## Testing Workflow

### Manual Test: Recurring Task

1. Run app: `uv run python -m todo_app`
2. Add task → Set recurrence: Weekly on Monday
3. Mark task complete
4. Verify new task created with next Monday's date

### Manual Test: Reminder

1. Add task with due date/time: today + 1 minute
2. Add reminder: "At time"
3. Wait 1 minute
4. Verify notification appears on next app action

## File Checklist

```
□ src/todo_app/models/recurrence.py (NEW)
□ src/todo_app/models/reminder.py (NEW)
□ src/todo_app/models/task.py (EXTEND)
□ src/todo_app/models/__init__.py (UPDATE exports)
□ src/todo_app/services/recurrence_service.py (NEW)
□ src/todo_app/services/reminder_service.py (NEW)
□ src/todo_app/services/task_service.py (EXTEND)
□ src/todo_app/services/validators.py (EXTEND)
□ src/todo_app/services/__init__.py (UPDATE exports)
□ src/todo_app/storage/json_store.py (EXTEND)
□ src/todo_app/storage/preferences.py (NEW)
□ src/todo_app/storage/__init__.py (UPDATE exports)
□ src/todo_app/ui/prompts.py (EXTEND)
□ src/todo_app/ui/display.py (EXTEND)
□ src/todo_app/ui/menu.py (EXTEND)
□ pyproject.toml (ADD python-dateutil)
□ tests/unit/test_recurrence.py (NEW)
□ tests/unit/test_reminder.py (NEW)
```

## Common Issues

### Issue: dateutil not found
```bash
uv add python-dateutil
uv sync
```

### Issue: Old tasks.json incompatible
- Solution: Delete tasks.json or let it auto-migrate (new fields are optional)

### Issue: Timezone confusion
- All times stored as UTC
- Display uses local timezone automatically
