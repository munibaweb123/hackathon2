# Research: Todo In-Memory Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-09
**Status**: Complete

## Research Summary

This document captures technical decisions and best practices research for the Todo Console App implementation.

---

## 1. Python Project Structure with UV

**Decision**: Use UV for package management with standard src-layout

**Rationale**:
- UV is a modern, fast Python package manager written in Rust
- Provides faster dependency resolution than pip/poetry
- Compatible with standard pyproject.toml configuration
- Supports Python 3.13+ as required

**Alternatives Considered**:
- pip + venv: More familiar but slower, less modern
- Poetry: Feature-rich but heavier than needed for simple CLI
- Pipenv: Less active development, slower than UV

**Implementation Notes**:
```bash
# Project initialization
uv init todo-console-app
uv add pytest --dev
```

---

## 2. Task Data Model Pattern

**Decision**: Use Python dataclass with auto-incrementing ID counter

**Rationale**:
- Dataclasses provide clean, immutable-friendly data structures
- Built into Python standard library (no dependencies)
- Auto-generates __init__, __repr__, __eq__ methods
- Type hints improve code clarity and IDE support

**Alternatives Considered**:
- NamedTuple: Less flexible for mutable status field
- Plain class: More boilerplate code
- Pydantic: Overkill for simple in-memory model (adds dependency)

**Implementation Pattern**:
```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class Task:
    title: str
    description: str = ""
    completed: bool = False
    id: int = field(default=0)
    _id_counter: ClassVar[int] = 0
```

---

## 3. In-Memory Storage Pattern

**Decision**: Use dictionary with task ID as key

**Rationale**:
- O(1) lookup, update, delete by ID
- Simple iteration for list operations
- No external dependencies
- Naturally handles ID uniqueness

**Alternatives Considered**:
- List with linear search: O(n) for ID lookup
- SQLite in-memory: Adds complexity, not needed for simple case
- Collections.OrderedDict: Unnecessary ordering overhead

**Implementation Pattern**:
```python
class TaskService:
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
```

---

## 4. CLI Menu Pattern

**Decision**: Infinite loop with numeric menu options

**Rationale**:
- Simple, familiar pattern for console apps
- Easy to extend with new options
- Clear separation of menu display and action handling
- Graceful exit with dedicated option

**Alternatives Considered**:
- argparse subcommands: Better for non-interactive CLI
- Rich/Textual TUI: Adds dependencies, overkill for basic menu
- Click framework: Adds dependency, designed for different use case

**Implementation Pattern**:
```python
def main_menu():
    while True:
        print("\n=== Todo App ===")
        print("1. Add Task")
        print("2. View Tasks")
        # ... more options
        print("6. Exit")
        choice = input("Select option: ")
        # Handle choice
```

---

## 5. Error Handling Strategy

**Decision**: Catch specific exceptions, display user-friendly messages

**Rationale**:
- Users see helpful messages, not stack traces
- Specific exceptions allow targeted handling
- Application continues running after errors
- Graceful handling of Ctrl+C (KeyboardInterrupt)

**Alternatives Considered**:
- Bare except clauses: Anti-pattern, hides bugs
- Let exceptions propagate: Poor user experience
- Return codes: Less Pythonic, harder to maintain

**Implementation Pattern**:
```python
try:
    task_id = int(input("Enter task ID: "))
except ValueError:
    print("Error: Invalid ID format")
    return
```

---

## 6. Testing Strategy

**Decision**: pytest with separate unit and integration tests

**Rationale**:
- pytest is the Python testing standard
- Clear separation of test types
- Unit tests for Task model and TaskService
- Integration tests for CLI menu flow

**Alternatives Considered**:
- unittest: More verbose, less powerful fixtures
- nose2: Less popular, fewer features than pytest
- No tests: Unacceptable for production code

**Test Structure**:
```text
tests/
├── unit/
│   ├── test_task.py        # Task model tests
│   └── test_task_service.py # Service logic tests
└── integration/
    └── test_cli.py          # Menu flow tests (with mocked input)
```

---

## Resolved Clarifications

| Item | Resolution | Source |
|------|------------|--------|
| Python version | 3.13+ | Spec constraints |
| Package manager | UV | Spec requirements |
| Storage mechanism | In-memory dict | Spec constraints (no persistence) |
| Testing framework | pytest | Best practice for Python |
| CLI framework | Standard library (no framework) | Simplicity principle |

---

## Next Steps

1. Proceed to Phase 1: Create data-model.md with Task entity definition
2. Create quickstart.md with setup and run instructions
3. Generate tasks.md via `/sp.tasks` command
