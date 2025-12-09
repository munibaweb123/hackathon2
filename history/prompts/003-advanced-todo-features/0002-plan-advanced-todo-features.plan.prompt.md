---
id: "0002"
title: "Plan Advanced Todo Features"
stage: plan
date: 2025-12-09
surface: agent
model: claude-opus-4-5-20251101
feature: 003-advanced-todo-features
branch: 003-advanced-todo-features
user: developer
command: /sp.plan
labels: ["planning", "architecture", "recurring-tasks", "reminders"]
links:
  spec: specs/003-advanced-todo-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-advanced-todo-features/plan.md
  - specs/003-advanced-todo-features/research.md
  - specs/003-advanced-todo-features/data-model.md
  - specs/003-advanced-todo-features/contracts/service-interfaces.md
  - specs/003-advanced-todo-features/quickstart.md
  - CLAUDE.md
tests:
  - N/A (planning phase)
---

## Prompt

/sp.plan

Execute implementation planning workflow for the Advanced Todo Features specification (recurring tasks and reminders).

## Response snapshot

Completed Phase 0 and Phase 1 planning:

**Phase 0 - Research (research.md)**:
- Recurrence calculation: python-dateutil (rrule, relativedelta)
- Timezone handling: Store UTC, display local
- Console notifications: Check on startup/action, rich Panel alerts
- Series management: series_id UUID linking instances
- Backward compatibility: Optional fields with defaults
- Time parsing: dateutil.parser for flexible input

**Phase 1 - Design**:

*Data Model (data-model.md)*:
- RecurrenceFrequency enum (DAILY, WEEKLY, MONTHLY, CUSTOM)
- RecurrencePattern dataclass
- ReminderOffset enum with pre-defined timing options
- Reminder dataclass
- Extended Task with due_time, recurrence, series_id, reminders
- UserPreferences for default settings
- JSON schema v1.1 (backward compatible)

*Service Interfaces (contracts/service-interfaces.md)*:
- RecurrenceService: calculate_next_date, create_next_instance, series management
- ReminderService: add/remove/check reminders, mark as shown
- Extended TaskService for recurring task flows
- PreferencesService for user settings
- Extended validators for time and recurrence input

*Quickstart (quickstart.md)*:
- Development order: Models → Services → Validators → Storage → UI
- File checklist with 18 files to create/modify
- Testing workflow and common issues

**Constitution Check**: PASS - Implements MAY clause for advanced automation

## Outcome

- ✅ Impact: High - Complete architectural plan for advanced features
- 🧪 Tests: N/A - planning phase
- 📁 Files: 5 planning artifacts created, 1 context file updated
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Clean separation of concerns; python-dateutil solves complex date math; console notification approach is pragmatic for hackathon scope

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task generation
