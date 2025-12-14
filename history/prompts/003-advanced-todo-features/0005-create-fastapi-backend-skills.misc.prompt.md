---
id: 0005
title: Create FastAPI Backend Skills
stage: misc
date: 2025-12-10
surface: agent
model: claude-opus-4-5-20251101
feature: 003-advanced-todo-features
branch: 003-advanced-todo-features
user: user
command: direct-request
labels: ["skills", "fastapi", "crud", "api", "slash-commands"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/commands/fastapi.getTodos.md
  - .claude/commands/fastapi.createTodo.md
  - .claude/commands/fastapi.updateTodo.md
  - .claude/commands/fastapi.deleteTodo.md
  - .claude/commands/fastapi.config.md
tests:
  - N/A (documentation/skill files only)
---

## Prompt

create skills for {
  "name": "fastapi_backend",
  "description": "Interact with FastAPI backend for Todo App CRUD operations.",
  "type": "api",
  "config": {
    "baseUrl": "https://your-fastapi-url.com",
    "endpoints": {
      "getTodos": { "method": "GET", "path": "/todos" },
      "createTodo": { "method": "POST", "path": "/todos" },
      "updateTodo": { "method": "PUT", "path": "/todos/{id}" },
      "deleteTodo": { "method": "DELETE", "path": "/todos/{id}" }
    }
  }
}

## Response snapshot

Created 5 Claude Code slash command skills for FastAPI backend CRUD operations:

1. `/fastapi.getTodos` - Fetch all todos (GET /todos)
2. `/fastapi.createTodo` - Create new todo (POST /todos)
3. `/fastapi.updateTodo` - Update existing todo (PUT /todos/{id})
4. `/fastapi.deleteTodo` - Delete a todo (DELETE /todos/{id})
5. `/fastapi.config` - Configure base URL and auth token

Each skill includes:
- Endpoint details and method
- Request/response schemas
- curl command templates
- Error handling guidance
- Usage examples

## Outcome

- ✅ Impact: Added 5 new slash commands for FastAPI backend interaction
- 🧪 Tests: N/A - documentation/template files
- 📁 Files: 5 files created in .claude/commands/
- 🔁 Next prompts: Configure actual baseUrl, implement backend if not exists
- 🧠 Reflection: Skills provide consistent API interaction patterns via slash commands

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add actual API testing with real backend URL
