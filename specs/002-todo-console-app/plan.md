# Implementation Plan: Professional Todo Console Application

**Branch**: `002-todo-console-app` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todo-console-app/spec.md`

## Summary

Build a professional console-based todo application using Python 3.13+ with UV package manager. The application provides full CRUD operations for tasks with rich formatting, color-coded priorities, JSON file persistence, and advanced organization features (search, filter, sort). Implementation uses modular architecture with dataclasses for models, rich library for console UI, and pytest for testing.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: rich (console formatting)
**Storage**: JSON file (`tasks.json` in working directory)
**Testing**: pytest, pytest-cov
**Target Platform**: Cross-platform console (Linux, macOS, Windows Terminal)
**Project Type**: Single project (console application)
**Performance Goals**: Instant response for up to 500 tasks, immediate persistence
**Constraints**: Single-user, file-based storage, no external services
**Scale/Scope**: Up to 500 tasks, 9 menu options, single JSON file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| I. Basic Task Management | MUST: add, delete, update, view, toggle complete | ✅ PASS | FR-001 to FR-009 |
| II. Task Organization | SHOULD: priorities, categories, search, filter, sort | ✅ PASS | FR-015 to FR-025 |
| III. Advanced Automation | MAY: recurring tasks, reminders | ⏭️ N/A | Explicitly out of scope |

**Gate Result**: ✅ PASS - All MUST requirements covered, SHOULD requirements implemented, MAY requirements deferred appropriately.

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-console-app/
├── plan.md              # This file
├── research.md          # Phase 0 output - technical decisions
├── data-model.md        # Phase 1 output - Task entity definition
├── quickstart.md        # Phase 1 output - setup instructions
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
src/
└── todo_app/
    ├── __init__.py          # Package initialization
    ├── __main__.py          # Entry point (main loop)
    ├── models/
    │   ├── __init__.py
    │   └── task.py          # Task dataclass, Priority/Status enums
    ├── storage/
    │   ├── __init__.py
    │   └── json_store.py    # JSON persistence layer
    ├── services/
    │   ├── __init__.py
    │   ├── task_service.py  # CRUD operations
    │   ├── search.py        # Search functionality
    │   ├── filter.py        # Filter functionality
    │   └── sort.py          # Sort functionality
    └── ui/
        ├── __init__.py
        ├── console.py       # Rich console wrapper
        ├── menu.py          # Main menu system
        ├── prompts.py       # Input prompts with validation
        └── display.py       # Task table display

tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_models.py       # Task model tests
│   ├── test_storage.py      # JSON store tests
│   ├── test_services.py     # Service layer tests
│   └── test_validation.py   # Input validation tests
└── integration/
    ├── __init__.py
    └── test_app_flow.py     # End-to-end workflow tests
```

**Structure Decision**: Single project structure selected. Console application with clear separation:
- **models/**: Pure data structures with no dependencies
- **storage/**: JSON file I/O, isolated from business logic
- **services/**: Business logic, operates on models
- **ui/**: All console interaction via rich library

## Module Responsibilities

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| models/task.py | Task dataclass, enums | None (stdlib only) |
| storage/json_store.py | Load/save JSON, atomic writes | models |
| services/task_service.py | CRUD operations | models, storage |
| services/search.py | Keyword search | models |
| services/filter.py | Filter by criteria | models |
| services/sort.py | Sort by property | models |
| ui/console.py | Rich console wrapper | rich |
| ui/menu.py | Main menu loop | ui/console, services |
| ui/prompts.py | Input with validation | ui/console |
| ui/display.py | Task table rendering | ui/console, models |

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data model | Python dataclass | Type safety, minimal boilerplate |
| ID strategy | Sequential, never reused | User-friendly, simple implementation |
| Persistence | JSON with atomic writes | Human-readable, crash-safe |
| UI library | rich | Best-in-class console formatting |
| Testing | pytest | Standard, excellent fixtures |
| Validation | Dedicated functions | Reusable, testable |

## Complexity Tracking

> No constitution violations - no entries needed.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |

## Phase Outputs

### Phase 0: Research
- [x] `research.md` - Technical decisions documented

### Phase 1: Design
- [x] `data-model.md` - Task entity with validation rules
- [x] `quickstart.md` - Setup and run instructions
- [ ] `contracts/` - N/A (no external APIs)

### Phase 2: Tasks (next step)
- [ ] `tasks.md` - Implementation tasks (run `/sp.tasks`)

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Implement in priority order (P1 → P2 → P3)
3. Write tests alongside implementation
4. Validate against spec acceptance scenarios
