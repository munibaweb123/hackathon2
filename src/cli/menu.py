"""Menu module for the Todo Console Application CLI."""

from src.models.task import Task
from src.services.task_service import TaskService


def display_menu() -> None:
    """Display the main menu options."""
    print("\n" + "=" * 30)
    print("       TODO APP MENU")
    print("=" * 30)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Complete")
    print("4. Mark Incomplete")
    print("5. Update Task")
    print("6. Delete Task")
    print("7. Exit")
    print("=" * 30)


def get_user_choice() -> str:
    """Get user's menu choice.

    Returns:
        The user's input string.
    """
    return input("Select option (1-7): ").strip()


def format_task(task: Task) -> str:
    """Format a task for display.

    Args:
        task: The task to format.

    Returns:
        Formatted string with status indicator.
    """
    status = "[X]" if task.completed else "[ ]"
    result = f"{status} {task.id}. {task.title}"
    if task.description:
        result += f"\n    {task.description}"
    return result


def get_task_id(prompt: str = "Enter task ID: ") -> int | None:
    """Get and validate a task ID from user input.

    Args:
        prompt: The prompt to display.

    Returns:
        The task ID as integer, or None if invalid.
    """
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Error: Invalid ID format. Please enter a number.")
        return None


def handle_add_task(service: TaskService) -> None:
    """Handle adding a new task.

    Args:
        service: The TaskService instance.
    """
    print("\n--- Add Task ---")
    title = input("Enter title: ").strip()

    if not title:
        print("Error: Task title cannot be empty.")
        return

    description = input("Enter description (optional): ").strip()

    try:
        task = service.add_task(title, description)
        print(f"Task added with ID: {task.id}")
    except ValueError as e:
        print(f"Error: {e}")


def handle_view_tasks(service: TaskService) -> None:
    """Handle viewing all tasks.

    Args:
        service: The TaskService instance.
    """
    print("\n--- All Tasks ---")
    tasks = service.get_all_tasks()

    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        print(format_task(task))


def handle_mark_complete(service: TaskService) -> None:
    """Handle marking a task as complete.

    Args:
        service: The TaskService instance.
    """
    print("\n--- Mark Complete ---")
    task_id = get_task_id()

    if task_id is None:
        return

    if service.mark_complete(task_id):
        print(f"Task {task_id} marked as complete.")
    else:
        print("Error: Task not found.")


def handle_mark_incomplete(service: TaskService) -> None:
    """Handle marking a task as incomplete.

    Args:
        service: The TaskService instance.
    """
    print("\n--- Mark Incomplete ---")
    task_id = get_task_id()

    if task_id is None:
        return

    if service.mark_incomplete(task_id):
        print(f"Task {task_id} marked as incomplete.")
    else:
        print("Error: Task not found.")


def handle_update_task(service: TaskService) -> None:
    """Handle updating a task's details.

    Args:
        service: The TaskService instance.
    """
    print("\n--- Update Task ---")
    task_id = get_task_id()

    if task_id is None:
        return

    task = service.get_task(task_id)
    if task is None:
        print("Error: Task not found.")
        return

    print(f"Current title: {task.title}")
    new_title = input("Enter new title (press Enter to keep current): ").strip()

    print(f"Current description: {task.description or '(empty)'}")
    new_description = input(
        "Enter new description (press Enter to keep current): "
    ).strip()

    # Use None to indicate "keep current value"
    title_to_update = new_title if new_title else None
    description_to_update = new_description if new_description else None

    # Only update if at least one field is being changed
    if title_to_update is None and description_to_update is None:
        print("No changes made.")
        return

    try:
        service.update_task(task_id, title_to_update, description_to_update)
        print(f"Task {task_id} updated successfully.")
    except ValueError as e:
        print(f"Error: {e}")


def handle_delete_task(service: TaskService) -> None:
    """Handle deleting a task.

    Args:
        service: The TaskService instance.
    """
    print("\n--- Delete Task ---")
    task_id = get_task_id()

    if task_id is None:
        return

    if service.delete_task(task_id):
        print(f"Task {task_id} deleted successfully.")
    else:
        print("Error: Task not found.")


def run_menu_loop(service: TaskService) -> None:
    """Run the main menu loop.

    Args:
        service: The TaskService instance to use.
    """
    handlers = {
        "1": handle_add_task,
        "2": handle_view_tasks,
        "3": handle_mark_complete,
        "4": handle_mark_incomplete,
        "5": handle_update_task,
        "6": handle_delete_task,
    }

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == "7":
            print("\nGoodbye!")
            break

        handler = handlers.get(choice)
        if handler:
            handler(service)
        else:
            print("Error: Invalid option. Please select 1-7.")
