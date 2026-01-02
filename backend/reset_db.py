#!/usr/bin/env python3
"""Script to reset database schema by dropping and recreating all tables."""

from app.core.database import drop_all_tables, create_db_and_tables

def reset_database():
    print("Dropping all database tables...")
    drop_all_tables()
    print("All tables dropped successfully.")

    print("Creating new database tables...")
    create_db_and_tables()
    print("All tables created successfully with updated schema.")

    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()