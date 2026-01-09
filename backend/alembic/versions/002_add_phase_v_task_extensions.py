"""Add Phase V task extensions (priority, due_date, reminder_at, status)

Revision ID: 002
Revises: 001_create_chatkit_entities
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001_create_chatkit_entities'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    priority_enum = sa.Enum('none', 'low', 'medium', 'high', name='priority')
    status_enum = sa.Enum('pending', 'in_progress', 'completed', name='taskstatus')

    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('status', status_enum, nullable=False, server_default='pending'))
    op.add_column('tasks', sa.Column('reminder_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_id', UUID(as_uuid=True), nullable=True))

    # Update priority column to use new enum with 'none' default
    # First, add a temporary column
    op.add_column('tasks', sa.Column('priority_new', priority_enum, nullable=False, server_default='none'))

    # Migrate existing data
    op.execute("""
        UPDATE tasks
        SET priority_new = CASE
            WHEN priority = 'low' THEN 'low'::priority
            WHEN priority = 'medium' THEN 'medium'::priority
            WHEN priority = 'high' THEN 'high'::priority
            ELSE 'none'::priority
        END
    """)

    # Drop old column and rename new one
    op.drop_column('tasks', 'priority')
    op.alter_column('tasks', 'priority_new', new_column_name='priority')

    # Create indexes
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'], postgresql_where=sa.text('due_date IS NOT NULL'))
    op.create_index('idx_tasks_recurrence_id', 'tasks', ['recurrence_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_tasks_recurrence_id', table_name='tasks')
    op.drop_index('idx_tasks_due_date', table_name='tasks')
    op.drop_index('idx_tasks_priority', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')

    # Remove columns
    op.drop_column('tasks', 'recurrence_id')
    op.drop_column('tasks', 'reminder_at')
    op.drop_column('tasks', 'status')

    # Restore old priority (medium default)
    old_priority_enum = sa.Enum('low', 'medium', 'high', name='priority_old')
    op.add_column('tasks', sa.Column('priority_old', old_priority_enum, nullable=False, server_default='medium'))
    op.drop_column('tasks', 'priority')
    op.alter_column('tasks', 'priority_old', new_column_name='priority')

    # Drop enums
    sa.Enum(name='taskstatus').drop(op.get_bind())
    sa.Enum(name='priority').drop(op.get_bind())
