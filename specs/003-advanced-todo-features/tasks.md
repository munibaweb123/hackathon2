# Tasks: Advanced Todo Features

**Input**: Design documents from `/specs/003-advanced-todo-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - test tasks are minimal (validation only)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add python-dateutil dependency and prepare project structure

- [x] T001 Add python-dateutil dependency to pyproject.toml
- [x] T002 Run `uv sync` to install new dependency
- [x] T003 [P] Create tests/unit/ directory structure if not exists
- [x] T004 [P] Create tests/integration/ directory structure if not exists

---

## Phase 2: Foundational (Core Models & Storage)

**Purpose**: Core models and storage extensions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Enums and Dataclasses

- [x] T005 [P] Create RecurrenceFrequency enum and RecurrencePattern dataclass in src/todo_app/models/recurrence.py
- [x] T006 [P] Create ReminderOffset enum and Reminder dataclass in src/todo_app/models/reminder.py
- [x] T007 [P] Create UserPreferences dataclass in src/todo_app/storage/preferences.py
- [x] T008 Update src/todo_app/models/__init__.py to export new models

### Extend Task Model

- [x] T009 Add due_time, recurrence, series_id, reminders fields to Task in src/todo_app/models/task.py
- [x] T010 Update Task.to_dict() to serialize new fields in src/todo_app/models/task.py
- [x] T011 Update Task.from_dict() to deserialize new fields with defaults in src/todo_app/models/task.py

### Extend Storage

- [x] T012 Update JsonStore schema version to 1.1 in src/todo_app/storage/json_store.py
- [x] T013 [P] Implement PreferencesStore load/save in src/todo_app/storage/preferences.py
- [x] T014 Update src/todo_app/storage/__init__.py to export preferences

### Core Validators

- [x] T015 [P] Add validate_time() for flexible time parsing in src/todo_app/services/validators.py
- [x] T016 [P] Add validate_recurrence() for pattern validation in src/todo_app/services/validators.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create Recurring Task (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with recurrence patterns (daily/weekly/monthly/custom) that auto-regenerate when completed

**Independent Test**: Create a recurring weekly task, mark it complete, verify new instance is auto-created with next week's due date

### Implementation for User Story 1

- [x] T017 [US1] Implement calculate_next_date() in src/todo_app/services/recurrence_service.py
- [x] T018 [US1] Implement create_next_instance() in src/todo_app/services/recurrence_service.py
- [x] T019 [US1] Add generate_series_id() helper in src/todo_app/services/recurrence_service.py
- [x] T020 [US1] Update src/todo_app/services/__init__.py to export recurrence_service
- [x] T021 [US1] Extend TaskService.add_task() to accept recurrence pattern in src/todo_app/services/task_service.py
- [x] T022 [US1] Extend TaskService to auto-create next instance on completion in src/todo_app/services/task_service.py
- [x] T023 [US1] Add prompt_recurrence() for recurrence input in src/todo_app/ui/prompts.py
- [x] T024 [US1] Update _add_task_flow() in src/todo_app/ui/menu.py to prompt for recurrence
- [x] T025 [US1] Add recurrence display to task details in src/todo_app/ui/display.py
- [x] T026 [US1] Show "Next instance created" message after completing recurring task in src/todo_app/ui/menu.py

**Checkpoint**: User Story 1 complete - recurring tasks auto-regenerate on completion

---

## Phase 4: User Story 2 - Set Due Date with Time (Priority: P1)

**Goal**: Users can set specific due times (not just dates) for their tasks

**Independent Test**: Create a task with due date "2025-12-15" and time "14:30", verify both are stored and displayed correctly

### Implementation for User Story 2

- [x] T027 [US2] Add prompt_due_time() for time input with flexible parsing in src/todo_app/ui/prompts.py
- [x] T028 [US2] Update _add_task_flow() in src/todo_app/ui/menu.py to prompt for due time
- [x] T029 [US2] Update task display to show due time alongside date in src/todo_app/ui/display.py
- [x] T030 [US2] Handle default time (23:59) when only date is provided in src/todo_app/services/task_service.py
- [x] T031 [US2] Ensure due_time persists correctly through JsonStore in src/todo_app/storage/json_store.py

**Checkpoint**: User Story 2 complete - tasks can have precise due times

---

## Phase 5: User Story 3 - Receive Reminder Notifications (Priority: P2)

**Goal**: Users can set reminders that trigger console notifications before task deadlines

**Independent Test**: Set a task due in 1 minute with a reminder, wait for trigger time, verify notification appears

### Implementation for User Story 3

- [x] T032 [US3] Implement add_reminder() in src/todo_app/services/reminder_service.py
- [x] T033 [US3] Implement check_due_reminders() in src/todo_app/services/reminder_service.py
- [x] T034 [US3] Implement mark_as_shown() in src/todo_app/services/reminder_service.py
- [x] T035 [US3] Implement recalculate_reminders() for updated due dates in src/todo_app/services/reminder_service.py
- [x] T036 [US3] Update src/todo_app/services/__init__.py to export reminder_service
- [x] T037 [US3] Add prompt_reminder() for reminder offset selection in src/todo_app/ui/prompts.py
- [x] T038 [US3] Update _add_task_flow() to prompt for reminders in src/todo_app/ui/menu.py
- [x] T039 [US3] Add reminder display to task details in src/todo_app/ui/display.py
- [x] T040 [US3] Implement show_reminder_notification() using rich Panel in src/todo_app/ui/display.py
- [x] T041 [US3] Check and display due reminders on app startup in src/todo_app/__main__.py
- [x] T042 [US3] Check and display due reminders after each menu action in src/todo_app/ui/menu.py

**Checkpoint**: User Story 3 complete - reminders trigger console notifications

---

## Phase 6: User Story 4 - Manage Recurring Task Series (Priority: P3)

**Goal**: Users can edit or delete entire recurring series, or just single instances

**Independent Test**: Edit a recurring task, choose "all future instances", verify all future tasks are updated

### Implementation for User Story 4

- [x] T043 [US4] Implement get_series_tasks() in src/todo_app/services/recurrence_service.py
- [x] T044 [US4] Implement update_series() in src/todo_app/services/recurrence_service.py
- [x] T045 [US4] Implement delete_series() in src/todo_app/services/recurrence_service.py
- [x] T046 [US4] Add prompt for "this instance only" vs "all future instances" in src/todo_app/ui/prompts.py
- [x] T047 [US4] Update _update_task_flow() to handle series editing in src/todo_app/ui/menu.py
- [x] T048 [US4] Update _delete_task_flow() to handle series deletion in src/todo_app/ui/menu.py
- [x] T049 [US4] Add "stop recurrence" option when editing task in src/todo_app/ui/menu.py

**Checkpoint**: User Story 4 complete - users can manage recurring series

---

## Phase 7: User Story 5 - Configure Default Reminder Preferences (Priority: P3)

**Goal**: Users can set default reminder timing that auto-applies to new tasks

**Independent Test**: Set default reminder to "30 minutes before" in settings, create new task with due date, verify reminder auto-added

### Implementation for User Story 5

- [x] T050 [US5] Implement PreferencesService.get_preferences() in src/todo_app/services/preferences_service.py
- [x] T051 [US5] Implement PreferencesService.update_preferences() in src/todo_app/services/preferences_service.py
- [x] T052 [US5] Update src/todo_app/services/__init__.py to export preferences_service
- [x] T053 [US5] Add "Settings" menu option (option 10) in src/todo_app/ui/menu.py
- [x] T054 [US5] Implement _settings_flow() with default reminder configuration in src/todo_app/ui/menu.py
- [x] T055 [US5] Apply default reminder when adding tasks with due dates in src/todo_app/services/task_service.py
- [x] T056 [US5] Show current preferences in settings menu in src/todo_app/ui/display.py

**Checkpoint**: User Story 5 complete - default reminders auto-apply

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T057 [P] Add filter by recurrence (show only recurring tasks) in src/todo_app/services/filter.py
- [x] T058 [P] Update existing filter menu to include recurrence filter in src/todo_app/ui/menu.py
- [x] T059 Run quickstart.md validation - test all user scenarios
- [x] T060 Code cleanup - remove any debug prints or unused imports
- [x] T061 Verify backward compatibility - load old tasks.json and confirm no errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Priority | Dependencies | Notes |
|-------|----------|--------------|-------|
| US1: Recurring Tasks | P1 | Foundational only | Core feature, MVP |
| US2: Due Time | P1 | Foundational only | Independent of US1 |
| US3: Reminders | P2 | US2 (needs due_time for trigger calculation) | Builds on time support |
| US4: Series Management | P3 | US1 (needs recurring tasks to exist) | Enhancement to US1 |
| US5: Preferences | P3 | US3 (default reminders need reminder system) | Enhancement to US3 |

### Parallel Opportunities

**Within Foundational Phase:**
```
T005, T006, T007 can run in parallel (different files)
T015, T016 can run in parallel (different functions)
```

**After Foundational (if team allows):**
```
US1 and US2 can run in parallel (independent P1 stories)
```

**Within Each User Story:**
```
Model tasks marked [P] can run in parallel
Service must complete before UI tasks
```

---

## Parallel Example: Foundational Phase

```bash
# Launch these in parallel:
Task: "Create RecurrenceFrequency enum and RecurrencePattern dataclass in src/todo_app/models/recurrence.py"
Task: "Create ReminderOffset enum and Reminder dataclass in src/todo_app/models/reminder.py"
Task: "Create UserPreferences dataclass in src/todo_app/storage/preferences.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 - Recurring Tasks
4. Complete Phase 4: User Story 2 - Due Time
5. **STOP and VALIDATE**: Test both stories independently
6. Demo: "Weekly meeting" task that auto-regenerates with time support

### Incremental Delivery

| Delivery | Stories Included | Value Delivered |
|----------|------------------|-----------------|
| MVP | US1 + US2 | Recurring tasks with time |
| v1.1 | + US3 | Add reminder notifications |
| v1.2 | + US4 | Add series management |
| v1.3 | + US5 | Add default preferences |

### Hackathon Timeline Suggestion

| Day | Focus |
|-----|-------|
| Day 1 | Setup + Foundational + US1 |
| Day 2 | US2 + US3 |
| Day 3 | US4 + US5 + Polish |

---

## Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| 1: Setup | 4 | Dependencies |
| 2: Foundational | 12 | Core models, storage |
| 3: US1 Recurring | 10 | Auto-regenerate tasks |
| 4: US2 Due Time | 5 | Time support |
| 5: US3 Reminders | 11 | Notifications |
| 6: US4 Series | 7 | Manage recurring |
| 7: US5 Preferences | 7 | Default settings |
| 8: Polish | 5 | Cleanup, validation |
| **Total** | **61** | |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [US#] label maps task to specific user story
- Each user story is independently completable and testable
- Commit after each task or logical group
- US1 + US2 together form the MVP for hackathon demo
