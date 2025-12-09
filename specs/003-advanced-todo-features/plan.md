# Implementation Plan: Advanced Todo Features

**Branch**: `003-advanced-todo-features` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-advanced-todo-features/spec.md`

## Summary

Extend the existing Python console todo application with intelligent features: **recurring tasks** that auto-reschedule when completed, and **due date/time reminders** with notification support. The implementation builds on the existing Task model, JsonStore, and rich console UI, adding new models for recurrence patterns and reminders, along with a background reminder checker for console-based notifications.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: rich (console formatting), python-dateutil (recurrence calculation)
**Storage**: JSON file (`tasks.json` - extending existing JsonStore)
**Testing**: pytest with pytest-cov
**Target Platform**: Console application (cross-platform: Linux, macOS, Windows)
**Project Type**: Single project (existing structure)
**Performance Goals**: Task regeneration < 2 seconds, reminder check < 100ms
**Constraints**: No external services, offline-capable, single-user
**Scale/Scope**: Single user, unlimited tasks, local storage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Basic Task Management | MUST provide add, delete, update, view, toggle | ✅ PASS | Already implemented in existing app |
| II. Task Organization | SHOULD offer priorities, categories, search, filter, sort | ✅ PASS | Already implemented in existing app |
| III. Advanced Automation | MAY implement recurring tasks and reminders | ✅ PASS | This feature implements the MAY clause |

**Gate Result**: PASS - All MUST requirements already satisfied; this feature adds optional MAY functionality.

## Project Structure

### Documentation (this feature)

```text
specs/003-advanced-todo-features/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal API contracts)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/todo_app/
├── __init__.py
├── __main__.py          # Entry point
├── models/
│   ├── __init__.py
│   ├── task.py          # Existing - EXTEND with recurrence fields
│   ├── recurrence.py    # NEW - RecurrencePattern enum and dataclass
│   └── reminder.py      # NEW - Reminder dataclass
├── services/
│   ├── __init__.py
│   ├── task_service.py  # Existing - EXTEND for recurring task creation
│   ├── validators.py    # Existing - EXTEND for time/recurrence validation
│   ├── recurrence_service.py  # NEW - Calculate next dates, handle series
│   ├── reminder_service.py    # NEW - Check due reminders, trigger notifications
│   ├── search.py        # Existing - no changes
│   ├── filter.py        # Existing - EXTEND for recurrence filters
│   └── sort.py          # Existing - no changes
├── storage/
│   ├── __init__.py
│   ├── json_store.py    # Existing - EXTEND schema for new fields
│   └── preferences.py   # NEW - UserPreferences storage
├── ui/
│   ├── __init__.py
│   ├── console.py       # Existing - no changes
│   ├── display.py       # Existing - EXTEND for recurrence/reminder display
│   ├── menu.py          # Existing - EXTEND with new menu options
│   └── prompts.py       # Existing - EXTEND for recurrence/time input

tests/
├── unit/
│   ├── test_recurrence.py     # NEW
│   ├── test_reminder.py       # NEW
│   └── test_task_extended.py  # NEW
├── integration/
│   └── test_recurring_flow.py # NEW
└── contract/
    └── test_json_schema.py    # NEW - Validate JSON schema compatibility
```

**Structure Decision**: Extend existing single-project structure. New models and services are added as separate modules to maintain separation of concerns while preserving backward compatibility with existing tasks.json files.

## Complexity Tracking

> No violations detected - implementing optional MAY requirements from constitution.

| Area | Complexity Level | Justification |
|------|------------------|---------------|
| Recurrence calculation | Medium | Using python-dateutil for robust date math |
| Reminder notifications | Low | Console-based alerts (not browser notifications for MVP) |
| Data migration | Low | New fields are optional with defaults |
