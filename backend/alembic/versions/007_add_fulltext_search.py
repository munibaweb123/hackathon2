"""Add full-text search trigger on tasks.search_vector

Revision ID: 007
Revises: 006
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Add search_vector column
    op.add_column('tasks', sa.Column('search_vector', TSVECTOR(), nullable=True))

    # Create GIN index for full-text search
    op.create_index(
        'idx_tasks_search',
        'tasks',
        ['search_vector'],
        postgresql_using='gin'
    )

    # Create trigger function for automatic search_vector updates
    op.execute("""
        CREATE OR REPLACE FUNCTION tasks_search_trigger() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.description, ''));
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on tasks table
    op.execute("""
        CREATE TRIGGER tasks_search_update
        BEFORE INSERT OR UPDATE ON tasks
        FOR EACH ROW EXECUTE FUNCTION tasks_search_trigger();
    """)

    # Update existing rows to populate search_vector
    op.execute("""
        UPDATE tasks
        SET search_vector = to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''));
    """)


def downgrade():
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS tasks_search_update ON tasks;")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS tasks_search_trigger();")

    # Drop index
    op.drop_index('idx_tasks_search', table_name='tasks')

    # Remove column
    op.drop_column('tasks', 'search_vector')
