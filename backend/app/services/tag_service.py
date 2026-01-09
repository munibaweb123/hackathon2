"""Tag service for handling business logic related to tags."""

from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID

from app.models.tag import Tag
from app.models.task_tag import TaskTag
from app.models.task import Task
from app.schemas.tag import TagCreate, TagUpdate


class TagService:
    """Service for managing tags."""

    def __init__(self, session: Session):
        self.session = session

    def create_tag(self, tag_data: TagCreate, user_id: str) -> Tag:
        """Create a new tag for a user."""
        # Check if tag with same name already exists for this user
        existing_tag = self.session.exec(
            select(Tag).where(
                Tag.user_id == user_id,
                Tag.name == tag_data.name
            )
        ).first()

        if existing_tag:
            raise ValueError(f"Tag with name '{tag_data.name}' already exists for this user")

        tag = Tag(
            name=tag_data.name,
            color=tag_data.color,
            user_id=user_id
        )
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        return tag

    def get_tag_by_id(self, tag_id: str, user_id: str) -> Optional[Tag]:
        """Get a specific tag by its ID for a specific user."""
        try:
            tag_uuid = UUID(tag_id)
        except ValueError:
            return None

        statement = select(Tag).where(
            Tag.id == tag_uuid,
            Tag.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_tags_by_user_id(self, user_id: str) -> List[Tag]:
        """Get all tags for a specific user."""
        statement = select(Tag).where(Tag.user_id == user_id)
        return self.session.exec(statement).all()

    def update_tag(self, tag_id: str, user_id: str, tag_data: TagUpdate) -> Optional[Tag]:
        """Update a tag for a user."""
        try:
            tag_uuid = UUID(tag_id)
        except ValueError:
            return None

        statement = select(Tag).where(
            Tag.id == tag_uuid,
            Tag.user_id == user_id
        )
        tag = self.session.exec(statement).first()

        if not tag:
            return None

        # Update fields that are provided
        update_data = tag_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(tag, field):
                setattr(tag, field, value)

        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        return tag

    def delete_tag(self, tag_id: str, user_id: str) -> bool:
        """Delete a tag for a user."""
        try:
            tag_uuid = UUID(tag_id)
        except ValueError:
            return False

        statement = select(Tag).where(
            Tag.id == tag_uuid,
            Tag.user_id == user_id
        )
        tag = self.session.exec(statement).first()

        if not tag:
            return False

        # Remove all associations with tasks
        task_tag_statement = select(TaskTag).where(TaskTag.tag_id == tag_uuid)
        task_tags = self.session.exec(task_tag_statement).all()
        for task_tag in task_tags:
            self.session.delete(task_tag)

        self.session.delete(tag)
        self.session.commit()
        return True

    def add_tag_to_task(self, task_id: int, tag_id: str, user_id: str) -> bool:
        """Add a tag to a task."""
        try:
            tag_uuid = UUID(tag_id)
        except ValueError:
            return False

        # Verify that the tag belongs to the user
        tag = self.session.exec(
            select(Tag).where(
                Tag.id == tag_uuid,
                Tag.user_id == user_id
            )
        ).first()

        if not tag:
            return False

        # Verify that the task belongs to the user
        task = self.session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).first()

        if not task:
            return False

        # Check if the association already exists
        existing = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_uuid
            )
        ).first()

        if existing:
            return True  # Already exists, return True

        task_tag = TaskTag(
            task_id=task_id,
            tag_id=tag_uuid
        )
        self.session.add(task_tag)
        self.session.commit()
        return True

    def remove_tag_from_task(self, task_id: int, tag_id: str, user_id: str) -> bool:
        """Remove a tag from a task."""
        try:
            tag_uuid = UUID(tag_id)
        except ValueError:
            return False

        # Verify that the tag belongs to the user
        tag = self.session.exec(
            select(Tag).where(
                Tag.id == tag_uuid,
                Tag.user_id == user_id
            )
        ).first()

        if not tag:
            return False

        # Remove the association
        task_tag_statement = select(TaskTag).where(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_uuid
        )
        task_tag = self.session.exec(task_tag_statement).first()

        if not task_tag:
            return False

        self.session.delete(task_tag)
        self.session.commit()
        return True

    def get_tags_for_task(self, task_id: int, user_id: str) -> List[Tag]:
        """Get all tags for a specific task."""
        # Verify that the task belongs to the user
        task = self.session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).first()

        if not task:
            return []

        # Get all tags associated with this task
        statement = (
            select(Tag)
            .join(TaskTag)
            .where(TaskTag.task_id == task_id)
        )
        return self.session.exec(statement).all()

    def get_tasks_for_tag(self, tag_id: str, user_id: str) -> List[Task]:
        """Get all tasks associated with a specific tag."""
        try:
            tag_uuid = UUID(tag_id)
        except ValueError:
            return []

        # Verify that the tag belongs to the user
        tag = self.session.exec(
            select(Tag).where(
                Tag.id == tag_uuid,
                Tag.user_id == user_id
            )
        ).first()

        if not tag:
            return []

        # Get all tasks associated with this tag
        statement = (
            select(Task)
            .join(TaskTag)
            .where(TaskTag.tag_id == tag_uuid)
        )
        return self.session.exec(statement).all()


def get_tag_service(session: Session) -> TagService:
    """Factory function to get a TagService instance."""
    return TagService(session)