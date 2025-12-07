# Todo In-Memory Python Console App

A command-line todo application that stores tasks in memory.

## Features

- Add new tasks with descriptions
- View all tasks with their completion status
- Mark tasks as complete/incomplete
- Update task descriptions
- Delete tasks
- Auto-generated task identifiers in TSK-### format

## Important Note

This application stores all tasks in memory only. Tasks are not persisted between application sessions. When you close and reopen the application, all tasks will be lost. This is by design as specified in the requirements (in-memory storage during application session).

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd todo-app

# Install dependencies
uv sync  # or pip install -e .
```

## Usage

```bash
# Add a new task
python -m src.todo_app.main add "Complete project documentation"

# View all tasks
python -m src.todo_app.main list

# View only completed tasks
python -m src.todo_app.main list --completed

# View only pending tasks
python -m src.todo_app.main view --pending

# Mark a task as complete
python -m src.todo_app.main complete TSK-001

# Update a task description
python -m src.todo_app.main update TSK-001 "Revised project documentation"

# Delete a task
python -m src.todo_app.main delete TSK-001
```

## Development

```bash
# Run tests
pytest

# Run specific tests
pytest tests/unit/
pytest tests/integration/
```# hackathon2
