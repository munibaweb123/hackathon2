---
id: "0003"
title: "Generate Implementation Tasks"
stage: tasks
date: 2025-12-09
surface: agent
model: claude-opus-4-5-20251101
feature: 003-advanced-todo-features
branch: 003-advanced-todo-features
user: developer
command: /sp.tasks
labels: ["task-generation", "implementation", "recurring-tasks", "reminders"]
links:
  spec: specs/003-advanced-todo-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-advanced-todo-features/tasks.md
tests:
  - N/A (task generation phase)
---

## Prompt

/sp.tasks

Generate implementation tasks from the design documents for Advanced Todo Features (recurring tasks and reminders).

## Response snapshot

Generated 61 implementation tasks organized by user story:

**Phase 1: Setup (4 tasks)**
- Add python-dateutil dependency
- Create test directories

**Phase 2: Foundational (12 tasks)**
- Core enums: RecurrenceFrequency, ReminderOffset
- Core dataclasses: RecurrencePattern, Reminder, UserPreferences
- Extend Task model with new fields
- Update JsonStore schema to v1.1
- Add validators for time and recurrence

**Phase 3: US1 - Recurring Tasks (10 tasks) - P1 MVP**
- RecurrenceService: calculate_next_date, create_next_instance
- Extend TaskService for auto-regeneration
- UI prompts and display for recurrence

**Phase 4: US2 - Due Time (5 tasks) - P1**
- Time input with flexible parsing
- Due time display and storage

**Phase 5: US3 - Reminders (11 tasks) - P2**
- ReminderService: add, check, mark_as_shown
- Console notifications on startup and after actions

**Phase 6: US4 - Series Management (7 tasks) - P3**
- Series operations: get, update, delete
- "This instance only" vs "all future" UI

**Phase 7: US5 - Preferences (7 tasks) - P3**
- PreferencesService and storage
- Settings menu and default reminder application

**Phase 8: Polish (5 tasks)**
- Recurrence filter, validation, cleanup

**Dependencies Mapped:**
- US1 + US2: Independent (P1 MVP)
- US3: Depends on US2 (due_time)
- US4: Depends on US1 (recurring tasks)
- US5: Depends on US3 (reminder system)

## Outcome

- ✅ Impact: High - Complete implementation roadmap with 61 executable tasks
- 🧪 Tests: Test tasks minimal (validation only, not TDD)
- 📁 Files: 1 created (tasks.md)
- 🔁 Next prompts: /sp.implement to begin execution
- 🧠 Reflection: Tasks follow strict checklist format; user story organization enables parallel work and incremental delivery; MVP is US1+US2

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Format validation PASS (all tasks have checkbox, ID, labels, file paths)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin implementation with Phase 1 setup
