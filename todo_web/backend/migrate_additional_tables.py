"""Database migration script to add reminders and preferences tables."""

from sqlmodel import create_engine
from sqlalchemy import text
from app.core.config import settings

def run_migration():
    # Create engine
    engine = create_engine(settings.DATABASE_URL)

    # SQL statements to create reminders and preferences tables
    migration_sql = """
    -- Create reminders table
    CREATE TABLE IF NOT EXISTS reminders (
        id VARCHAR(255) PRIMARY KEY,
        task_id VARCHAR(255) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        reminder_time TIMESTAMP NOT NULL,
        reminder_type VARCHAR(20) DEFAULT 'push',
        status VARCHAR(20) DEFAULT 'pending',
        message VARCHAR(500),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_reminder_user_id (user_id),
        INDEX idx_reminder_task_id (task_id),
        INDEX idx_reminder_time (reminder_time),
        INDEX idx_reminder_status (status)
    );

    -- Create user_preferences table
    CREATE TABLE IF NOT EXISTS user_preferences (
        id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255) UNIQUE NOT NULL,
        theme VARCHAR(20) DEFAULT 'auto',
        language VARCHAR(10) DEFAULT 'en',
        task_notifications VARCHAR(20) DEFAULT 'all',
        reminder_notifications VARCHAR(20) DEFAULT 'all',
        email_notifications BOOLEAN DEFAULT TRUE,
        default_view VARCHAR(20) DEFAULT 'list',
        show_completed_tasks BOOLEAN DEFAULT TRUE,
        group_by VARCHAR(20) DEFAULT 'none',
        auto_archive_completed BOOLEAN DEFAULT FALSE,
        auto_snooze_time INTEGER,
        work_hours_start VARCHAR(5) DEFAULT '09:00',
        work_hours_end VARCHAR(5) DEFAULT '17:00',
        custom_settings TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_preferences_user_id (user_id)
    );
    """

    with engine.connect() as conn:
        conn.execute(text(migration_sql))
        conn.commit()

    print("Reminders and preferences tables created successfully!")

if __name__ == "__main__":
    run_migration()