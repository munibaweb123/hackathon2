"""Add RecurrencePattern table and enums

Revision ID: 004
Revises: 003
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    frequency_enum = sa.Enum('daily', 'weekly', 'monthly', 'yearly', 'custom', name='recurrencefrequency')
    status_enum = sa.Enum('active', 'completed', 'cancelled', name='recurrencestatus')

    frequency_enum.create(op.get_bind())
    status_enum.create(op.get_bind())

    # Create recurrence_patterns table
    op.create_table(
        'recurrence_patterns',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('frequency', frequency_enum, nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('day_of_week', ARRAY(sa.Integer()), nullable=True),
        sa.Column('day_of_month', ARRAY(sa.Integer()), nullable=True),
        sa.Column('month_of_year', ARRAY(sa.Integer()), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('count', sa.Integer(), nullable=True),
        sa.Column('status', status_enum, nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('interval >= 1', name='check_interval_positive'),
    )

    # Add foreign key constraint to tasks table
    op.create_foreign_key(
        'fk_tasks_recurrence_id',
        'tasks', 'recurrence_patterns',
        ['recurrence_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    op.drop_constraint('fk_tasks_recurrence_id', 'tasks', type_='foreignkey')
    op.drop_table('recurrence_patterns')
    sa.Enum(name='recurrencestatus').drop(op.get_bind())
    sa.Enum(name='recurrencefrequency').drop(op.get_bind())
