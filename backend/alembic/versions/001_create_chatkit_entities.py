"""Create ChatKit entities: threads, chatkit_messages, widgets, actions

Revision ID: 001_create_chatkit_entities
Revises:
Create Date: 2026-01-02 09:52:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel
from uuid import UUID

# revision identifiers, used by Alembic.
revision: str = '001_create_chatkit_entities'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create threads table
    op.create_table('threads',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_threads_user_id'), 'threads', ['user_id'], unique=False)

    # Create chatkit_messages table
    op.create_table('chatkit_messages',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('thread_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(length=10000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chatkit_messages_thread_id'), 'chatkit_messages', ['thread_id'], unique=False)

    # Create widgets table
    op.create_table('widgets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('message_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('action_handler', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_widgets_message_id'), 'widgets', ['message_id'], unique=False)

    # Create actions table
    op.create_table('actions',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('widget_id', sa.String(), nullable=True),
        sa.Column('thread_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('result', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_actions_thread_id'), 'actions', ['thread_id'], unique=False)
    op.create_index(op.f('ix_actions_widget_id'), 'actions', ['widget_id'], unique=False)

    # Add chatkit-specific columns to users table
    op.add_column('users', sa.Column('chat_preferences', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('last_chat_thread_id', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove chatkit-specific columns from users table
    op.drop_column('users', 'last_chat_thread_id')
    op.drop_column('users', 'chat_preferences')

    # Drop actions table
    op.drop_index(op.f('ix_actions_widget_id'), table_name='actions')
    op.drop_index(op.f('ix_actions_thread_id'), table_name='actions')
    op.drop_table('actions')

    # Drop widgets table
    op.drop_index(op.f('ix_widgets_message_id'), table_name='widgets')
    op.drop_table('widgets')

    # Drop chatkit_messages table
    op.drop_index(op.f('ix_chatkit_messages_thread_id'), table_name='chatkit_messages')
    op.drop_table('chatkit_messages')

    # Drop threads table
    op.drop_index(op.f('ix_threads_user_id'), table_name='threads')
    op.drop_table('threads')