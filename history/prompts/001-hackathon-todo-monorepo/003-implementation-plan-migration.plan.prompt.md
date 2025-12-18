---
id: 003
title: Create implementation plan for monorepo migration
stage: plan
date: 2025-12-18
surface: agent
model: claude-opus-4-5-20251101
feature: 001-hackathon-todo-monorepo
branch: 001-hackathon-todo-monorepo
user: user
command: /sp.plan
labels: ["planning", "migration", "monorepo", "restructure"]
links:
  spec: specs/001-hackathon-todo-monorepo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-hackathon-todo-monorepo/plan.md
  - specs/001-hackathon-todo-monorepo/research.md
  - specs/001-hackathon-todo-monorepo/data-model.md
  - specs/001-hackathon-todo-monorepo/quickstart.md
  - specs/001-hackathon-todo-monorepo/contracts/openapi.yaml
  - CLAUDE.md
tests:
  - None (planning phase)
---

## Prompt

/sp.plan project till todo-web is already build, adjust directory structure for monorepo as in specification

## Response snapshot

Created comprehensive implementation plan for migrating existing `todo_web/` application to monorepo structure:

**Key Findings:**
- Existing todo_web/backend has full FastAPI implementation (45+ files)
- Existing todo_web/todo_web_frontend has full Next.js implementation (55+ files)
- New backend/ and frontend/ directories have placeholder boilerplate
- Migration approach: replace placeholders with existing code using git mv

**Phase 0 (research.md):**
- Decision 1: Use git mv for history preservation
- Decision 2: Migrate app/ → tests/ → config files order
- Decision 3: Replace placeholder files with real code
- Decision 4: Copy existing .env files
- Decision 5: Preserve src/todo_app as Phase 1 artifact
- Decision 6: Update docker-compose build contexts

**Phase 1 Artifacts:**
- data-model.md: Documented 4 entities (User, Task, Reminder, UserPreference) with full schema
- contracts/openapi.yaml: Complete OpenAPI 3.1 specification for all endpoints
- quickstart.md: Setup guide for local dev and Docker deployment

**Constitution Check:** PASSED - All 3 principles satisfied by existing implementation

**Migration Strategy:**
1. Backend Migration: Move todo_web/backend/app → backend/app
2. Frontend Migration: Move todo_web/todo_web_frontend/src → frontend/src
3. Cleanup: Remove todo_web/ after verification

## Outcome

- ✅ Impact: Complete implementation plan with migration strategy for monorepo restructure
- 🧪 Tests: N/A (planning phase - tests defined in tasks)
- 📁 Files: 5 planning artifacts created
- 🔁 Next prompts: `/sp.tasks` to generate migration tasks
- 🧠 Reflection: Plan accounts for existing code; migration is file move operation, not new development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check - PASS
- Prompt variant (if applicable): Standard /sp.plan with user context about existing code
- Next experiment (smallest change to try): N/A - ready for task generation
