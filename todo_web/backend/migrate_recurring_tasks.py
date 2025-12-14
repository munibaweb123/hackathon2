"""Database migration script to add recurring task fields to existing tasks table."""

import os
from sqlmodel import create_engine
from sqlalchemy import text
from app.core.config import settings

def run_migration():
    # Create engine
    engine = create_engine(settings.DATABASE_URL)

    # SQL statements to add missing columns
    migration_sql = """
    -- Add recurring task columns to tasks table
    ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE;
    ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20);
    ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_interval INTEGER DEFAULT 1;
    ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_end_date TIMESTAMP;
    ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id VARCHAR(255);

    -- Add foreign key constraint for parent_task_id
    ALTER TABLE tasks ADD CONSTRAINT fk_tasks_parent_task_id
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id);
    """

    with engine.connect() as conn:
        conn.execute(text(migration_sql))
        conn.commit()

    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()