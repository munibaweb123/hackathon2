"""Rich console wrapper for the Todo application."""

from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.text import Text


class Console:
    """
    Wrapper around rich.Console for consistent styling and messaging.

    Provides methods for:
        - Success/error/warning messages
        - Styled panels and text
        - Input prompts
    """

    def __init__(self):
        """Initialize the console wrapper."""
        self._console = RichConsole()

    @property
    def rich_console(self) -> RichConsole:
        """Get the underlying rich Console instance."""
        return self._console

    def print(self, *args, **kwargs) -> None:
        """Print to the console."""
        self._console.print(*args, **kwargs)

    def success(self, message: str) -> None:
        """Display a success message in green."""
        self._console.print(f"[bold green]✓[/bold green] {message}")

    def error(self, message: str) -> None:
        """Display an error message in red."""
        self._console.print(f"[bold red]✗[/bold red] {message}")

    def warning(self, message: str) -> None:
        """Display a warning message in yellow."""
        self._console.print(f"[bold yellow]![/bold yellow] {message}")

    def info(self, message: str) -> None:
        """Display an info message in blue."""
        self._console.print(f"[bold blue]ℹ[/bold blue] {message}")

    def header(self, title: str) -> None:
        """Display a header panel."""
        panel = Panel(
            Text(title, justify="center", style="bold white"),
            style="bold cyan",
            padding=(0, 2),
        )
        self._console.print(panel)

    def divider(self) -> None:
        """Print a horizontal divider."""
        self._console.rule()

    def blank(self) -> None:
        """Print a blank line."""
        self._console.print()

    def input(self, prompt: str = "") -> str:
        """
        Get input from the user.

        Args:
            prompt: The prompt to display.

        Returns:
            The user's input as a string.
        """
        return self._console.input(prompt)

    def confirm(self, message: str, default: bool = False) -> bool:
        """
        Ask for confirmation from the user.

        Args:
            message: The question to ask.
            default: The default value if user just presses Enter.

        Returns:
            True if confirmed, False otherwise.
        """
        hint = "[Y/n]" if default else "[y/N]"
        response = self.input(f"{message} {hint}: ").strip().lower()

        if not response:
            return default

        return response in ("y", "yes")
