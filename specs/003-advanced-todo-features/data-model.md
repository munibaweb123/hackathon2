# Data Model: Advanced Todo Features

**Feature**: 003-advanced-todo-features
**Date**: 2025-12-09
**Schema Version**: 1.1

## Entity Definitions

### 1. RecurrenceFrequency (Enum)

Defines how often a task repeats.

| Value | Description |
|-------|-------------|
| `DAILY` | Repeats every N days |
| `WEEKLY` | Repeats every N weeks on specific day(s) |
| `MONTHLY` | Repeats every N months on specific day |
| `CUSTOM` | Repeats every N days (flexible interval) |

---

### 2. RecurrencePattern (Dataclass)

Defines the complete recurrence rule for a task.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `frequency` | RecurrenceFrequency | Yes | - | How often the task repeats |
| `interval` | int | No | 1 | Every N periods (e.g., every 2 weeks) |
| `day_of_week` | list[int] | No | [] | For WEEKLY: 0=Mon, 1=Tue, ..., 6=Sun |
| `day_of_month` | int | No | None | For MONTHLY: 1-31 (adjusted for short months) |
| `end_date` | str | No | None | ISO date when recurrence stops |

**Validation Rules**:
- `interval` must be >= 1
- `day_of_week` values must be 0-6
- `day_of_month` must be 1-31
- `end_date` must be valid ISO date if provided

**Example Patterns**:
```python
# Daily
RecurrencePattern(frequency=DAILY, interval=1)

# Every Monday and Wednesday
RecurrencePattern(frequency=WEEKLY, interval=1, day_of_week=[0, 2])

# Monthly on the 15th
RecurrencePattern(frequency=MONTHLY, interval=1, day_of_month=15)

# Every 3 days
RecurrencePattern(frequency=CUSTOM, interval=3)
```

---

### 3. ReminderOffset (Enum)

Pre-defined reminder timing options.

| Value | Description | Minutes Before |
|-------|-------------|----------------|
| `AT_TIME` | At the due time | 0 |
| `MINUTES_15` | 15 minutes before | 15 |
| `MINUTES_30` | 30 minutes before | 30 |
| `HOUR_1` | 1 hour before | 60 |
| `HOURS_2` | 2 hours before | 120 |
| `DAY_1` | 1 day before | 1440 |
| `CUSTOM` | Custom minutes | (user-defined) |

---

### 4. Reminder (Dataclass)

A reminder linked to a specific task.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | str | Yes | UUID | Unique reminder identifier |
| `task_id` | int | Yes | - | ID of the associated task |
| `offset` | ReminderOffset | Yes | - | When to trigger relative to due time |
| `custom_minutes` | int | No | None | For CUSTOM offset: minutes before |
| `trigger_time` | str | Yes | - | Calculated ISO datetime to trigger |
| `shown` | bool | No | False | Whether notification was displayed |

**Validation Rules**:
- `custom_minutes` required if `offset` is CUSTOM
- `trigger_time` must be calculated from task due datetime minus offset

---

### 5. Task (Extended)

Existing Task entity with new optional fields.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | int | Yes | - | Unique sequential identifier |
| `title` | str | Yes | - | Task title (1-100 chars) |
| `description` | str | No | "" | Task description (0-500 chars) |
| `priority` | Priority | No | MEDIUM | HIGH, MEDIUM, LOW |
| `status` | Status | No | INCOMPLETE | INCOMPLETE, COMPLETE |
| `due_date` | str | No | None | ISO date (YYYY-MM-DD) |
| `due_time` | str | No | None | **NEW**: ISO time (HH:MM:SS) or None |
| `categories` | list[str] | No | [] | Organization tags |
| `created_at` | str | Yes | now | ISO datetime |
| `recurrence` | RecurrencePattern | No | None | **NEW**: Recurrence rule |
| `series_id` | str | No | None | **NEW**: UUID linking recurring instances |
| `reminders` | list[Reminder] | No | [] | **NEW**: Task reminders |

**State Transitions**:
```
INCOMPLETE --[toggle/complete]--> COMPLETE
    |                                |
    |                                | (if has recurrence)
    |                                v
    |                         [Create new instance]
    |                         with next due date
    |                                |
    v                                v
COMPLETE  <--[toggle]--      INCOMPLETE (new)
```

**Backward Compatibility**:
- All new fields have defaults
- `from_dict` handles missing fields gracefully
- Existing tasks load without modification

---

### 6. UserPreferences (Dataclass)

User settings stored in `preferences.json`.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `default_reminder` | ReminderOffset | No | None | Auto-add reminder to new tasks |
| `default_reminder_custom` | int | No | None | Custom minutes if default is CUSTOM |
| `notifications_enabled` | bool | No | True | Whether to show notifications |

---

## JSON Schema (v1.1)

### tasks.json

```json
{
  "metadata": {
    "version": "1.1",
    "max_id": 5,
    "last_modified": "2025-12-09T14:30:00Z"
  },
  "tasks": [
    {
      "id": 1,
      "title": "Weekly Team Meeting",
      "description": "Standup with the team",
      "priority": "high",
      "status": "incomplete",
      "due_date": "2025-12-09",
      "due_time": "10:00:00",
      "categories": ["work", "meeting"],
      "created_at": "2025-12-01T09:00:00Z",
      "recurrence": {
        "frequency": "weekly",
        "interval": 1,
        "day_of_week": [0]
      },
      "series_id": "550e8400-e29b-41d4-a716-446655440000",
      "reminders": [
        {
          "id": "reminder-uuid-1",
          "task_id": 1,
          "offset": "hour_1",
          "trigger_time": "2025-12-09T09:00:00Z",
          "shown": false
        }
      ]
    }
  ]
}
```

### preferences.json

```json
{
  "default_reminder": "minutes_30",
  "default_reminder_custom": null,
  "notifications_enabled": true
}
```

---

## Relationships

```
┌─────────────────┐
│      Task       │
├─────────────────┤
│ id              │◄──────────────┐
│ title           │               │
│ due_date        │               │
│ due_time        │               │
│ recurrence ─────┼───► RecurrencePattern
│ series_id       │               │
│ reminders ──────┼───► Reminder[]│
└─────────────────┘               │
        ▲                         │
        │                         │
        └─────────────────────────┘
              (task_id)

┌─────────────────┐
│ UserPreferences │ (separate file)
├─────────────────┤
│ default_reminder│
│ notifications   │
└─────────────────┘
```

---

## Migration Notes

1. **Schema version**: Bumped from 1.0 to 1.1
2. **No breaking changes**: All new fields are optional
3. **Lazy migration**: Old files upgrade on first save
4. **Validation**: New fields validated on task creation/update only
