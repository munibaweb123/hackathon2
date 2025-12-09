# Tasks: Professional Todo Console Application

**Input**: Design documents from `/specs/002-todo-console-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Included - spec requests "comprehensive unit tests"

**Organization**: Tasks grouped by user story (8 stories: 3 P1, 3 P2, 2 P3)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US8) this task belongs to
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization with UV and Python 3.13+

- [ ] T001 Initialize Python project with UV: `uv init todo-app --python 3.13`
- [ ] T002 Add runtime dependency: `uv add rich`
- [ ] T003 Add dev dependencies: `uv add --dev pytest pytest-cov`
- [ ] T004 [P] Create package structure: `src/todo_app/__init__.py`
- [ ] T005 [P] Create models package: `src/todo_app/models/__init__.py`
- [ ] T006 [P] Create storage package: `src/todo_app/storage/__init__.py`
- [ ] T007 [P] Create services package: `src/todo_app/services/__init__.py`
- [ ] T008 [P] Create UI package: `src/todo_app/ui/__init__.py`
- [ ] T009 [P] Create tests structure: `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`
- [ ] T010 [P] Create test fixtures file: `tests/conftest.py`
- [ ] T011 Update pyproject.toml with project metadata and script entry point

**Checkpoint**: Project structure ready, `uv run python -c "import todo_app"` succeeds

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and storage that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Models

- [ ] T012 Implement Priority enum in `src/todo_app/models/task.py` (HIGH, MEDIUM, LOW)
- [ ] T013 Implement Status enum in `src/todo_app/models/task.py` (INCOMPLETE, COMPLETE)
- [ ] T014 Implement Task dataclass in `src/todo_app/models/task.py` with all fields from data-model.md
- [ ] T015 Export models from `src/todo_app/models/__init__.py`

### Core Storage

- [ ] T016 Implement JsonStore class in `src/todo_app/storage/json_store.py` with load/save methods
- [ ] T017 Implement atomic write (temp file + rename) in `src/todo_app/storage/json_store.py`
- [ ] T018 Implement missing file handling (create empty) in `src/todo_app/storage/json_store.py`
- [ ] T019 Implement corrupted JSON handling (backup + fresh start) in `src/todo_app/storage/json_store.py`
- [ ] T020 Implement max_id tracking in metadata in `src/todo_app/storage/json_store.py`
- [ ] T021 Export storage from `src/todo_app/storage/__init__.py`

### Core UI Infrastructure

- [ ] T022 Implement Console wrapper class in `src/todo_app/ui/console.py` using rich.Console
- [ ] T023 Implement success/error/warning message methods in `src/todo_app/ui/console.py`
- [ ] T024 Export UI components from `src/todo_app/ui/__init__.py`

### Unit Tests for Foundation

- [ ] T025 [P] Write unit tests for Priority/Status enums in `tests/unit/test_models.py`
- [ ] T026 [P] Write unit tests for Task dataclass creation in `tests/unit/test_models.py`
- [ ] T027 [P] Write unit tests for JsonStore load/save in `tests/unit/test_storage.py`
- [ ] T028 [P] Write unit tests for atomic write in `tests/unit/test_storage.py`
- [ ] T029 [P] Write unit tests for missing file handling in `tests/unit/test_storage.py`
- [ ] T030 [P] Write unit tests for corrupted JSON handling in `tests/unit/test_storage.py`

**Checkpoint**: Foundation ready - `uv run pytest tests/unit/` passes, user story implementation can begin

---

## Phase 3: User Story 1 - Add New Task (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with title, description, due date, priority, and categories

**Independent Test**: Run app → Select "Add Task" → Enter all fields → Verify task appears in JSON file

### Implementation for User Story 1

- [ ] T031 [US1] Implement input validation functions in `src/todo_app/services/validators.py`:
  - validate_title (non-empty, max 100 chars)
  - validate_description (max 500 chars)
  - validate_due_date (YYYY-MM-DD format)
  - validate_priority (high/medium/low)
  - validate_categories (parse comma-separated, normalize)
- [ ] T032 [US1] Implement TaskService.add_task() in `src/todo_app/services/task_service.py`
- [ ] T033 [US1] Implement add task prompts in `src/todo_app/ui/prompts.py`:
  - prompt_title(), prompt_description(), prompt_due_date()
  - prompt_priority(), prompt_categories()
- [ ] T034 [US1] Implement add_task_flow() in `src/todo_app/ui/menu.py` (orchestrates prompts + service)
- [ ] T035 [US1] Wire add task option in main menu in `src/todo_app/ui/menu.py`

### Tests for User Story 1

- [ ] T036 [P] [US1] Write validation tests in `tests/unit/test_validation.py`:
  - test_validate_title_empty, test_validate_title_too_long
  - test_validate_description_too_long
  - test_validate_due_date_valid, test_validate_due_date_invalid
  - test_validate_priority_valid, test_validate_priority_invalid
  - test_validate_categories_parsing
- [ ] T037 [P] [US1] Write TaskService.add_task tests in `tests/unit/test_services.py`
- [ ] T038 [US1] Write integration test for add task flow in `tests/integration/test_app_flow.py`

**Checkpoint**: User Story 1 complete - Can add tasks via menu, persisted to JSON

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Display all tasks in formatted table with color-coded priorities and status indicators

**Independent Test**: Add tasks → Select "View Tasks" → Verify table shows all columns with colors

### Implementation for User Story 2

- [ ] T039 [US2] Implement task table display in `src/todo_app/ui/display.py`:
  - create_task_table() using rich.Table
  - Priority color mapping (high=red, medium=yellow, low=green)
  - Status indicator (checkmark for complete, empty box for incomplete)
- [ ] T040 [US2] Implement empty state message in `src/todo_app/ui/display.py`
- [ ] T041 [US2] Implement TaskService.get_all_tasks() in `src/todo_app/services/task_service.py`
- [ ] T042 [US2] Implement view_tasks_flow() in `src/todo_app/ui/menu.py`
- [ ] T043 [US2] Wire view tasks option in main menu in `src/todo_app/ui/menu.py`

### Tests for User Story 2

- [ ] T044 [P] [US2] Write display tests in `tests/unit/test_display.py`:
  - test_create_task_table_with_tasks
  - test_create_task_table_empty
  - test_priority_color_mapping
  - test_status_indicator
- [ ] T045 [P] [US2] Write TaskService.get_all_tasks tests in `tests/unit/test_services.py`
- [ ] T046 [US2] Write integration test for view flow in `tests/integration/test_app_flow.py`

**Checkpoint**: User Stories 1+2 complete - Can add and view tasks with formatting

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P1)

**Goal**: Toggle task completion status by ID

**Independent Test**: Add task → Mark complete by ID → Verify status changed → Toggle back

### Implementation for User Story 3

- [ ] T047 [US3] Implement TaskService.toggle_status(task_id) in `src/todo_app/services/task_service.py`
- [ ] T048 [US3] Implement TaskService.get_task_by_id(task_id) in `src/todo_app/services/task_service.py`
- [ ] T049 [US3] Implement prompt_task_id() in `src/todo_app/ui/prompts.py` with validation
- [ ] T050 [US3] Implement toggle_status_flow() in `src/todo_app/ui/menu.py`
- [ ] T051 [US3] Wire toggle status option in main menu in `src/todo_app/ui/menu.py`

### Tests for User Story 3

- [ ] T052 [P] [US3] Write toggle status tests in `tests/unit/test_services.py`:
  - test_toggle_incomplete_to_complete
  - test_toggle_complete_to_incomplete
  - test_toggle_nonexistent_task
- [ ] T053 [P] [US3] Write get_task_by_id tests in `tests/unit/test_services.py`
- [ ] T054 [US3] Write integration test for toggle flow in `tests/integration/test_app_flow.py`

**Checkpoint**: P1 stories complete - Core MVP functional (add, view, toggle)

---

## Phase 6: User Story 4 - Update Task Properties (Priority: P2)

**Goal**: Edit any task property (title, description, due date, priority, categories)

**Independent Test**: Add task → Update title → Verify change persisted → Update other fields

### Implementation for User Story 4

- [ ] T055 [US4] Implement TaskService.update_task(task_id, **updates) in `src/todo_app/services/task_service.py`
- [ ] T056 [US4] Implement update field selection submenu in `src/todo_app/ui/prompts.py`
- [ ] T057 [US4] Implement update prompts (reuse from add, allow empty to keep current) in `src/todo_app/ui/prompts.py`
- [ ] T058 [US4] Implement update_task_flow() in `src/todo_app/ui/menu.py`
- [ ] T059 [US4] Wire update task option in main menu in `src/todo_app/ui/menu.py`

### Tests for User Story 4

- [ ] T060 [P] [US4] Write update task tests in `tests/unit/test_services.py`:
  - test_update_single_field
  - test_update_multiple_fields
  - test_update_preserves_unchanged_fields
  - test_update_nonexistent_task
- [ ] T061 [US4] Write integration test for update flow in `tests/integration/test_app_flow.py`

**Checkpoint**: User Story 4 complete - Can update any task property

---

## Phase 7: User Story 5 - Delete Task with Confirmation (Priority: P2)

**Goal**: Delete tasks by ID with confirmation prompt to prevent accidents

**Independent Test**: Add task → Delete by ID → Confirm → Verify removed from JSON

### Implementation for User Story 5

- [ ] T062 [US5] Implement TaskService.delete_task(task_id) in `src/todo_app/services/task_service.py`
- [ ] T063 [US5] Implement prompt_confirmation() in `src/todo_app/ui/prompts.py` (y/n with task title)
- [ ] T064 [US5] Implement delete_task_flow() in `src/todo_app/ui/menu.py` with confirmation
- [ ] T065 [US5] Wire delete task option in main menu in `src/todo_app/ui/menu.py`

### Tests for User Story 5

- [ ] T066 [P] [US5] Write delete task tests in `tests/unit/test_services.py`:
  - test_delete_existing_task
  - test_delete_nonexistent_task
- [ ] T067 [US5] Write integration test for delete flow in `tests/integration/test_app_flow.py`

**Checkpoint**: User Story 5 complete - Can delete tasks with confirmation

---

## Phase 8: User Story 6 - Search Tasks (Priority: P2)

**Goal**: Find tasks by keyword in title or description (case-insensitive)

**Independent Test**: Add tasks with various titles → Search keyword → Verify only matching shown

### Implementation for User Story 6

- [ ] T068 [US6] Implement search_tasks(keyword) in `src/todo_app/services/search.py`
- [ ] T069 [US6] Implement prompt_search_keyword() in `src/todo_app/ui/prompts.py`
- [ ] T070 [US6] Implement search_tasks_flow() in `src/todo_app/ui/menu.py`
- [ ] T071 [US6] Wire search option in main menu in `src/todo_app/ui/menu.py`

### Tests for User Story 6

- [ ] T072 [P] [US6] Write search tests in `tests/unit/test_search.py`:
  - test_search_matches_title
  - test_search_matches_description
  - test_search_case_insensitive
  - test_search_no_matches
- [ ] T073 [US6] Write integration test for search flow in `tests/integration/test_app_flow.py`

**Checkpoint**: P2 stories complete - All CRUD + search functional

---

## Phase 9: User Story 7 - Filter Tasks (Priority: P3)

**Goal**: Filter tasks by status, priority, due date range, or category

**Independent Test**: Add varied tasks → Apply each filter type → Verify correct subset shown

### Implementation for User Story 7

- [ ] T074 [US7] Implement filter functions in `src/todo_app/services/filter.py`:
  - filter_by_status(tasks, status)
  - filter_by_priority(tasks, priority)
  - filter_by_date_range(tasks, start_date, end_date)
  - filter_by_category(tasks, category)
  - combine_filters(tasks, **filters)
- [ ] T075 [US7] Implement filter selection submenu in `src/todo_app/ui/prompts.py`
- [ ] T076 [US7] Implement prompt_date_range() in `src/todo_app/ui/prompts.py`
- [ ] T077 [US7] Implement filter_tasks_flow() in `src/todo_app/ui/menu.py`
- [ ] T078 [US7] Wire filter option in main menu in `src/todo_app/ui/menu.py`

### Tests for User Story 7

- [ ] T079 [P] [US7] Write filter tests in `tests/unit/test_filter.py`:
  - test_filter_by_status_complete
  - test_filter_by_status_incomplete
  - test_filter_by_priority
  - test_filter_by_date_range
  - test_filter_by_category
  - test_combine_multiple_filters
- [ ] T080 [US7] Write integration test for filter flow in `tests/integration/test_app_flow.py`

**Checkpoint**: User Story 7 complete - Can filter tasks by any criteria

---

## Phase 10: User Story 8 - Sort Tasks (Priority: P3)

**Goal**: Sort tasks by due date, priority, title, or creation date

**Independent Test**: Add varied tasks → Apply each sort option → Verify correct order

### Implementation for User Story 8

- [ ] T081 [US8] Implement sort functions in `src/todo_app/services/sort.py`:
  - sort_by_due_date(tasks, ascending=True)
  - sort_by_priority(tasks)
  - sort_by_title(tasks)
  - sort_by_created_at(tasks)
- [ ] T082 [US8] Implement sort selection submenu in `src/todo_app/ui/prompts.py`
- [ ] T083 [US8] Implement sort_tasks_flow() in `src/todo_app/ui/menu.py`
- [ ] T084 [US8] Wire sort option in main menu in `src/todo_app/ui/menu.py`

### Tests for User Story 8

- [ ] T085 [P] [US8] Write sort tests in `tests/unit/test_sort.py`:
  - test_sort_by_due_date_ascending
  - test_sort_by_due_date_descending
  - test_sort_by_priority
  - test_sort_by_title_alphabetical
  - test_sort_by_created_at
  - test_sort_with_none_values
- [ ] T086 [US8] Write integration test for sort flow in `tests/integration/test_app_flow.py`

**Checkpoint**: All P3 stories complete - Full feature set implemented

---

## Phase 11: Application Entry Point & Menu System

**Purpose**: Wire everything together with main menu loop and exit handling

- [ ] T087 Implement main menu display in `src/todo_app/ui/menu.py`:
  - Show all 9 options (1-8 features + 9 exit)
  - Use rich Panel for styled header
- [ ] T088 Implement main loop in `src/todo_app/ui/menu.py` with menu dispatch
- [ ] T089 Implement clean exit handling in `src/todo_app/ui/menu.py` (option 9 + Ctrl+C)
- [ ] T090 Implement entry point in `src/todo_app/__main__.py`
- [ ] T091 Verify script entry point works: `uv run todo`

**Checkpoint**: Application fully functional via `uv run python -m todo_app` or `uv run todo`

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements

- [ ] T092 [P] Add comprehensive docstrings to all public functions/classes
- [ ] T093 [P] Add type hints verification: `uv run mypy src/todo_app/` (optional)
- [ ] T094 [P] Run all tests with coverage: `uv run pytest --cov=todo_app --cov-report=term-missing`
- [ ] T095 [P] Verify PEP 8 compliance (ruff or similar)
- [ ] T096 Verify quickstart.md instructions work end-to-end
- [ ] T097 Final manual testing of all 8 user stories
- [ ] T098 Create README.md with installation and usage instructions

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation) → Phases 3-10 (User Stories) → Phase 11 (Entry Point) → Phase 12 (Polish)
                                              ↓
                                    Can run in parallel by priority:
                                    P1: US1, US2, US3 (Phases 3-5)
                                    P2: US4, US5, US6 (Phases 6-8)
                                    P3: US7, US8 (Phases 9-10)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Add) | Foundation | US2, US3 |
| US2 (View) | Foundation | US1, US3 |
| US3 (Toggle) | Foundation | US1, US2 |
| US4 (Update) | Foundation | US5, US6 |
| US5 (Delete) | Foundation | US4, US6 |
| US6 (Search) | Foundation | US4, US5 |
| US7 (Filter) | Foundation | US8 |
| US8 (Sort) | Foundation | US7 |

### Within Each User Story

1. Service layer first (business logic)
2. UI prompts second (input handling)
3. Menu flow third (orchestration)
4. Tests can run parallel with implementation

---

## Parallel Execution Examples

### Phase 2: Foundation Models (Parallel)
```
T012 Priority enum, T013 Status enum, T014 Task dataclass → all can run parallel
T025-T030 Unit tests → all can run parallel
```

### Phase 3-5: P1 Stories (Parallel if multiple developers)
```
Developer A: US1 (T031-T038)
Developer B: US2 (T039-T046)
Developer C: US3 (T047-T054)
```

### Within User Story 1 (Parallel tasks)
```
T036, T037 → Unit tests can run parallel
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundation (T012-T030)
3. Complete Phase 3: US1 Add Task (T031-T038)
4. Complete Phase 4: US2 View Tasks (T039-T046)
5. Complete Phase 5: US3 Toggle Status (T047-T054)
6. Complete Phase 11: Entry Point (T087-T091)
7. **STOP and VALIDATE**: Core MVP functional

### Incremental Delivery

- After Phase 5: MVP with Add/View/Toggle
- After Phase 8: Full CRUD + Search
- After Phase 10: Complete feature set
- After Phase 12: Production ready

---

## Task Summary

| Phase | Tasks | User Story |
|-------|-------|------------|
| 1. Setup | T001-T011 (11) | - |
| 2. Foundation | T012-T030 (19) | - |
| 3. Add Task | T031-T038 (8) | US1 (P1) |
| 4. View Tasks | T039-T046 (8) | US2 (P1) |
| 5. Toggle Status | T047-T054 (8) | US3 (P1) |
| 6. Update Task | T055-T061 (7) | US4 (P2) |
| 7. Delete Task | T062-T067 (6) | US5 (P2) |
| 8. Search | T068-T073 (6) | US6 (P2) |
| 9. Filter | T074-T080 (7) | US7 (P3) |
| 10. Sort | T081-T086 (6) | US8 (P3) |
| 11. Entry Point | T087-T091 (5) | - |
| 12. Polish | T092-T098 (7) | - |

**Total**: 98 tasks

---

## Notes

- [P] tasks = different files, no blocking dependencies
- [Story] label maps task to user story for traceability
- Each user story independently testable after completion
- Commit after each task or logical group
- Run tests frequently: `uv run pytest`
