"""Entry point for the Todo application."""

from .ui.menu import Menu


def main() -> None:
    """Main entry point for the Todo application."""
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()
