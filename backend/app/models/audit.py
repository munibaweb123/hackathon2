"""AuditLog model for immutable record of all task operations."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON

from .enums import AuditAction


class AuditLog(SQLModel, table=True):
    """Immutable record of all task operations for compliance and debugging."""

    __tablename__ = "audit_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(nullable=False, index=True)
    entity_type: str = Field(max_length=50, nullable=False)  # 'task', 'tag', etc.
    entity_id: str = Field(nullable=False)  # ID of affected entity (string to support various ID types)
    action: AuditAction = Field(nullable=False)

    # State snapshots stored as JSON
    old_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )
    new_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )

    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    correlation_id: Optional[UUID] = Field(default=None)  # Request correlation ID for tracing

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-123",
                "entity_type": "task",
                "entity_id": "456",
                "action": "updated",
                "old_data": {"title": "Old Title", "completed": False},
                "new_data": {"title": "New Title", "completed": False},
                "timestamp": "2024-12-10T10:00:00Z",
                "correlation_id": "789e4567-e89b-12d3-a456-426614174000"
            }
        }
