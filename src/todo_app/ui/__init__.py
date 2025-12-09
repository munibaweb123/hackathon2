"""User interface components for the Todo application."""

from .console import Console
from .display import create_task_table, display_task_detail, display_tasks
from .menu import Menu
from .prompts import Prompts

__all__ = [
    "Console",
    "Menu",
    "Prompts",
    "create_task_table",
    "display_task_detail",
    "display_tasks",
]
