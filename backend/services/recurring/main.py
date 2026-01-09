"""Recurring task microservice main entry point.

This service handles:
- Receiving task completion events from Dapr Pub/Sub
- Generating next occurrences for completed recurring tasks
- Managing recurrence lifecycle events

Dapr subscription handler for 'task-events' topic.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app for Dapr subscriptions
app = FastAPI(
    title="Recurring Task Service",
    description="Handles recurring task generation based on completion events",
    version="1.0.0",
)

# Environment configuration
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")
TOPIC_TASK_EVENTS = "task-events"


class TaskEventType(str, Enum):
    """Valid task event types."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"


class TaskEvent(BaseModel):
    """Schema for incoming task events from Dapr Pub/Sub."""
    event_id: UUID
    event_type: TaskEventType
    task_id: int
    user_id: str
    task_data: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[UUID] = None


class CloudEvent(BaseModel):
    """CloudEvents specification wrapper for Dapr subscriptions."""
    id: str
    source: str
    specversion: str = "1.0"
    type: str
    datacontenttype: str = "application/json"
    data: Dict[str, Any]
    time: Optional[datetime] = None
    traceparent: Optional[str] = None


# Import task generator (created in parallel tasks)
from .task_generator import generate_next_occurrence


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns the list of topics this service subscribes to.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_TASK_EVENTS,
            "route": "/task-events",
        }
    ]


@app.post("/task-events")
async def handle_task_event(request: Request):
    """
    Handle incoming task events from Dapr Pub/Sub.

    This endpoint receives CloudEvents from Kafka/Redpanda and
    processes recurring task generation when tasks are completed.
    """
    try:
        # Parse the incoming CloudEvent
        body = await request.json()
        logger.info(f"Received task event: {body.get('id', 'unknown')}")

        # Extract the event data
        if "data" in body:
            # CloudEvents format
            event_data = body["data"]
        else:
            # Raw event format
            event_data = body

        # Parse the task event
        task_event = TaskEvent(**event_data)

        # Only process completed events for recurring tasks
        if task_event.event_type != TaskEventType.COMPLETED:
            logger.info(f"Ignoring {task_event.event_type} event for task {task_event.task_id}")
            return {"status": "IGNORED"}

        # Check if this is a recurring task
        if not task_event.task_data.get("recurrence_id"):
            logger.info(f"Task {task_event.task_id} is not recurring, skipping")
            return {"status": "IGNORED"}

        # Generate the next occurrence
        success = await generate_next_occurrence(
            original_task_id=task_event.task_id,
            user_id=task_event.user_id,
            task_data=task_event.task_data
        )

        if success:
            logger.info(f"Successfully generated next occurrence for recurring task {task_event.task_id}")
            return {"status": "SUCCESS"}
        else:
            logger.warning(f"Failed to generate next occurrence for recurring task {task_event.task_id}")
            return {"status": "FAILED"}

    except Exception as e:
        logger.exception(f"Error processing task event: {e}")
        # Return success anyway to avoid message redelivery for bad messages
        return {"status": "DROP"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {
        "status": "healthy",
        "service": "recurring",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes probes."""
    return {
        "status": "ready",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)