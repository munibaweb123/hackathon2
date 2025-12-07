#!/usr/bin/env python3
"""
Main entry point for the Todo In-Memory Python Console App.
"""
import argparse
import sys
from .services.task_service import TaskList
from .cli.cli import TodoCLI


def main():
    """
    Main function to run the todo application.
    """
    # Create shared instances
    task_list = TaskList()
    cli = TodoCLI(task_list)

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Todo In-Memory Python Console App")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", nargs="*", help="Task description")

    # List command
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("--completed", action="store_true", help="Show only completed tasks")
    list_parser.add_argument("--pending", action="store_true", help="Show only pending tasks")

    # Alias for list command
    view_parser = subparsers.add_parser("view", help="View all tasks")
    view_parser.add_argument("--completed", action="store_true", help="Show only completed tasks")
    view_parser.add_argument("--pending", action="store_true", help="Show only pending tasks")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark task as complete")
    complete_parser.add_argument("task_id", help="Task ID in TSK-### format")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update task description")
    update_parser.add_argument("task_id", help="Task ID in TSK-### format")
    update_parser.add_argument("new_description", nargs="*", help="New task description")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID in TSK-### format")

    # Help command
    subparsers.add_parser("help", help="Show help information")

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "add":
        if not args.description:
            print("Error: Task description is required")
            sys.exit(1)
        description = " ".join(args.description)
        result = cli.add_task(description)
        print(result)

    elif args.command in ["list", "view"]:
        if args.completed:
            tasks = task_list.find_tasks_by_status(completed=True)
            print("Completed Tasks:")
            if not tasks:
                print("No completed tasks found.")
            else:
                for task in tasks:
                    print(f"{task.id} [x] {task.description}")
        elif args.pending:
            tasks = task_list.find_tasks_by_status(completed=False)
            print("Pending Tasks:")
            if not tasks:
                print("No pending tasks found.")
            else:
                for task in tasks:
                    print(f"{task.id} [ ] {task.description}")
        else:
            result = cli.list_tasks()
            print(result)

    elif args.command == "complete":
        result = cli.complete_task(args.task_id)
        print(result)

    elif args.command == "update":
        if not args.new_description:
            print("Error: New task description is required")
            sys.exit(1)
        new_description = " ".join(args.new_description)
        result = cli.update_task(args.task_id, new_description)
        print(result)

    elif args.command == "delete":
        result = cli.delete_task(args.task_id)
        print(result)

    elif args.command == "help" or not args.command:
        parser.print_help()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    main()