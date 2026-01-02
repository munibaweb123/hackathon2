"""Widget factories and components for ChatKit implementation in the todo application."""

from typing import List, Optional, Dict, Any
from ..models.task import Task


class WidgetFactory:
    """Factory class for creating various ChatKit widgets."""

    @staticmethod
    def create_task_widget(task: Task) -> Dict[str, Any]:
        """
        Create a widget to display a single task.

        Args:
            task: The task object to display

        Returns:
            Dictionary representing the task widget
        """
        return {
            "id": f"task_{task.id}",
            "type": "card",
            "children": [
                {
                    "id": f"task_row_{task.id}",
                    "type": "row",
                    "children": [
                        {
                            "id": f"task_title_{task.id}",
                            "type": "text",
                            "props": {
                                "text": task.title,
                                "weight": "bold" if task.priority == "high" else "normal"
                            }
                        },
                        {
                            "id": f"task_status_badge_{task.id}",
                            "type": "badge",
                            "props": {
                                "text": "Completed" if task.completed else "Pending",
                                "color": "success" if task.completed else "warning"
                            }
                        }
                    ]
                },
                {
                    "id": f"task_description_{task.id}",
                    "type": "text",
                    "props": {
                        "text": task.description or "",
                        "size": "sm"
                    }
                },
                {
                    "id": f"task_details_{task.id}",
                    "type": "row",
                    "children": [
                        {
                            "id": f"task_priority_{task.id}",
                            "type": "badge",
                            "props": {
                                "text": task.priority or "normal",
                                "color": "primary"
                            }
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def create_task_list_widget(tasks: List[Task], title: str = "Your Tasks") -> Dict[str, Any]:
        """
        Create a widget to display a list of tasks.

        Args:
            tasks: List of task objects to display
            title: Title for the task list

        Returns:
            Dictionary representing the task list widget
        """
        task_items = []
        for task in tasks:
            task_items.append(WidgetFactory.create_task_widget(task))

        return {
            "id": "task_list_card",
            "type": "card",
            "children": [
                {
                    "id": "task_list_headline",
                    "type": "headline",
                    "props": {
                        "text": title
                    }
                },
                {
                    "id": "task_list",
                    "type": "listview",
                    "children": task_items
                },
                {
                    "id": "task_count_badge",
                    "type": "badge",
                    "props": {
                        "text": f"{len(tasks)} tasks",
                        "color": "primary"
                    }
                }
            ]
        }

    @staticmethod
    def create_empty_state_widget(message: str = "No tasks found") -> Dict[str, Any]:
        """
        Create a widget to display when there are no tasks.

        Args:
            message: Message to display in the empty state

        Returns:
            Dictionary representing the empty state widget
        """
        return {
            "id": "empty_state_card",
            "type": "card",
            "children": [
                {
                    "id": "empty_state_text",
                    "type": "text",
                    "props": {
                        "text": message,
                        "align": "center"
                    }
                }
            ]
        }

    @staticmethod
    def create_button_widget(id: str, text: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a button widget with specified action.

        Args:
            id: Unique identifier for the button
            text: Text to display on the button
            action: Action to perform when button is clicked

        Returns:
            Dictionary representing the button widget
        """
        return {
            "id": id,
            "type": "button",
            "props": {
                "text": text,
                "action": action
            }
        }

    @staticmethod
    def create_confirmation_dialog_widget(
        title: str,
        message: str,
        confirm_action: Dict[str, Any],
        cancel_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a confirmation dialog widget.

        Args:
            title: Title of the confirmation dialog
            message: Message to display in the dialog
            confirm_action: Action to perform when confirmed
            cancel_action: Action to perform when canceled

        Returns:
            Dictionary representing the confirmation dialog widget
        """
        return {
            "id": "confirmation_dialog",
            "type": "card",
            "children": [
                {
                    "id": "dialog_title",
                    "type": "headline",
                    "props": {
                        "text": title
                    }
                },
                {
                    "id": "dialog_message",
                    "type": "text",
                    "props": {
                        "text": message
                    }
                },
                {
                    "id": "dialog_buttons",
                    "type": "row",
                    "children": [
                        WidgetFactory.create_button_widget(
                            "confirm_button",
                            "Confirm",
                            confirm_action
                        ),
                        WidgetFactory.create_button_widget(
                            "cancel_button",
                            "Cancel",
                            cancel_action
                        )
                    ]
                }
            ]
        }

    @staticmethod
    def create_success_confirmation_widget(message: str, task_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a success confirmation widget.

        Args:
            message: Success message to display
            task_details: Optional task details to show

        Returns:
            Dictionary representing the success confirmation widget
        """
        children = [
            {
                "id": "success_message",
                "type": "text",
                "props": {
                    "text": message,
                    "color": "success"
                }
            }
        ]

        if task_details:
            children.append({
                "id": "task_details",
                "type": "card",
                "children": [
                    {
                        "id": "task_title",
                        "type": "text",
                        "props": {
                            "text": task_details.get("title", ""),
                            "weight": "bold"
                        }
                    }
                ]
            })

        return {
            "id": "success_confirmation",
            "type": "card",
            "children": children
        }