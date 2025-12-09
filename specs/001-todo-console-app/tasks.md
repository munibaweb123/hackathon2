# Tasks: Todo In-Memory Console Application

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, quickstart.md

**Tests**: Not explicitly requested in spec - omitted per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure: src/, src/models/, src/services/, src/cli/, tests/
- [x] T002 Initialize Python project with UV and create pyproject.toml per quickstart.md
- [x] T003 [P] Create src/__init__.py with package initialization
- [x] T004 [P] Create src/models/__init__.py
- [x] T005 [P] Create src/services/__init__.py
- [x] T006 [P] Create src/cli/__init__.py
- [x] T007 [P] Create tests/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create Task dataclass model in src/models/task.py with id, title, description, completed fields
- [x] T009 Add title validation (__post_init__) to reject empty titles in src/models/task.py
- [x] T010 Implement TaskService class skeleton in src/services/task_service.py with storage dict and next_id counter
- [x] T011 Create main menu loop skeleton in src/cli/menu.py with display_menu() and get_user_choice() functions
- [x] T012 Create application entry point in src/main.py that initializes TaskService and runs menu loop
- [x] T013 Implement graceful exit handler for Ctrl+C (KeyboardInterrupt) in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add New Task (Priority: P1) 🎯 MVP

**Goal**: Allow users to add tasks with title and description, auto-generating unique IDs

**Independent Test**: Run app, select "Add Task", enter title "Buy groceries" and description "Milk, eggs, bread", verify task created with ID=1 and status=incomplete

### Implementation for User Story 1

- [x] T014 [US1] Implement add_task(title, description) method in src/services/task_service.py
- [x] T015 [US1] Implement handle_add_task() function in src/cli/menu.py with input prompts for title and description
- [x] T016 [US1] Add empty title validation with error message in handle_add_task() in src/cli/menu.py
- [x] T017 [US1] Add "Add Task" menu option (option 1) to display_menu() in src/cli/menu.py
- [x] T018 [US1] Wire handle_add_task() to menu option 1 in run_menu_loop() in src/cli/menu.py
- [x] T019 [US1] Display success message with task ID after adding in src/cli/menu.py

**Checkpoint**: User Story 1 complete - can add tasks with validation

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Display all tasks with ID, title, description, and completion status indicators

**Independent Test**: Add 2-3 tasks, select "View Tasks", verify all tasks displayed with [X]/[ ] status indicators

### Implementation for User Story 2

- [x] T020 [US2] Implement get_all_tasks() method in src/services/task_service.py
- [x] T021 [US2] Implement format_task(task) helper function in src/cli/menu.py with [X]/[ ] status display
- [x] T022 [US2] Implement handle_view_tasks() function in src/cli/menu.py
- [x] T023 [US2] Add "No tasks found" message for empty list in handle_view_tasks() in src/cli/menu.py
- [x] T024 [US2] Add "View Tasks" menu option (option 2) to display_menu() in src/cli/menu.py
- [x] T025 [US2] Wire handle_view_tasks() to menu option 2 in run_menu_loop() in src/cli/menu.py

**Checkpoint**: User Stories 1 AND 2 complete - can add and view tasks

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Allow users to toggle task completion status by ID

**Independent Test**: Add task, select "Mark Complete" with ID 1, verify status changes to [X], then "Mark Incomplete" to toggle back to [ ]

### Implementation for User Story 3

- [x] T026 [US3] Implement mark_complete(task_id) method in src/services/task_service.py
- [x] T027 [US3] Implement mark_incomplete(task_id) method in src/services/task_service.py
- [x] T028 [US3] Implement handle_mark_complete() function in src/cli/menu.py with ID input
- [x] T029 [US3] Implement handle_mark_incomplete() function in src/cli/menu.py with ID input
- [x] T030 [US3] Add "Task not found" error handling in mark complete/incomplete handlers in src/cli/menu.py
- [x] T031 [US3] Add "Invalid ID format" error handling for non-numeric input in src/cli/menu.py
- [x] T032 [US3] Add "Mark Complete" (option 3) and "Mark Incomplete" (option 4) to display_menu() in src/cli/menu.py
- [x] T033 [US3] Wire mark complete/incomplete handlers to menu options 3 and 4 in src/cli/menu.py

**Checkpoint**: User Stories 1, 2, AND 3 complete - can add, view, and toggle completion

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Allow users to update task title and/or description by ID, preserving unchanged fields

**Independent Test**: Add task, select "Update Task" with ID 1, enter new title, verify title updated while description preserved

### Implementation for User Story 4

- [x] T034 [US4] Implement get_task(task_id) method in src/services/task_service.py
- [x] T035 [US4] Implement update_task(task_id, title, description) method in src/services/task_service.py
- [x] T036 [US4] Implement handle_update_task() function in src/cli/menu.py with ID and field inputs
- [x] T037 [US4] Add "press Enter to keep current value" prompt logic in handle_update_task() in src/cli/menu.py
- [x] T038 [US4] Add "Task not found" error handling in handle_update_task() in src/cli/menu.py
- [x] T039 [US4] Add "Update Task" menu option (option 5) to display_menu() in src/cli/menu.py
- [x] T040 [US4] Wire handle_update_task() to menu option 5 in run_menu_loop() in src/cli/menu.py

**Checkpoint**: User Stories 1-4 complete - full CRUD except delete

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Allow users to permanently delete tasks by ID

**Independent Test**: Add task, select "Delete Task" with ID 1, verify task removed from view list

### Implementation for User Story 5

- [x] T041 [US5] Implement delete_task(task_id) method in src/services/task_service.py
- [x] T042 [US5] Implement handle_delete_task() function in src/cli/menu.py with ID input
- [x] T043 [US5] Add "Task not found" error handling in handle_delete_task() in src/cli/menu.py
- [x] T044 [US5] Add success message after deletion in handle_delete_task() in src/cli/menu.py
- [x] T045 [US5] Add "Delete Task" menu option (option 6) to display_menu() in src/cli/menu.py
- [x] T046 [US5] Wire handle_delete_task() to menu option 6 in run_menu_loop() in src/cli/menu.py

**Checkpoint**: All 5 user stories complete - full todo app functionality

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T047 Add "Exit" menu option (option 7) with goodbye message in src/cli/menu.py
- [x] T048 Ensure consistent error message format across all handlers in src/cli/menu.py
- [x] T049 Add clear screen or separator between operations for readability in src/cli/menu.py
- [x] T050 Update README.md with setup and usage instructions per quickstart.md
- [x] T051 Run manual validation following quickstart.md test scenarios
- [x] T052 Clean up any TODO comments or debug statements in all src/ files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 priority and can run in parallel
  - US3 and US4 are both P2 priority and can run in parallel (after P1)
  - US5 is P3 priority (after P2)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational - Benefits from US1+US2 for testing
- **User Story 4 (P2)**: Can start after Foundational - Requires get_task() which can be implemented here
- **User Story 5 (P3)**: Can start after Foundational - No dependencies on other stories

### Within Each User Story

- Service methods before CLI handlers
- Menu option registration after handler implementation
- Error handling within handler implementation

### Parallel Opportunities

**Phase 1 (all [P] tasks)**:
```bash
# Can run in parallel:
T003: src/__init__.py
T004: src/models/__init__.py
T005: src/services/__init__.py
T006: src/cli/__init__.py
T007: tests/__init__.py
```

**Phase 3-4 (P1 stories can run in parallel)**:
```bash
# Developer A: User Story 1
T014-T019: Add Task functionality

# Developer B: User Story 2
T020-T025: View Tasks functionality
```

**Phase 5-6 (P2 stories can run in parallel)**:
```bash
# Developer A: User Story 3
T026-T033: Mark Complete/Incomplete

# Developer B: User Story 4
T034-T040: Update Task
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Test adding and viewing tasks
6. This is a minimal working todo app!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 + US2 → Can add and view tasks (MVP!)
3. Add US3 → Can mark complete/incomplete
4. Add US4 → Can update tasks
5. Add US5 → Can delete tasks
6. Polish → Production ready

### Single Developer Strategy

Execute phases sequentially in priority order:
1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → **Demo MVP**
2. Phase 5 → Phase 6 → Phase 7 → Phase 8 → **Complete**

---

## Summary

| Phase | User Story | Priority | Task Count |
|-------|------------|----------|------------|
| 1 | Setup | - | 7 |
| 2 | Foundational | - | 6 |
| 3 | Add Task | P1 | 6 |
| 4 | View Tasks | P1 | 6 |
| 5 | Mark Complete/Incomplete | P2 | 8 |
| 6 | Update Task | P2 | 7 |
| 7 | Delete Task | P3 | 6 |
| 8 | Polish | - | 6 |
| **Total** | | | **52** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- No test tasks generated (not explicitly requested in spec)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
