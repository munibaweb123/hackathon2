---
id: 0007
title: Create Neon Database Skills
stage: misc
date: 2025-12-10
surface: agent
model: claude-opus-4-5-20251101
feature: 003-advanced-todo-features
branch: 003-advanced-todo-features
user: user
command: direct-request
labels: ["skills", "neon", "postgresql", "database", "sql", "slash-commands"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/commands/neon.query.md
  - .claude/commands/neon.select.md
  - .claude/commands/neon.insert.md
  - .claude/commands/neon.update.md
  - .claude/commands/neon.delete.md
  - .claude/commands/neon.config.md
tests:
  - N/A (documentation/skill files only)
---

## Prompt

create skill for {
  "name": "neon_database_skill",
  "description": "Skill for interacting directly with Neon Serverless PostgreSQL using SQL API.",
  "type": "api",
  "config": {
    "baseUrl": "https://your-neon-project-url.com/sql",
    "headers": {
      "Authorization": "Bearer YOUR_NEON_API_KEY"
    },
    "endpoints": {
      "runQuery": {
        "method": "POST",
        "path": "/query"
      }
    }
  }
}

## Response snapshot

Created 6 Claude Code slash command skills for Neon Serverless PostgreSQL:

1. `/neon.query` - Execute raw SQL queries (POST /query)
2. `/neon.select` - Simplified SELECT with helper syntax
3. `/neon.insert` - Insert records with column=value syntax
4. `/neon.update` - Update records by ID/condition
5. `/neon.delete` - Delete records by ID/condition
6. `/neon.config` - Configure connection, test, list tables/schema

Each skill includes:
- Endpoint details and curl examples
- Request/response schemas
- Parameterized query support for SQL injection prevention
- Error handling guidance
- Common patterns and usage examples

## Outcome

- ✅ Impact: Added 6 new slash commands for Neon PostgreSQL interaction
- 🧪 Tests: N/A - documentation/template files
- 📁 Files: 6 files created in .claude/commands/
- 🔁 Next prompts: Configure actual Neon project URL and API key
- 🧠 Reflection: Database skills provide full CRUD + schema introspection capabilities

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add transaction support skill, add migration skill
