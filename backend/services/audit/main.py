"""Audit Log Microservice - Subscribes to task-events and writes audit logs."""

import os
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
import httpx

from log_writer import AuditLogWriter
from retention import RetentionJob

DATABASE_URL = os.getenv("DATABASE_URL", "")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")

log_writer = AuditLogWriter(DATABASE_URL)
retention_job = RetentionJob(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await log_writer.initialize()
    yield
    await log_writer.close()


app = FastAPI(title="Audit Service", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "audit"}


@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events",
        }
    ]


@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """Handle task events from Dapr pub/sub and write audit log entries."""
    event = await request.json()
    data = event.get("data", event)

    await log_writer.write(
        user_id=data.get("user_id"),
        entity_type="task",
        entity_id=data.get("task_id"),
        action=data.get("event_type", "unknown"),
        old_data=data.get("old_data"),
        new_data=data.get("task_data"),
        correlation_id=data.get("correlation_id"),
    )

    return {"status": "SUCCESS"}


@app.post("/api/retention/run")
async def trigger_retention():
    """Manually trigger audit log retention cleanup."""
    deleted = await retention_job.cleanup()
    return {"deleted": deleted}
