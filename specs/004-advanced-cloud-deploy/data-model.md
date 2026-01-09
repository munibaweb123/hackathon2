# Data Model: Phase V - Advanced Cloud Deployment

**Feature**: 004-advanced-cloud-deploy
**Date**: 2026-01-04
**Database**: PostgreSQL (Neon Serverless)

## Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐                │
│  │    User     │───────│    Task     │───────│     Tag     │                │
│  │  (existing) │ 1   n │             │ n   m │             │                │
│  └─────────────┘       └──────┬──────┘       └─────────────┘                │
│                               │                                              │
│                               │ 1                                            │
│                               │                                              │
│                        ┌──────┴──────┐                                       │
│                        │ Recurrence  │                                       │
│                        │   Pattern   │                                       │
│                        └─────────────┘                                       │
│                                                                              │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐                │
│  │   Audit     │       │  Task Event │       │  Reminder   │                │
│  │    Log      │       │   (Kafka)   │       │   Event     │                │
│  └─────────────┘       └─────────────┘       │   (Kafka)   │                │
│                                              └─────────────┘                │
│                                                                              │
│  ┌─────────────┐                                                             │
│  │Notification │                                                             │
│  │ Preference  │                                                             │
│  └─────────────┘                                                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Entities

### Task (Extended)

Extends existing Task model with advanced features.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User, NOT NULL | Owner of the task |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULL | Task description |
| status | ENUM | NOT NULL, DEFAULT 'pending' | pending, in_progress, completed |
| priority | ENUM | NOT NULL, DEFAULT 'none' | none, low, medium, high |
| due_date | TIMESTAMPTZ | NULL | Due date with time |
| reminder_at | TIMESTAMPTZ | NULL | When to send reminder |
| recurrence_id | UUID | FK → RecurrencePattern, NULL | Link to recurrence pattern |
| parent_task_id | UUID | FK → Task, NULL | Parent for recurring instances |
| search_vector | TSVECTOR | AUTO-GENERATED | Full-text search index |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `idx_tasks_user_id` on (user_id)
- `idx_tasks_due_date` on (due_date) WHERE due_date IS NOT NULL
- `idx_tasks_status` on (status)
- `idx_tasks_priority` on (priority)
- `idx_tasks_search` GIN on (search_vector)

**Validation Rules**:
- `reminder_at` must be before `due_date` if both are set
- `priority` must be one of: none, low, medium, high
- `status` must be one of: pending, in_progress, completed

---

### Tag

User-defined labels for task organization.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User, NOT NULL | Owner of the tag |
| name | VARCHAR(50) | NOT NULL | Tag name |
| color | VARCHAR(7) | NULL | Hex color code (e.g., #FF5733) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- `idx_tags_user_id` on (user_id)
- `idx_tags_name` UNIQUE on (user_id, name)

**Validation Rules**:
- `name` must be unique per user
- `color` must be valid hex format if provided

---

### TaskTag (Junction)

Many-to-many relationship between tasks and tags.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| task_id | UUID | FK → Task, NOT NULL | Task reference |
| tag_id | UUID | FK → Tag, NOT NULL | Tag reference |

**Indexes**:
- `pk_task_tags` PRIMARY KEY on (task_id, tag_id)
- `idx_task_tags_tag_id` on (tag_id)

---

### RecurrencePattern

Defines how a task repeats.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| frequency | ENUM | NOT NULL | daily, weekly, monthly, yearly, custom |
| interval | INTEGER | NOT NULL, DEFAULT 1 | Every N frequency units |
| day_of_week | INTEGER[] | NULL | 0-6 (Mon-Sun) for weekly |
| day_of_month | INTEGER[] | NULL | 1-31 for monthly |
| month_of_year | INTEGER[] | NULL | 1-12 for yearly |
| start_date | DATE | NOT NULL | When recurrence begins |
| end_date | DATE | NULL | When recurrence ends (NULL = never) |
| count | INTEGER | NULL | Max occurrences (NULL = unlimited) |
| status | ENUM | NOT NULL, DEFAULT 'active' | active, completed, cancelled |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Validation Rules**:
- `interval` must be >= 1
- `day_of_week` values must be 0-6
- `day_of_month` values must be 1-31
- `end_date` must be after `start_date` if provided
- When `end_date` is reached, `status` becomes 'completed'

**State Transitions**:
```
active → completed (when end_date reached or count exhausted)
active → cancelled (user cancels)
```

---

### AuditLog

Immutable record of all task operations.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | NOT NULL | User who performed action |
| entity_type | VARCHAR(50) | NOT NULL | 'task', 'tag', etc. |
| entity_id | UUID | NOT NULL | ID of affected entity |
| action | ENUM | NOT NULL | created, updated, deleted, completed |
| old_data | JSONB | NULL | Previous state |
| new_data | JSONB | NULL | New state |
| timestamp | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | When action occurred |
| correlation_id | UUID | NULL | Request correlation ID |

**Indexes**:
- `idx_audit_user_id` on (user_id)
- `idx_audit_entity` on (entity_type, entity_id)
- `idx_audit_timestamp` on (timestamp)

**Retention**: 30 days, then deleted permanently (per clarification).

---

### NotificationPreference

User settings for notification delivery.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User, UNIQUE, NOT NULL | User reference |
| in_app_enabled | BOOLEAN | NOT NULL, DEFAULT true | WebSocket/browser notifications |
| email_enabled | BOOLEAN | NOT NULL, DEFAULT true | Email notifications |
| reminder_lead_time | INTEGER | NOT NULL, DEFAULT 60 | Minutes before due date |
| quiet_hours_start | TIME | NULL | Start of quiet period |
| quiet_hours_end | TIME | NULL | End of quiet period |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Validation Rules**:
- `reminder_lead_time` must be >= 0
- If `quiet_hours_start` is set, `quiet_hours_end` must also be set

---

## Event Schemas (Kafka/Redpanda)

### TaskEvent

Published to `task-events` topic.

```json
{
  "event_id": "uuid",
  "event_type": "created | updated | completed | deleted",
  "task_id": "uuid",
  "user_id": "uuid",
  "task_data": {
    "title": "string",
    "description": "string | null",
    "status": "pending | in_progress | completed",
    "priority": "none | low | medium | high",
    "due_date": "ISO8601 | null",
    "tags": ["string"]
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

**Consumers**: Recurring Service, Audit Service

---

### ReminderEvent

Published to `reminders` topic.

```json
{
  "event_id": "uuid",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "due_at": "ISO8601",
  "remind_at": "ISO8601",
  "notification_preferences": {
    "in_app": true,
    "email": true
  },
  "timestamp": "ISO8601"
}
```

**Consumers**: Notification Service

---

### TaskUpdateEvent

Published to `task-updates` topic for real-time sync.

```json
{
  "event_id": "uuid",
  "event_type": "sync",
  "task_id": "uuid",
  "user_id": "uuid",
  "changes": {
    "field": "value"
  },
  "timestamp": "ISO8601"
}
```

**Consumers**: WebSocket Service (broadcasts to clients)

---

## Database Migrations

### Migration 001: Add Priority and Due Date

```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'none';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMPTZ;
ALTER TABLE tasks ADD COLUMN reminder_at TIMESTAMPTZ;

CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

### Migration 002: Add Tags

```sql
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(7),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, name)
);

CREATE TABLE task_tags (
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (task_id, tag_id)
);
```

### Migration 003: Add Recurrence Pattern

```sql
CREATE TYPE recurrence_frequency AS ENUM ('daily', 'weekly', 'monthly', 'yearly', 'custom');
CREATE TYPE recurrence_status AS ENUM ('active', 'completed', 'cancelled');

CREATE TABLE recurrence_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  frequency recurrence_frequency NOT NULL,
  interval INTEGER NOT NULL DEFAULT 1,
  day_of_week INTEGER[],
  day_of_month INTEGER[],
  month_of_year INTEGER[],
  start_date DATE NOT NULL,
  end_date DATE,
  count INTEGER,
  status recurrence_status NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE tasks ADD COLUMN recurrence_id UUID REFERENCES recurrence_patterns(id);
ALTER TABLE tasks ADD COLUMN parent_task_id UUID REFERENCES tasks(id);
```

### Migration 004: Add Full-Text Search

```sql
ALTER TABLE tasks ADD COLUMN search_vector TSVECTOR;

CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);

CREATE OR REPLACE FUNCTION tasks_search_trigger() RETURNS trigger AS $$
BEGIN
  NEW.search_vector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.description, ''));
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_search_update
  BEFORE INSERT OR UPDATE ON tasks
  FOR EACH ROW EXECUTE FUNCTION tasks_search_trigger();
```

### Migration 005: Add Audit Log

```sql
CREATE TYPE audit_action AS ENUM ('created', 'updated', 'deleted', 'completed');

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID NOT NULL,
  action audit_action NOT NULL,
  old_data JSONB,
  new_data JSONB,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  correlation_id UUID
);

CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
```

### Migration 006: Add Notification Preferences

```sql
CREATE TABLE notification_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  in_app_enabled BOOLEAN NOT NULL DEFAULT true,
  email_enabled BOOLEAN NOT NULL DEFAULT true,
  reminder_lead_time INTEGER NOT NULL DEFAULT 60,
  quiet_hours_start TIME,
  quiet_hours_end TIME,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## SQLModel Definitions

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date, time
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum

class Priority(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class RecurrenceFrequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"
    custom = "custom"

class RecurrenceStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: Priority = Field(default=Priority.none)
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    recurrence_id: Optional[UUID] = Field(foreign_key="recurrence_patterns.id")
    parent_task_id: Optional[UUID] = Field(foreign_key="tasks.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    tags: List["Tag"] = Relationship(back_populates="tasks", link_model="TaskTag")
    recurrence: Optional["RecurrencePattern"] = Relationship()

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    name: str = Field(max_length=50, nullable=False)
    color: Optional[str] = Field(max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List[Task] = Relationship(back_populates="tags", link_model="TaskTag")

class RecurrencePattern(SQLModel, table=True):
    __tablename__ = "recurrence_patterns"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    frequency: RecurrenceFrequency
    interval: int = Field(default=1, ge=1)
    day_of_week: Optional[List[int]] = None
    day_of_month: Optional[List[int]] = None
    month_of_year: Optional[List[int]] = None
    start_date: date
    end_date: Optional[date] = None
    count: Optional[int] = None
    status: RecurrenceStatus = Field(default=RecurrenceStatus.active)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```
