"""Audit log writer - persists audit entries to PostgreSQL."""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

import asyncpg


class AuditLogWriter:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None

    async def initialize(self):
        if self.database_url:
            self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=5)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def write(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        action: str,
        old_data: Optional[dict] = None,
        new_data: Optional[dict] = None,
        correlation_id: Optional[str] = None,
    ):
        if not self.pool:
            return

        await self.pool.execute(
            """
            INSERT INTO audit_logs (id, user_id, entity_type, entity_id, action, old_data, new_data, timestamp, correlation_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            str(uuid.uuid4()),
            user_id,
            entity_type,
            entity_id,
            action,
            json.dumps(old_data) if old_data else None,
            json.dumps(new_data) if new_data else None,
            datetime.now(timezone.utc),
            correlation_id,
        )
