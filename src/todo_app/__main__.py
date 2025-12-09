"""Entry point for the Todo application."""

from .ui.menu import Menu


def main() -> None:
    """Main entry point for the Todo application."""
    menu = Menu()
    # Check for due reminders on startup
    menu.check_reminders()
    menu.run()


if __name__ == "__main__":
    main()
