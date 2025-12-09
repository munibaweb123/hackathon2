# Quickstart: Professional Todo Console Application

**Feature**: 002-todo-console-app
**Date**: 2025-12-09

## Prerequisites

- Python 3.13 or higher
- UV package manager installed ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- Terminal with ANSI color support

## Project Setup

### 1. Initialize Project

```bash
# Create project directory
uv init todo-app --python 3.13
cd todo-app
```

### 2. Add Dependencies

```bash
# Add rich for console formatting
uv add rich

# Add development dependencies
uv add --dev pytest pytest-cov
```

### 3. Project Structure

Create the following directory structure:

```bash
mkdir -p src/todo_app/{models,storage,services,ui}
mkdir -p tests/{unit,integration}

# Create __init__.py files
touch src/todo_app/__init__.py
touch src/todo_app/models/__init__.py
touch src/todo_app/storage/__init__.py
touch src/todo_app/services/__init__.py
touch src/todo_app/ui/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

### 4. Configure pyproject.toml

Update `pyproject.toml`:

```toml
[project]
name = "todo-app"
version = "1.0.0"
description = "Professional console-based todo application"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "rich>=13.0.0",
]

[project.scripts]
todo = "todo_app.__main__:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
]
```

## Running the Application

### Development Mode

```bash
# Run directly with UV
uv run python -m todo_app

# Or using the script entry point (after install)
uv run todo
```

### Production Mode

```bash
# Install the package
uv pip install -e .

# Run the application
todo
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=todo_app --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run specific test
uv run pytest tests/unit/test_models.py::test_task_creation
```

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| Tasks data | `./tasks.json` | Persistent task storage |
| Source code | `src/todo_app/` | Application modules |
| Tests | `tests/` | Unit and integration tests |

## Quick Verification

After setup, verify the installation:

```bash
# Check Python version
python --version  # Should show 3.13+

# Check UV
uv --version

# Verify rich is installed
uv run python -c "from rich.console import Console; print('Rich OK')"

# Run the app
uv run python -m todo_app
```

## Expected Output

```
╭────────────────────────────────────╮
│     === Todo Application ===       │
╰────────────────────────────────────╯

1. Add new task
2. View all tasks
3. Update task
4. Delete task
5. Mark task complete/incomplete
6. Search tasks
7. Filter tasks
8. Sort tasks
9. Exit

Enter choice:
```

## Troubleshooting

### Python Version Issues

```bash
# Check available Python versions
uv python list

# Install Python 3.13 if needed
uv python install 3.13
```

### Permission Issues (Linux/Mac)

```bash
# Make sure you have write access to current directory
ls -la tasks.json  # Check file permissions
```

### Color Display Issues

If colors don't display correctly:
- Windows: Use Windows Terminal or enable ANSI in cmd
- Linux/Mac: Ensure TERM environment variable is set

```bash
echo $TERM  # Should be xterm-256color or similar
```

## Development Workflow

1. **Make changes** to source files in `src/todo_app/`
2. **Run tests** with `uv run pytest`
3. **Test manually** with `uv run python -m todo_app`
4. **Format code** (optional): `uv run ruff format .`
5. **Lint code** (optional): `uv run ruff check .`

## Next Steps

After quickstart verification:
1. Implement models (`src/todo_app/models/task.py`)
2. Implement storage (`src/todo_app/storage/json_store.py`)
3. Implement services (`src/todo_app/services/task_service.py`)
4. Implement UI (`src/todo_app/ui/console.py`)
5. Wire up entry point (`src/todo_app/__main__.py`)
