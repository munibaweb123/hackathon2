"""Action model for ChatKit implementation."""
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .thread import Thread  # Assuming Thread model exists
    from .widget import Widget  # Assuming Widget model exists


class ActionBase(SQLModel):
    """Base model for Action with shared attributes."""
    thread_id: UUID = Field(index=True, description="Reference to the thread where action occurred")
    type: str = Field(description="Type of action (button_click, form_submit, etc.)")
    payload: str = Field(description="Data associated with the action")


class Action(ActionBase, table=True):
    """Action model representing user interaction event with type, payload, and sender information that triggers backend processing."""
    __tablename__ = "actions"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="Unique identifier for the action")
    widget_id: Optional[str] = Field(None, index=True, description="Reference to the widget that triggered this action")
    thread_id: UUID = Field(description="Reference to the thread where action occurred")
    type: str = Field(description="Type of action (button_click, form_submit, etc.)")
    payload: str = Field(description="Data associated with the action")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the action was triggered")
    processed_at: Optional[datetime] = Field(None, description="Timestamp when the action was processed")
    result: Optional[str] = Field(None, description="Result of the action processing")


class ActionPublic(ActionBase):
    """Public model for Action without sensitive information."""
    id: UUID
    widget_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    result: Optional[str] = None


class ActionCreate(ActionBase):
    """Model for creating a new Action."""
    pass


class ActionUpdate(SQLModel):
    """Model for updating an existing Action."""
    widget_id: Optional[str] = None
    processed_at: Optional[datetime] = None
    result: Optional[str] = None