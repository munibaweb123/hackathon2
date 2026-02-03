"""Audit log retention - 30-day cleanup job."""

from datetime import datetime, timezone, timedelta
from typing import Optional

import asyncpg


class RetentionJob:
    def __init__(self, database_url: str, retention_days: int = 30):
        self.database_url = database_url
        self.retention_days = retention_days

    async def cleanup(self) -> int:
        if not self.database_url:
            return 0

        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        conn = await asyncpg.connect(self.database_url)
        try:
            result = await conn.execute(
                "DELETE FROM audit_logs WHERE timestamp < $1", cutoff
            )
            # result is like "DELETE 42"
            return int(result.split()[-1])
        finally:
            await conn.close()
