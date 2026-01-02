"""Widget model for ChatKit implementation."""
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .message import Message  # Assuming Message model exists


class WidgetBase(SQLModel):
    """Base model for Widget with shared attributes."""
    message_id: UUID = Field(index=True, description="Reference to the message this widget is associated with")
    type: str = Field(description="Widget type (card, text, button, listview, etc.)")
    payload: str = Field(description="The actual widget data following ChatKit schema")


class Widget(WidgetBase, table=True):
    """Widget model representing JSON structure containing type, id, children, and action definitions that render as interactive UI components."""
    __tablename__ = "widgets"

    id: str = Field(primary_key=True, description="Unique identifier for the widget within the thread")
    message_id: UUID = Field(description="Reference to the message this widget is associated with")
    type: str = Field(description="Widget type (card, text, button, listview, etc.)")
    payload: str = Field(description="The actual widget data following ChatKit schema")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the widget was created")
    action_handler: Optional[str] = Field(None, description="Optional reference to the action handler function")


class WidgetPublic(WidgetBase):
    """Public model for Widget without sensitive information."""
    id: str
    created_at: datetime
    action_handler: Optional[str] = None


class WidgetCreate(WidgetBase):
    """Model for creating a new Widget."""
    id: str  # ID needs to be provided for widgets


class WidgetUpdate(SQLModel):
    """Model for updating an existing Widget."""
    payload: Optional[str] = None
    action_handler: Optional[str] = None