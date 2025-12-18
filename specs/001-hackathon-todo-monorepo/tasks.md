# Tasks: Hackathon Todo Monorepo Migration

**Input**: Design documents from `/specs/001-hackathon-todo-monorepo/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/openapi.yaml (complete)

**Migration Note**: This is a code migration, not new development. Existing code in `todo_web/` moves to root-level `backend/` and `frontend/` directories. Using `git mv` preserves file history.

**Organization**: Tasks are grouped by user story to enable independent verification of each story's success criteria.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- File paths use absolute paths from repository root

---

## Phase 1: Pre-Migration Setup

**Purpose**: Prepare for migration by removing placeholder files that will be replaced

- [x] T001 [P] Remove placeholder `backend/main.py` (will be replaced by migrated code)
- [x] T002 [P] Remove placeholder `backend/models.py` (will be replaced by migrated code)
- [x] T003 [P] Remove placeholder `backend/db.py` (will be replaced by migrated code)
- [x] T004 [P] Remove placeholder `frontend/src/app/page.tsx` (will be replaced by migrated code)
- [x] T005 [P] Remove placeholder `frontend/src/app/layout.tsx` (will be replaced by migrated code)
- [x] T006 [P] Remove placeholder `frontend/src/lib/api.ts` (will be replaced by migrated code)

**Checkpoint**: Placeholder files removed, ready for migration

---

## Phase 2: User Story 1 - Project Initialization (Priority: P1)

**Goal**: Pre-configured monorepo structure with all directories and configuration files in place

**Independent Test**: Clone repo, verify backend/, frontend/, specs/, .spec-kit/ exist with proper configs

### Implementation for User Story 1

- [x] T007 [US1] Verify .spec-kit/config.yaml exists with phase definitions
- [x] T008 [US1] Verify specs/ directory structure (overview.md, features/, api/, database/)
- [x] T009 [US1] Update root CLAUDE.md with accurate monorepo structure post-migration
- [x] T010 [US1] Verify docker-compose.yml references correct paths (backend/, frontend/)

**Checkpoint**: Project structure validated - US1 acceptance scenarios can be verified

---

## Phase 3: User Story 2 - Backend Development Setup (Priority: P1)

**Goal**: Working FastAPI backend with full implementation migrated from todo_web/backend

**Independent Test**: Run `cd backend && uvicorn app.main:app --reload` and access /health endpoint

### Backend Migration Tasks

- [x] T011 [US2] Git mv `todo_web/backend/app/` to `backend/app/`
- [x] T012 [US2] Git mv `todo_web/backend/tests/` to `backend/tests/`
- [x] T013 [P] [US2] Copy `todo_web/backend/.env` to `backend/.env`
- [x] T014 [P] [US2] Copy `todo_web/backend/.env.example` to `backend/.env.example`
- [x] T015 [P] [US2] Copy `todo_web/backend/requirements.txt` to `backend/requirements.txt`
- [x] T016 [P] [US2] Copy `todo_web/backend/pyproject.toml` to `backend/pyproject.toml`
- [x] T017 [P] [US2] Copy `todo_web/backend/Dockerfile` to `backend/Dockerfile` (if exists)
- [x] T018 [US2] Update backend/CLAUDE.md with accurate paths and structure

### Backend Verification Tasks

- [ ] T019 [US2] Verify backend imports work (no broken relative imports)
- [ ] T020 [US2] Run `cd backend && python -c "from app.main import app; print('OK')"` to verify imports
- [ ] T021 [US2] Start backend server and verify /health endpoint responds

**Checkpoint**: Backend fully functional at new location - US2 acceptance scenarios can be verified

---

## Phase 4: User Story 3 - Frontend Development Setup (Priority: P2)

**Goal**: Working Next.js frontend with full implementation migrated from todo_web/todo_web_frontend

**Independent Test**: Run `cd frontend && npm install && npm run dev` and access localhost:3000

### Frontend Migration Tasks

- [x] T022 [US3] Git mv `todo_web/todo_web_frontend/src/` to `frontend/src/`
- [x] T023 [US3] Git mv `todo_web/todo_web_frontend/public/` to `frontend/public/`
- [x] T024 [P] [US3] Copy `todo_web/todo_web_frontend/package.json` to `frontend/package.json`
- [x] T025 [P] [US3] Copy `todo_web/todo_web_frontend/package-lock.json` to `frontend/package-lock.json`
- [x] T026 [P] [US3] Copy `todo_web/todo_web_frontend/tsconfig.json` to `frontend/tsconfig.json`
- [x] T027 [P] [US3] Copy `todo_web/todo_web_frontend/tailwind.config.ts` to `frontend/tailwind.config.ts`
- [x] T028 [P] [US3] Copy `todo_web/todo_web_frontend/postcss.config.mjs` to `frontend/postcss.config.mjs`
- [x] T029 [P] [US3] Copy `todo_web/todo_web_frontend/next.config.ts` to `frontend/next.config.ts`
- [x] T030 [P] [US3] Copy `todo_web/todo_web_frontend/.env.local` to `frontend/.env.local`
- [x] T031 [P] [US3] Copy `todo_web/todo_web_frontend/.env.example` to `frontend/.env.example` (if exists)
- [x] T032 [P] [US3] Copy `todo_web/todo_web_frontend/components.json` to `frontend/components.json` (if exists)
- [x] T033 [US3] Update frontend/CLAUDE.md with accurate paths and structure

### Frontend Verification Tasks

- [ ] T034 [US3] Run `cd frontend && npm install` - verify no errors
- [ ] T035 [US3] Run `cd frontend && npm run build` - verify build succeeds
- [ ] T036 [US3] Start frontend dev server and verify home page renders

**Checkpoint**: Frontend fully functional at new location - US3 acceptance scenarios can be verified

---

## Phase 5: User Story 4 - Specification Reference (Priority: P2)

**Goal**: Centralized specifications for understanding requirements before implementing features

**Independent Test**: Read specs/overview.md and follow links to individual spec files

### Specification Verification Tasks

- [ ] T037 [P] [US4] Verify specs/overview.md exists and contains phase development approach
- [ ] T038 [P] [US4] Verify specs/api/rest-endpoints.md contains complete endpoint documentation
- [ ] T039 [P] [US4] Verify specs/database/schema.md contains table definitions and relationships
- [ ] T040 [P] [US4] Verify specs/features/task-crud.md contains task CRUD feature specification
- [ ] T041 [US4] Update any spec file links that reference old todo_web/ paths

**Checkpoint**: All specification files accessible and accurate - US4 acceptance scenarios can be verified

---

## Phase 6: User Story 5 - Container Orchestration (Priority: P3)

**Goal**: Docker Compose configuration that runs the entire stack with one command

**Independent Test**: Run `docker-compose up` and access both frontend (3000) and backend (8000)

### Docker Configuration Tasks

- [ ] T042 [US5] Verify docker-compose.yml backend service uses `./backend` context
- [ ] T043 [US5] Verify docker-compose.yml frontend service uses `./frontend` context
- [ ] T044 [US5] Update docker-compose volume mounts if they reference old paths
- [ ] T045 [US5] Update backend Dockerfile if paths changed
- [ ] T046 [US5] Update frontend Dockerfile if paths changed

### Docker Verification Tasks

- [ ] T047 [US5] Run `docker-compose build` - verify images build successfully
- [ ] T048 [US5] Run `docker-compose up` - verify all services start
- [ ] T049 [US5] Access localhost:8000/health - verify backend responds
- [ ] T050 [US5] Access localhost:3000 - verify frontend renders

**Checkpoint**: Docker orchestration functional - US5 acceptance scenarios can be verified

---

## Phase 7: Cleanup & Final Verification

**Purpose**: Remove old directories and perform final validation

### Cleanup Tasks

- [x] T051 Remove `todo_web/` directory (after verifying all code migrated)
- [x] T052 [P] Remove any empty placeholder directories in backend/
- [x] T053 [P] Remove any empty placeholder directories in frontend/
- [x] T054 Update .gitignore if necessary for new structure

### Final Verification Tasks

- [ ] T055 [P] Run full backend test suite: `cd backend && pytest`
- [ ] T056 [P] Run frontend type check: `cd frontend && npm run type-check` (if configured)
- [ ] T057 Run quickstart.md validation - follow all steps in specs/001-hackathon-todo-monorepo/quickstart.md
- [ ] T058 Git commit all changes with message documenting migration

**Checkpoint**: Migration complete - all user story acceptance scenarios should pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Pre-Migration Setup)**: No dependencies - start immediately
- **Phase 2 (US1)**: Depends on Phase 1 - verify structure before migration
- **Phase 3 (US2)**: Depends on Phase 1 - backend migration
- **Phase 4 (US3)**: Depends on Phase 1, can run parallel with Phase 3 - frontend migration
- **Phase 5 (US4)**: No migration dependencies - verification only
- **Phase 6 (US5)**: Depends on Phase 3 and Phase 4 - Docker needs both migrated
- **Phase 7 (Cleanup)**: Depends on all previous phases - final step

### Task Dependencies Within Phases

**Phase 3 (Backend Migration)**:
```
T011 (git mv app/) → T019 (verify imports) → T020 (test import) → T021 (test server)
T012-T018 can run parallel with T011
```

**Phase 4 (Frontend Migration)**:
```
T022 (git mv src/) → T034 (npm install) → T035 (npm build) → T036 (test dev server)
T023-T033 can run parallel with T022
```

### Parallel Opportunities

- Phase 1: All T001-T006 can run in parallel (removing different placeholder files)
- Phase 3: T013-T018 can run in parallel (copying independent config files)
- Phase 4: T024-T032 can run in parallel (copying independent config files)
- Phase 5: All T037-T040 can run in parallel (verifying different spec files)
- Phase 3 and Phase 4 can run in parallel (backend and frontend independent)

---

## Implementation Strategy

### Recommended Execution Order

1. **Phase 1**: Remove all placeholder files (5 minutes)
2. **Phase 2 + Phase 3**: Migrate backend first (ensures API available)
3. **Phase 4**: Migrate frontend (connects to migrated backend)
4. **Phase 5**: Verify specifications (quick verification)
5. **Phase 6**: Test Docker orchestration (integration test)
6. **Phase 7**: Cleanup and final commit

### Rollback Plan

If migration fails at any point:
1. Use `git checkout -- .` to restore placeholder files
2. Keep `todo_web/` intact until Phase 7 cleanup
3. Migration uses `git mv` so history is preserved, can revert if needed

---

## Notes

- [P] tasks = can run in parallel (different files, no dependencies)
- [US#] label maps task to specific user story for traceability
- Using `git mv` preserves file history - preferred over `cp` then `rm`
- Verify each phase checkpoint before proceeding to next phase
- All migrated code should work without import changes (relative imports)
- Keep `src/todo_app/` (Phase 1 console app) - do not migrate or delete
