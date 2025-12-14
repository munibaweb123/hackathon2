---
id: 0016
title: Change Task ID Type and Fix Timezone Issues
stage: refactor
date: 2025-12-14
surface: agent
model: claude-opus-4-5-20251101
feature: 003-advanced-todo-features
branch: 003-advanced-todo-features
user: YOusuf Traders
command: null
labels: ["refactor", "database", "timezone", "type-change"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - todo_web/backend/app/models/task.py
  - todo_web/backend/app/models/reminder.py
  - todo_web/backend/app/schemas/task.py
  - todo_web/backend/app/schemas/reminder.py
  - todo_web/backend/app/api/tasks.py
  - todo_web/backend/app/core/database.py
  - todo_web/todo_web_frontend/src/types/index.ts
  - todo_web/todo_web_frontend/src/lib/api-client.ts
  - todo_web/todo_web_frontend/src/hooks/use-tasks.ts
  - todo_web/todo_web_frontend/src/components/tasks/task-item.tsx
  - todo_web/todo_web_frontend/src/components/tasks/task-list.tsx
  - todo_web/todo_web_frontend/src/components/tasks/task-form.tsx
  - todo_web/todo_web_frontend/src/components/reminders/reminder-form.tsx
  - todo_web/todo_web_frontend/src/app/(dashboard)/tasks/page.tsx
  - todo_web/todo_web_frontend/src/app/(dashboard)/tasks/[id]/page.tsx
  - todo_web/todo_web_frontend/src/app/(dashboard)/reminders/page.tsx
tests:
  - null
---

## Prompt

1. Change datatype of task id from string to number
2. Fix timezone mismatch - reminder times showing wrong (7 hours off)

## Response snapshot

### Task ID Type Change (string -> number)
Changed task ID from UUID string to auto-increment integer across the entire stack:

**Backend:**
- `models/task.py`: `id: str` -> `id: Optional[int]` (auto-increment primary key)
- `models/task.py`: `parent_task_id: Optional[str]` -> `Optional[int]`
- `models/reminder.py`: `task_id: str` -> `task_id: int`
- `schemas/task.py`: Updated TaskResponse id and parent_task_id types
- `schemas/reminder.py`: Updated task_id types
- `api/tasks.py`: Updated all route parameters from `task_id: str` to `task_id: int`
- `database.py`: Added `drop_all_tables()` helper for schema reset

**Frontend:**
- `types/index.ts`: Task.id, Reminder.task_id, parent_task_id changed to `number`
- `api-client.ts`: All taskId parameters changed to `number`
- `hooks/use-tasks.ts`: Updated callback signatures
- Components: Updated all task ID types in props and handlers

### Timezone Fix
Fixed reminder/task times showing 7 hours off due to UTC conversion issues:

**Backend:**
- Added `field_serializer` to ReminderResponse and TaskResponse
- Datetime fields now serialize with timezone info (`+00:00`)

**Frontend:**
- Updated `reminder-form.tsx` to send times with local timezone offset
- Display code correctly interprets UTC times in local timezone

### Database Reset Required
User had to drop existing tables (`DROP TABLE reminders; DROP TABLE tasks;`) since column type changed from VARCHAR to INTEGER.

## Outcome

- Impact: Major refactor - changed primary key type across full stack
- Tests: null
- Files: 16 files modified
- Next prompts: Test full CRUD operations with new ID type
- Reflection: Type changes affecting primary keys require careful coordination across all layers and database migration

## Evaluation notes (flywheel)

- Failure modes observed: CORS error appeared after schema change due to backend crash from type mismatch
- Graders run and results (PASS/FAIL): Manual testing - PASS after database reset
- Prompt variant (if applicable): null
- Next experiment: Consider using Alembic migrations for future schema changes
