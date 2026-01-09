"""Add NotificationPreference table

Revision ID: 006
Revises: 005
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('reminder_lead_time', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('quiet_hours_start', sa.Time(), nullable=True),
        sa.Column('quiet_hours_end', sa.Time(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('reminder_lead_time >= 0', name='check_lead_time_positive'),
    )

    # Create index on user_id
    op.create_index('idx_notification_prefs_user_id', 'notification_preferences', ['user_id'])


def downgrade():
    op.drop_index('idx_notification_prefs_user_id', table_name='notification_preferences')
    op.drop_table('notification_preferences')
