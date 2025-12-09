"""Task display components for the Todo application."""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models import Priority, Reminder, Status, Task
from .console import Console


# Priority color mapping
PRIORITY_COLORS = {
    Priority.HIGH: "red",
    Priority.MEDIUM: "yellow",
    Priority.LOW: "green",
}

# Status indicators
STATUS_INDICATORS = {
    Status.COMPLETE: "[bold green]✓[/bold green]",
    Status.INCOMPLETE: "[ ]",
}


def create_task_table(tasks: list[Task], title: str = "Tasks") -> Table:
    """
    Create a rich Table displaying tasks.

    Args:
        tasks: List of tasks to display.
        title: Table title.

    Returns:
        A rich Table object.
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")

    # Add columns
    table.add_column("ID", style="dim", width=4)
    table.add_column("Status", width=6, justify="center")
    table.add_column("Title", min_width=20)
    table.add_column("Priority", width=8, justify="center")
    table.add_column("Due Date", width=12)
    table.add_column("Categories", width=15)

    # Add rows
    for task in tasks:
        # Status indicator
        status = STATUS_INDICATORS[task.status]

        # Priority with color
        priority_color = PRIORITY_COLORS[task.priority]
        priority_text = f"[{priority_color}]{task.priority.value.capitalize()}[/{priority_color}]"

        # Due date with optional time
        if task.due_date:
            due_display = task.due_date
            if task.due_time:
                # Show just HH:MM for compactness
                due_display += f" {task.due_time[:5]}"
        else:
            due_display = "-"

        # Categories (with recurrence indicator)
        categories = ", ".join(task.categories) if task.categories else "-"
        if task.is_recurring():
            categories = f"🔄 {categories}" if categories != "-" else "🔄"

        # Title (strike through if complete)
        title = task.title
        if task.status == Status.COMPLETE:
            title = f"[strike]{title}[/strike]"

        table.add_row(
            str(task.id),
            status,
            title,
            priority_text,
            due_display,
            categories,
        )

    return table


def display_tasks(console: Console, tasks: list[Task], title: str = "Tasks") -> None:
    """
    Display tasks in a formatted table.

    Args:
        console: The console to print to.
        tasks: List of tasks to display.
        title: Table title.
    """
    if not tasks:
        console.info("No tasks found.")
        return

    table = create_task_table(tasks, title)
    console.print(table)
    console.blank()
    console.info(f"Total: {len(tasks)} task(s)")


def display_task_detail(console: Console, task: Task) -> None:
    """
    Display detailed information about a single task.

    Args:
        console: The console to print to.
        task: The task to display.
    """
    priority_color = PRIORITY_COLORS[task.priority]
    status_text = "Complete" if task.status == Status.COMPLETE else "Incomplete"

    console.blank()
    console.print(f"[bold]Task #{task.id}[/bold]")
    console.print(f"  Title: {task.title}")
    console.print(f"  Description: {task.description or '(none)'}")
    console.print(f"  Priority: [{priority_color}]{task.priority.value.capitalize()}[/{priority_color}]")
    console.print(f"  Status: {status_text}")

    # Display due date with optional time
    if task.due_date:
        due_display = task.due_date
        if task.due_time:
            due_display += f" at {task.due_time}"
        console.print(f"  Due: {due_display}")
    else:
        console.print("  Due Date: (none)")

    console.print(f"  Categories: {', '.join(task.categories) if task.categories else '(none)'}")

    # Display recurrence info
    if task.is_recurring():
        console.print(f"  [cyan]{task.recurrence}[/cyan]")
        if task.series_id:
            console.print(f"  Series ID: {task.series_id[:8]}...")

    # Display reminders
    if task.has_reminders():
        reminder_texts = [r.get_display_text() for r in task.reminders if not r.shown]
        if reminder_texts:
            console.print(f"  Reminders: {', '.join(reminder_texts)}")

    console.print(f"  Created: {task.created_at}")
    console.blank()


def show_reminder_notification(console: Console, reminder: Reminder, task: Task) -> None:
    """
    Display a reminder notification using a rich Panel.

    Args:
        console: The console to print to.
        reminder: The reminder that triggered.
        task: The associated task.
    """
    priority_color = PRIORITY_COLORS[task.priority]

    # Build notification content
    content_lines = [
        f"[bold]{task.title}[/bold]",
        "",
        f"Due: {task.due_date}",
    ]
    if task.due_time:
        content_lines[-1] += f" at {task.due_time}"

    if task.description:
        content_lines.append(f"Description: {task.description[:50]}...")

    content_lines.append(f"Priority: [{priority_color}]{task.priority.value.capitalize()}[/{priority_color}]")

    content = "\n".join(content_lines)

    # Create and display panel
    panel = Panel(
        content,
        title="[bold yellow]⏰ REMINDER[/bold yellow]",
        subtitle=f"Task #{task.id}",
        border_style="yellow",
        padding=(1, 2),
    )

    console.blank()
    console.print(panel)
    console.blank()
