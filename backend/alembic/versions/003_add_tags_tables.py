"""Add Tag and TaskTag tables

Revision ID: 003
Revises: 002
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create unique constraint for user_id + name
    op.create_unique_constraint('uq_tags_user_name', 'tags', ['user_id', 'name'])

    # Create index on user_id
    op.create_index('idx_tags_user_id', 'tags', ['user_id'])

    # Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', UUID(as_uuid=True), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )

    # Create index on tag_id for reverse lookups
    op.create_index('idx_task_tags_tag_id', 'task_tags', ['tag_id'])


def downgrade():
    op.drop_index('idx_task_tags_tag_id', table_name='task_tags')
    op.drop_table('task_tags')
    op.drop_index('idx_tags_user_id', table_name='tags')
    op.drop_constraint('uq_tags_user_name', 'tags', type_='unique')
    op.drop_table('tags')
