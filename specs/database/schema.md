# Database Specification: Schema

**Version**: 1.0.0
**Created**: 2025-12-18
**Database**: PostgreSQL (production) / SQLite (development)

## Overview

Database schema for the hackathon-todo application, designed using SQLModel (SQLAlchemy + Pydantic).

## Entity Relationship Diagram

```
┌─────────────────────┐
│        User         │
├─────────────────────┤
│ id (PK)             │
│ email (UNIQUE)      │
│ name                │
│ hashed_password     │
│ is_active           │
│ created_at          │
│ updated_at          │
└─────────┬───────────┘
          │
          │ 1:N
          │
┌─────────▼───────────┐
│        Task         │
├─────────────────────┤
│ id (PK)             │
│ owner_id (FK→User)  │
│ title               │
│ description         │
│ status              │
│ priority            │
│ due_date            │
│ created_at          │
│ updated_at          │
│ completed_at        │
└─────────────────────┘
```

## Tables

### User

Stores user account information.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | INTEGER | No | auto | PRIMARY KEY |
| email | VARCHAR(255) | No | - | UNIQUE, INDEX |
| name | VARCHAR(100) | Yes | NULL | - |
| hashed_password | VARCHAR(255) | No | - | - |
| is_active | BOOLEAN | No | TRUE | - |
| created_at | TIMESTAMP | No | NOW() | - |
| updated_at | TIMESTAMP | No | NOW() | - |

**Indexes**:
- `idx_user_email` on `email` (unique)

---

### Task

Stores task/todo items.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | INTEGER | No | auto | PRIMARY KEY |
| owner_id | INTEGER | Yes | NULL | FOREIGN KEY → user.id |
| title | VARCHAR(200) | No | - | CHECK length >= 1 |
| description | TEXT | Yes | NULL | CHECK length <= 2000 |
| status | VARCHAR(20) | No | 'pending' | CHECK in enum |
| priority | VARCHAR(10) | No | 'medium' | CHECK in enum |
| due_date | TIMESTAMP | Yes | NULL | - |
| created_at | TIMESTAMP | No | NOW() | - |
| updated_at | TIMESTAMP | No | NOW() | - |
| completed_at | TIMESTAMP | Yes | NULL | - |

**Foreign Keys**:
- `fk_task_owner` → `user.id` ON DELETE SET NULL

**Indexes**:
- `idx_task_owner_id` on `owner_id`
- `idx_task_status` on `status`
- `idx_task_due_date` on `due_date`

---

## Enumerations

### TaskStatus

| Value | Description |
|-------|-------------|
| pending | Task not started |
| in_progress | Task being worked on |
| completed | Task finished successfully |
| cancelled | Task cancelled/abandoned |

### TaskPriority

| Value | Description |
|-------|-------------|
| low | Low importance |
| medium | Normal importance (default) |
| high | High importance |
| urgent | Critical/immediate attention |

---

## Constraints

### Business Rules

1. **User email uniqueness**: Each email can only be registered once
2. **Task ownership**: Tasks must belong to a user (nullable for migration compatibility)
3. **Title length**: Task titles must be 1-200 characters
4. **Description length**: Descriptions limited to 2000 characters
5. **Completed timestamp**: Set automatically when status changes to 'completed'

### Referential Integrity

- Deleting a user sets their tasks' `owner_id` to NULL (soft orphan)
- Alternative: CASCADE delete all user tasks on user deletion

---

## Migrations

Using Alembic for schema migrations. Migration files stored in `backend/migrations/`.

### Initial Migration

```sql
-- Create user table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON user(email);

-- Create task table
CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER REFERENCES user(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    due_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_task_owner_id ON task(owner_id);
CREATE INDEX idx_task_status ON task(status);
CREATE INDEX idx_task_due_date ON task(due_date);
```

---

## Data Retention

- User accounts: Retained indefinitely while active
- Completed tasks: Retained for 1 year by default
- Cancelled tasks: Retained for 30 days, then archived
- Audit logs: Retained for 90 days
