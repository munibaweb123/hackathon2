# Research: Hackathon Todo Monorepo Migration

**Date**: 2025-12-18
**Feature**: 001-hackathon-todo-monorepo

## Research Summary

This feature involves restructuring an existing working application into a monorepo structure. No new technology decisions needed - focusing on migration best practices.

## Decision 1: Migration Approach

**Decision**: In-place migration with git mv to preserve history

**Rationale**:
- Using `git mv` preserves file history, making it easier to trace changes
- Avoids duplicate commits that would occur with copy-then-delete
- Atomic operation reduces risk of partial migration states

**Alternatives Considered**:
- Copy-then-delete: Loses git history, simpler but less traceable
- Fresh clone approach: Overkill for this project size
- Symlinks: Adds complexity, potential issues with Docker contexts

## Decision 2: Backend Migration Order

**Decision**: Migrate app/ first, then tests/, then config files

**Rationale**:
- Core application code is the primary concern
- Tests depend on app code paths being correct
- Config files can be updated last to reference new paths

**Alternatives Considered**:
- All-at-once: Higher risk of something breaking mid-migration
- Config first: Would break application until code moves

## Decision 3: Placeholder File Handling

**Decision**: Remove placeholder files created by /sp.specify, replace with real code

**Rationale**:
- The new backend/main.py, models.py, db.py are boilerplate
- Existing todo_web/backend has full implementation
- Replace placeholders rather than merge

**Alternatives Considered**:
- Merge placeholder with existing: Unnecessary complexity
- Keep both: Duplication, confusion

## Decision 4: Environment Files

**Decision**: Copy .env from todo_web/backend, update paths in docker-compose

**Rationale**:
- Existing .env has working configuration
- Only docker-compose paths need updating
- Avoid breaking development environment

**Alternatives Considered**:
- Create new .env: Would need to recreate secrets, database URLs
- Symlink: Complexity with Docker volumes

## Decision 5: Console App Preservation

**Decision**: Keep src/todo_app as Phase 1 artifact, do not integrate

**Rationale**:
- Console app represents Phase 1 (completed)
- Web app is Phase 2 (current)
- Clear separation of phases aids project history

**Alternatives Considered**:
- Move to apps/console: Overengineering for single console app
- Delete: Loses Phase 1 history and documentation value

## Decision 6: Docker Compose Updates

**Decision**: Update build contexts to use root-level backend/ and frontend/

**Rationale**:
- Current docker-compose.yml already references backend/ and frontend/
- Just needs verification after migration
- Volume mounts need path updates

**Changes Required**:
```yaml
services:
  backend:
    build:
      context: ./backend  # Already correct
  frontend:
    build:
      context: ./frontend  # Already correct
```

## Open Questions (None)

All technical decisions resolved. Ready for task generation.

## Files Analyzed

| Source | Purpose | Target |
|--------|---------|--------|
| todo_web/backend/app/ | FastAPI application | backend/app/ |
| todo_web/backend/tests/ | Backend tests | backend/tests/ |
| todo_web/backend/.env | Environment config | backend/.env |
| todo_web/backend/requirements.txt | Python deps | backend/requirements.txt |
| todo_web/backend/pyproject.toml | Project config | backend/pyproject.toml |
| todo_web/todo_web_frontend/src/ | Next.js source | frontend/src/ |
| todo_web/todo_web_frontend/public/ | Static assets | frontend/public/ |
| todo_web/todo_web_frontend/.env.local | Frontend env | frontend/.env.local |
| todo_web/todo_web_frontend/package.json | Node deps | frontend/package.json |
| todo_web/todo_web_frontend/*.config.* | Config files | frontend/*.config.* |
