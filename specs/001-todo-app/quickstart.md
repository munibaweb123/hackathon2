# Quickstart: Todo In-Memory Python Console App

## Prerequisites
- Python 3.13+
- UV package manager

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the application**:
   ```bash
   uv run python -m src.todo_app.main
   ```

## Basic Usage

### Adding a Task
```bash
python -m src.todo_app.main add "Complete project documentation"
```

### Viewing All Tasks
```bash
python -m src.todo_app.main list
# or
python -m src.todo_app.main view
```

### Marking a Task as Complete
```bash
python -m src.todo_app.main complete TSK-001
```

### Updating a Task Description
```bash
python -m src.todo_app.main update TSK-001 "Revised project documentation"
```

### Deleting a Task
```bash
python -m src.todo_app.main delete TSK-001
```

## Project Structure
```
src/
├── todo_app/              # Main application package
│   ├── __init__.py
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   └── task.py
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   └── task_service.py
│   ├── cli/               # Command-line interface
│   │   ├── __init__.py
│   │   └── cli.py
│   └── main.py            # Entry point
```

## Development

### Running Tests
```bash
uv run pytest
```

### Running Tests with Coverage
```bash
uv run pytest --cov=src.todo_app
```

## Available Commands
- `add <description>` - Add a new task
- `list` or `view` - Show all tasks
- `complete <task_id>` - Mark task as complete
- `update <task_id> <new_description>` - Update task description
- `delete <task_id>` - Delete a task
- `help` - Show available commands