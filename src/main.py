"""Main entry point for the Todo Console Application."""

from src.cli.menu import run_menu_loop
from src.services.task_service import TaskService


def main() -> None:
    """Initialize the application and start the menu loop."""
    print("Welcome to Todo Console App!")
    print("=" * 30)

    service = TaskService()

    try:
        run_menu_loop(service)
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye!")


if __name__ == "__main__":
    main()
