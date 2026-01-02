# ChatKit Integration Setup Guide

This document provides instructions for setting up and using the ChatKit integration in the todo application.

## Overview

The ChatKit integration enables conversational task management through natural language commands. Users can interact with their tasks using commands like "Show me my tasks", "Add a task to buy groceries", or "Complete task 3".

## Backend Setup

### Prerequisites

- Python 3.13+
- FastAPI
- OpenAI Agents SDK
- Better Auth for authentication
- PostgreSQL (production) or SQLite (development)

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Required environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key for agent model access
   - `BETTER_AUTH_URL`: Better Auth service URL
   - `BETTER_AUTH_SECRET`: Better Auth secret key
   - `DATABASE_URL`: Database connection string

## Frontend Setup

### Prerequisites

- Node.js 20+
- Next.js 14
- TypeScript

### Installation

1. Install dependencies:
   ```bash
   cd frontend && npm install
   ```

2. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

## API Endpoints

### ChatKit Endpoints

- `POST /api/chatkit/respond` - Process user input and generate response
- `POST /api/chatkit/action` - Handle widget interactions (button clicks, etc.)

Both endpoints require authentication via JWT token in the Authorization header.

## Usage Examples

### Natural Language Commands

The ChatKit supports the following types of commands:

1. **View Tasks**: "Show me my tasks", "List my tasks", "What are my tasks?"
2. **Add Task**: "Add a task to buy groceries", "Create a task: finish report"
3. **Complete Task**: "Complete task 3", "Mark task 1 as done", "Finish task 5"
4. **Delete Task**: "Delete task 2", "Remove task 4"
5. **Update Task**: "Change task 1 title to 'new title'"

### Widget Interactions

Interactive widgets allow users to manage tasks without typing commands:
- Click "Complete" buttons to mark tasks as done
- Click "Delete" buttons to remove tasks
- Click task items to view details

## Development

### Running the Application

Backend:
```bash
cd backend && uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend && npm run dev
```

### Testing

Run the full test suite to ensure all functionality works:
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm run test
```

## Troubleshooting

### Common Issues

1. **Widget rendering fails**: Check that the ChatKit CDN is accessible
2. **Authentication errors**: Verify JWT tokens are properly configured
3. **Action processing fails**: Ensure action payloads follow the correct schema

### Logging

Enable DEBUG-level logging to troubleshoot issues:
- Set `LOG_LEVEL=DEBUG` in your environment variables
- Check application logs for detailed error information

## Security

- All ChatKit endpoints require valid JWT tokens from Better Auth
- Widget data is sanitized before rendering
- Action payloads are validated before processing
- Rate limiting is implemented to prevent abuse