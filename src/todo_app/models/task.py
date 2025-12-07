from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """
    A todo item with a description, unique identifier, and completion status.
    """
    id: str  # Unique auto-generated short code identifier (format: TSK-###)
    description: str
    completed: bool = False
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def validate_id_format(self) -> bool:
        """
        Validate that the task ID follows the format TSK-### where ### is a 3-digit number.
        """
        import re
        pattern = r"^TSK-\d{3}$"
        return bool(re.match(pattern, self.id))

    def validate_description(self) -> bool:
        """
        Validate that the task description is not empty or contain only whitespace.
        """
        return bool(self.description and self.description.strip())