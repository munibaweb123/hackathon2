# Data Model: Hackathon Todo Application

**Date**: 2025-12-18
**Feature**: 001-hackathon-todo-monorepo
**Source**: Extracted from existing `todo_web/backend/app/models/`

## Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                             User                                  │
│  (Better Auth managed - read-only in backend)                    │
├──────────────────────────────────────────────────────────────────┤
│  id: str (PK, Better Auth format)                                │
│  email: str (UNIQUE)                                             │
│  name: str?                                                      │
│  email_verified: datetime?                                       │
│  image: str? (avatar URL)                                        │
│  created_at: datetime                                            │
│  updated_at: datetime                                            │
└───────────────────────┬───────────────────┬─────────────────────┘
                        │ 1:N               │ 1:1
         ┌──────────────▼──────────┐   ┌────▼────────────────────┐
         │          Task           │   │    UserPreference       │
         ├─────────────────────────┤   ├─────────────────────────┤
         │ id: int (PK)            │   │ id: str (PK, UUID)      │
         │ title: str              │   │ user_id: str (FK→User)  │
         │ description: str?       │   │ theme: enum             │
         │ completed: bool         │   │ language: str           │
         │ priority: enum          │   │ notifications: enum     │
         │ due_date: datetime?     │   │ default_view: str       │
         │ user_id: str (FK→User)  │   │ show_completed: bool    │
         │ is_recurring: bool      │   │ work_hours: str         │
         │ recurrence_pattern: enum│   │ custom_settings: JSON   │
         │ recurrence_interval: int│   └─────────────────────────┘
         │ recurrence_end_date: dt │
         │ parent_task_id: int?    │
         │ created_at: datetime    │
         │ updated_at: datetime    │
         └───────────────┬─────────┘
                         │ 1:N
              ┌──────────▼──────────┐
              │      Reminder       │
              ├─────────────────────┤
              │ id: str (PK, UUID)  │
              │ task_id: int (FK)   │
              │ user_id: str (FK)   │
              │ reminder_time: dt   │
              │ reminder_type: enum │
              │ status: enum        │
              │ message: str?       │
              │ created_at: datetime│
              │ updated_at: datetime│
              └─────────────────────┘
```

## Entities

### User (Better Auth Managed)

Aligned with Better Auth schema. Backend reads user data but doesn't create users.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PK | Better Auth generated ID |
| email | str | UNIQUE, NOT NULL | User email |
| name | str | nullable | Display name |
| email_verified | datetime | nullable | Email verification timestamp |
| image | str | nullable | Profile image URL |
| created_at | datetime | NOT NULL | Account creation time |
| updated_at | datetime | NOT NULL | Last modification time |

### Task

Core todo item entity with recurring task support.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PK, AUTO | Unique task identifier |
| title | str | NOT NULL, 1-255 chars | Task title |
| description | str | nullable, max 1000 | Task details |
| completed | bool | default: false | Completion status |
| priority | Priority | default: MEDIUM | LOW/MEDIUM/HIGH |
| due_date | datetime | nullable | When task is due |
| user_id | str | FK→User, NOT NULL | Owner |
| is_recurring | bool | default: false | Recurring flag |
| recurrence_pattern | RecurrencePattern | nullable | DAILY/WEEKLY/BIWEEKLY/MONTHLY/YEARLY/CUSTOM |
| recurrence_interval | int | default: 1 | Repeat every N periods |
| recurrence_end_date | datetime | nullable | Stop recurring after |
| parent_task_id | int | FK→Task, nullable | Parent for recurring instances |
| created_at | datetime | NOT NULL | Creation timestamp |
| updated_at | datetime | NOT NULL | Last update timestamp |

**Indexes**: title, user_id

### Reminder

Task notification scheduling.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PK, UUID | Unique reminder ID |
| task_id | int | FK→Task, NOT NULL | Associated task |
| user_id | str | FK→User, NOT NULL | Reminder owner |
| reminder_time | datetime | NOT NULL, indexed | When to send |
| reminder_type | ReminderType | default: PUSH | EMAIL/PUSH/SMS |
| status | ReminderStatus | default: PENDING | PENDING/SENT/CANCELLED |
| message | str | nullable, max 500 | Custom message |
| created_at | datetime | NOT NULL | Creation timestamp |
| updated_at | datetime | NOT NULL | Last update timestamp |

**Indexes**: task_id, user_id, reminder_time

### UserPreference

User settings and display preferences.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PK, UUID | Preference record ID |
| user_id | str | FK→User, UNIQUE | One preference per user |
| theme | Theme | default: AUTO | LIGHT/DARK/AUTO |
| language | str | default: "en" | ISO language code |
| task_notifications | NotificationPreference | default: ALL | ALL/MUTE/SCHEDULED |
| reminder_notifications | NotificationPreference | default: ALL | ALL/MUTE/SCHEDULED |
| email_notifications | bool | default: true | Email alerts enabled |
| default_view | str | default: "list" | list/grid/calendar |
| show_completed_tasks | bool | default: true | Show completed |
| group_by | str | default: "none" | none/priority/due_date/category |
| auto_archive_completed | bool | default: false | Auto archive |
| auto_snooze_time | int | nullable | Snooze duration (minutes) |
| work_hours_start | str | default: "09:00" | Work hours start (HH:MM) |
| work_hours_end | str | default: "17:00" | Work hours end (HH:MM) |
| custom_settings | str | nullable | JSON for additional settings |
| created_at | datetime | NOT NULL | Creation timestamp |
| updated_at | datetime | NOT NULL | Last update timestamp |

**Indexes**: user_id (unique)

## Enumerations

### Priority
- `LOW` - Low importance
- `MEDIUM` - Normal importance (default)
- `HIGH` - High importance

### RecurrencePattern
- `DAILY` - Every day
- `WEEKLY` - Every week
- `BIWEEKLY` - Every two weeks
- `MONTHLY` - Every month
- `YEARLY` - Every year
- `CUSTOM` - Custom interval

### ReminderType
- `EMAIL` - Email notification
- `PUSH` - Push notification (default)
- `SMS` - SMS notification (future)

### ReminderStatus
- `PENDING` - Not yet sent (default)
- `SENT` - Successfully delivered
- `CANCELLED` - Reminder cancelled

### Theme
- `LIGHT` - Light mode
- `DARK` - Dark mode
- `AUTO` - Follow system (default)

### NotificationPreference
- `ALL` - All notifications (default)
- `MUTE` - No notifications
- `SCHEDULED` - Only during work hours

## Relationships

| From | To | Type | Description |
|------|-----|------|-------------|
| User | Task | 1:N | User owns multiple tasks |
| User | UserPreference | 1:1 | One preference record per user |
| Task | Reminder | 1:N | Task can have multiple reminders |
| Task | Task | 1:N | Parent→child for recurring |
| Reminder | Task | N:1 | Reminder belongs to task |

## Validation Rules

1. **Task title**: Required, 1-255 characters
2. **Task description**: Optional, max 1000 characters
3. **Reminder message**: Optional, max 500 characters
4. **User ID format**: Better Auth format (string)
5. **Recurrence**: If is_recurring=true, recurrence_pattern is required
6. **Work hours**: Valid HH:MM format (00:00-23:59)
