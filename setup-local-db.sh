#!/bin/bash
# Script to set up local PostgreSQL for development

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install PostgreSQL first."
    echo "On Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "On macOS with Homebrew: brew install postgresql"
    echo "On Windows: Download from https://www.postgresql.org/download/"
    exit 1
fi

# Create the database for the application
echo "Setting up local database for development..."

# Switch to postgres user and create database/user
sudo -u postgres psql << EOF
CREATE USER hackathon_user WITH PASSWORD 'hackathon_pass';
CREATE DATABASE hackathon_todo WITH OWNER hackathon_user;
GRANT ALL PRIVILEGES ON DATABASE hackathon_todo TO hackathon_user;
\q
EOF

echo "Local database setup complete!"
echo "Update your frontend/.env.local to use:"
echo "DATABASE_URL=postgresql://hackathon_user:hackathon_pass@localhost:5432/hackathon_todo"