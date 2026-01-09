"""Add AuditLog table

Revision ID: 005
Revises: 004
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create audit action enum
    action_enum = sa.Enum('created', 'updated', 'deleted', 'completed', name='auditaction')
    action_enum.create(op.get_bind())

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('action', action_enum, nullable=False),
        sa.Column('old_data', JSONB(), nullable=True),
        sa.Column('new_data', JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('correlation_id', UUID(as_uuid=True), nullable=True),
    )

    # Create indexes for common query patterns
    op.create_index('idx_audit_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'])


def downgrade():
    op.drop_index('idx_audit_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_entity', table_name='audit_logs')
    op.drop_index('idx_audit_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')
    sa.Enum(name='auditaction').drop(op.get_bind())
