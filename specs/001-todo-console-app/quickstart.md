# Quickstart: Todo In-Memory Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-09

## Prerequisites

- Python 3.13 or higher
- UV package manager ([install instructions](https://docs.astral.sh/uv/getting-started/installation/))

## Setup

### 1. Clone and Navigate

```bash
cd hackathon_2
```

### 2. Create Virtual Environment with UV

```bash
uv venv --python 3.13
```

### 3. Activate Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
uv pip install -e .
```

For development (includes pytest):
```bash
uv pip install -e ".[dev]"
```

## Running the Application

### Start the Todo App

```bash
python -m src.main
```

Or if installed as a package:
```bash
todo-app
```

### Example Session

```
=== Todo App ===
1. Add Task
2. View Tasks
3. Mark Complete
4. Mark Incomplete
5. Update Task
6. Delete Task
7. Exit

Select option: 1

--- Add Task ---
Enter title: Buy groceries
Enter description (optional): Milk, eggs, bread
Task added with ID: 1

Select option: 2

--- All Tasks ---
[ ] 1. Buy groceries
    Milk, eggs, bread

Select option: 3

--- Mark Complete ---
Enter task ID: 1
Task 1 marked as complete

Select option: 2

--- All Tasks ---
[X] 1. Buy groceries
    Milk, eggs, bread

Select option: 7
Goodbye!
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

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
├── pyproject.toml           # Project configuration
└── README.md
```

## Configuration (pyproject.toml)

```toml
[project]
name = "todo-console-app"
version = "0.1.0"
description = "In-memory todo console application"
requires-python = ">=3.13"

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=4.0"]

[project.scripts]
todo-app = "src.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

## Common Issues

### UV Not Found

Install UV first:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Python Version Error

Ensure Python 3.13+ is installed:
```bash
python --version
```

### Module Not Found

Make sure you installed in editable mode:
```bash
uv pip install -e .
```
