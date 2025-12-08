# Todo In-Memory Python Console App

A command-line todo application that stores tasks in memory, built with Python 3.13+ and UV package manager.

## Features

- Add new tasks with title and description
- View all tasks with completion status indicators ([X] / [ ])
- Mark tasks as complete/incomplete
- Update task title and description
- Delete tasks by ID
- Auto-generated sequential task IDs

## Important Note

This application stores all tasks in memory only. Tasks are not persisted between application sessions. When you close and reopen the application, all tasks will be lost. This is by design as specified in the requirements (in-memory storage during application session).

## Prerequisites

- Python 3.13 or higher
- UV package manager ([install instructions](https://docs.astral.sh/uv/getting-started/installation/))

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd hackathon_2

# Create virtual environment with UV
uv venv --python 3.13

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat

# Install the package
uv pip install -e .

# For development (includes pytest):
uv pip install -e ".[dev]"
```

## Usage

### Start the Application

```bash
python -m src.main
```

### Example Session

```
Welcome to Todo Console App!
==============================

==============================
       TODO APP MENU
==============================
1. Add Task
2. View Tasks
3. Mark Complete
4. Mark Incomplete
5. Update Task
6. Delete Task
7. Exit
==============================
Select option (1-7): 1

--- Add Task ---
Enter title: Buy groceries
Enter description (optional): Milk, eggs, bread
Task added with ID: 1

Select option (1-7): 2

--- All Tasks ---
[ ] 1. Buy groceries
    Milk, eggs, bread

Select option (1-7): 3

--- Mark Complete ---
Enter task ID: 1
Task 1 marked as complete.

Select option (1-7): 2

--- All Tasks ---
[X] 1. Buy groceries
    Milk, eggs, bread

Select option (1-7): 7

Goodbye!
```

## Menu Options

| Option | Action | Description |
|--------|--------|-------------|
| 1 | Add Task | Create a new task with title and optional description |
| 2 | View Tasks | Display all tasks with status indicators |
| 3 | Mark Complete | Mark a task as done by ID |
| 4 | Mark Incomplete | Mark a task as not done by ID |
| 5 | Update Task | Modify title/description of existing task |
| 6 | Delete Task | Remove a task permanently by ID |
| 7 | Exit | Close the application |

## Project Structure

```
hackathon_2/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic
│   └── cli/
│       ├── __init__.py
│       └── menu.py          # Menu interface
├── tests/
│   ├── unit/
│   └── integration/
├── specs/                    # Feature specifications
├── pyproject.toml
└── README.md
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test types
pytest tests/unit/
pytest tests/integration/
```

## Technology Stack

- **Language**: Python 3.13+
- **Package Manager**: UV
- **Testing**: pytest
- **Storage**: In-memory (dictionary)
