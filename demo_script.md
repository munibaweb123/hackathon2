# Hackathon 2 - Phase 1 Intermediate Demo Script

## Introduction (30 seconds)
"Hi, I'm presenting my Todo Console Application for Hackathon 2 Phase 1 at the Intermediate level. This app demonstrates clean architecture, persistent storage, and a rich terminal interface."

## Key Features to Demo (2-3 minutes)

### 1. Add a Task
```
Choose option 1 → Add new task
- Title: "Complete hackathon presentation"
- Description: "Prepare and deliver demo"
- Due date: 2025-12-15
- Priority: high
- Categories: hackathon, demo
```

### 2. Add Another Task
```
Add a second task:
- Title: "Review code quality"
- Priority: medium
- Categories: code
```

### 3. View All Tasks
```
Choose option 2 → Shows formatted table with all tasks
```

### 4. Mark Task Complete
```
Choose option 5 → Mark task #1 as complete
```

### 5. Filter Tasks
```
Choose option 7 → Filter by status → incomplete
Shows only pending tasks
```

### 6. Search Tasks
```
Choose option 6 → Search "hackathon"
Finds matching tasks
```

## Technical Highlights to Mention

1. **Persistent JSON Storage** - Tasks saved to `tasks.json`, survives restarts
2. **Rich Terminal UI** - Colored output, formatted tables using `rich` library
3. **Input Validation** - Date format, priority levels, required fields
4. **Atomic File Writes** - Safe saves with temp file + rename pattern
5. **Clean Architecture** - Separated models, services, storage, and UI layers

## Project Structure (quick mention)
```
src/todo_app/
├── models/      # Task data model
├── services/    # Business logic
├── storage/     # JSON persistence
└── ui/          # Console interface
```

## Closing (15 seconds)
"This intermediate-level implementation shows proper separation of concerns, data persistence, and a polished user experience. Thank you!"

---

## Quick Commands Reference
```bash
# Run the app
uv run python -m todo_app

# Or with Python directly
python -m todo_app
```
