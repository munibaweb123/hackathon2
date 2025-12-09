# Service Interface Contracts

**Feature**: 003-advanced-todo-features
**Date**: 2025-12-09

This document defines the internal service interfaces for the advanced todo features. Since this is a console application (not an API server), these are Python interface contracts.

---

## RecurrenceService

Handles recurrence pattern calculations and series management.

### Methods

#### `calculate_next_date(task: Task) -> Optional[date]`

Calculate the next occurrence date for a recurring task.

**Input**:
- `task`: Task with `recurrence` pattern and `due_date`

**Output**:
- `date`: Next occurrence date, or `None` if recurrence has ended

**Behavior**:
- Uses current `due_date` as base
- Applies recurrence pattern to calculate next date
- Returns `None` if `end_date` has passed
- Handles month-end edge cases (e.g., Jan 31 → Feb 28)

**Example**:
```python
task = Task(due_date="2025-12-09", recurrence=RecurrencePattern(WEEKLY, day_of_week=[0]))
next_date = recurrence_service.calculate_next_date(task)
# Returns: date(2025, 12, 16)  # Next Monday
```

---

#### `create_next_instance(task: Task) -> Task`

Create the next recurring task instance after completion.

**Input**:
- `task`: Completed recurring task

**Output**:
- `Task`: New task with updated due_date, reset status, same series_id

**Behavior**:
1. Calculate next due date
2. Create new Task with:
   - New unique ID
   - Same title, description, priority, categories
   - Same recurrence pattern
   - Same series_id
   - Status = INCOMPLETE
   - New created_at timestamp
   - Recalculated reminders (if any)

**Errors**:
- Raises `ValueError` if task has no recurrence pattern

---

#### `get_series_tasks(series_id: str) -> list[Task]`

Get all tasks in a recurring series.

**Input**:
- `series_id`: UUID of the series

**Output**:
- `list[Task]`: All tasks with matching series_id, ordered by due_date

---

#### `update_series(series_id: str, updates: dict, future_only: bool) -> int`

Update tasks in a series.

**Input**:
- `series_id`: UUID of the series
- `updates`: Dictionary of field updates
- `future_only`: If True, only update incomplete future tasks

**Output**:
- `int`: Number of tasks updated

---

#### `delete_series(series_id: str, future_only: bool) -> int`

Delete tasks in a series.

**Input**:
- `series_id`: UUID of the series
- `future_only`: If True, only delete incomplete future tasks

**Output**:
- `int`: Number of tasks deleted

---

## ReminderService

Handles reminder management and notification triggering.

### Methods

#### `add_reminder(task_id: int, offset: ReminderOffset, custom_minutes: Optional[int]) -> Reminder`

Add a reminder to a task.

**Input**:
- `task_id`: ID of the task
- `offset`: Reminder timing (AT_TIME, MINUTES_15, etc.)
- `custom_minutes`: For CUSTOM offset, minutes before

**Output**:
- `Reminder`: Created reminder with calculated trigger_time

**Behavior**:
1. Load task
2. Calculate trigger_time from due_date + due_time - offset
3. Create Reminder with unique ID
4. Save to task's reminders list

**Errors**:
- Raises `ValueError` if task not found
- Raises `ValueError` if task has no due_date
- Raises `ValueError` if CUSTOM offset without custom_minutes

---

#### `remove_reminder(reminder_id: str) -> bool`

Remove a reminder.

**Input**:
- `reminder_id`: UUID of the reminder

**Output**:
- `bool`: True if removed, False if not found

---

#### `check_due_reminders() -> list[tuple[Reminder, Task]]`

Check for reminders that should trigger now.

**Input**: None

**Output**:
- `list[tuple[Reminder, Task]]`: Reminders due now with their tasks

**Behavior**:
1. Get current UTC time
2. Find all reminders where:
   - `trigger_time` <= now
   - `shown` == False
3. Return with associated tasks

---

#### `mark_as_shown(reminder_id: str) -> bool`

Mark a reminder as shown/triggered.

**Input**:
- `reminder_id`: UUID of the reminder

**Output**:
- `bool`: True if updated, False if not found

---

#### `recalculate_reminders(task: Task) -> None`

Recalculate trigger times for all reminders on a task.

**Input**:
- `task`: Task with updated due_date/due_time

**Behavior**:
- Updates trigger_time for each reminder based on new due datetime
- Resets `shown` to False for future reminders

---

## TaskService (Extended)

Extensions to existing TaskService for recurring tasks.

### Extended Methods

#### `add_task(..., recurrence: Optional[RecurrencePattern], reminders: Optional[list]) -> Task`

**Extended Input**:
- All existing parameters
- `recurrence`: Optional recurrence pattern
- `reminders`: Optional list of reminder offsets

**Extended Behavior**:
1. Generate series_id if recurrence provided
2. Calculate reminder trigger_times if due_date provided
3. Apply default reminder from preferences if configured

---

#### `complete_task(task_id: int) -> tuple[Task, Optional[Task]]`

**Extended Output**:
- `Task`: The completed task
- `Optional[Task]`: New instance if recurring, None otherwise

**Extended Behavior**:
1. Toggle task status to COMPLETE
2. If task has recurrence:
   - Call `recurrence_service.create_next_instance()`
   - Return both completed and new task

---

## PreferencesService

Handles user preference storage and retrieval.

### Methods

#### `get_preferences() -> UserPreferences`

Get current user preferences.

**Output**:
- `UserPreferences`: Current settings (or defaults if none saved)

---

#### `update_preferences(updates: dict) -> UserPreferences`

Update user preferences.

**Input**:
- `updates`: Dictionary of preference updates

**Output**:
- `UserPreferences`: Updated preferences

**Behavior**:
- Merges updates with existing preferences
- Saves to preferences.json

---

## Validators (Extended)

### `validate_time(time_str: str) -> str`

Validate and normalize time input.

**Input**:
- `time_str`: Time string in various formats ("2:30pm", "14:30", etc.)

**Output**:
- `str`: Normalized ISO time (HH:MM:SS)

**Errors**:
- Raises `ValueError` if format is invalid

---

### `validate_recurrence(pattern: dict) -> RecurrencePattern`

Validate recurrence pattern input.

**Input**:
- `pattern`: Dictionary with frequency, interval, etc.

**Output**:
- `RecurrencePattern`: Validated pattern

**Errors**:
- Raises `ValueError` for invalid frequency
- Raises `ValueError` for invalid interval (<1)
- Raises `ValueError` for invalid day_of_week values
