---
id: 004
title: Generate migration tasks for monorepo restructure
stage: tasks
date: 2025-12-18
surface: agent
model: claude-opus-4-5-20251101
feature: 001-hackathon-todo-monorepo
branch: 001-hackathon-todo-monorepo
user: user
command: /sp.tasks
labels: ["tasks", "migration", "monorepo", "restructure"]
links:
  spec: specs/001-hackathon-todo-monorepo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-hackathon-todo-monorepo/tasks.md
tests:
  - None (task generation phase)
---

## Prompt

/sp.tasks

## Response snapshot

Generated comprehensive task list (58 tasks) for migrating existing `todo_web/` application to monorepo structure:

**Task Distribution by User Story:**
- Phase 1 (Pre-Migration): 6 tasks - Remove placeholder files
- Phase 2 (US1 - Project Init): 4 tasks - Verify structure
- Phase 3 (US2 - Backend): 11 tasks - Migrate and verify backend
- Phase 4 (US3 - Frontend): 15 tasks - Migrate and verify frontend
- Phase 5 (US4 - Specs): 5 tasks - Verify specifications
- Phase 6 (US5 - Docker): 9 tasks - Configure and test orchestration
- Phase 7 (Cleanup): 8 tasks - Remove old directories, final validation

**Key Migration Tasks:**
- T011: Git mv `todo_web/backend/app/` → `backend/app/`
- T022: Git mv `todo_web/todo_web_frontend/src/` → `frontend/src/`
- T051: Remove `todo_web/` directory after verification

**Parallel Opportunities Identified:**
- Phase 1: All placeholder removal tasks
- Phase 3/4: Backend and frontend migrations can run in parallel
- Config file copies within each phase can run in parallel

**Dependency Graph:**
- Phase 1 → Phase 2/3/4 (structure ready before migration)
- Phase 3 + Phase 4 → Phase 6 (both needed for Docker)
- All phases → Phase 7 (cleanup last)

## Outcome

- ✅ Impact: Complete task list with 58 actionable migration tasks organized by user story
- 🧪 Tests: N/A (task generation phase - tests defined as verification tasks)
- 📁 Files: 1 file created (tasks.md)
- 🔁 Next prompts: `/sp.implement` to execute migration tasks
- 🧠 Reflection: Migration tasks focus on git mv for history preservation; verification tasks ensure each phase succeeds before proceeding

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - task generation complete
- Prompt variant (if applicable): Standard /sp.tasks command
- Next experiment (smallest change to try): N/A - ready for implementation
