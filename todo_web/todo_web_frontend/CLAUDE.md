# Todo Web Frontend

This is the Next.js frontend for the Todo Web Application.

## Technology Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: ShadCN UI
- **Authentication**: Better Auth with JWT Tokens
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form + Zod
- **Notifications**: Sonner

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Auth pages (login, register)
│   ├── (dashboard)/       # Protected dashboard pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   └── globals.css        # Global styles
├── components/
│   ├── auth/              # Authentication components
│   ├── layout/            # Layout components (header)
│   ├── tasks/             # Task management components
│   └── ui/                # ShadCN UI components
├── hooks/
│   ├── use-auth.ts        # Authentication hook
│   └── use-tasks.ts       # Tasks CRUD hook
├── lib/
│   ├── api-client.ts      # Axios API client with JWT
│   ├── auth.ts            # Better Auth server config
│   ├── auth-client.ts     # Better Auth client
│   └── utils.ts           # Utility functions
└── types/
    └── index.ts           # TypeScript types
```

## API Integration

The frontend integrates with a FastAPI backend. All API requests include JWT tokens in the `Authorization: Bearer <token>` header.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/{user_id}/tasks | List all tasks |
| POST | /api/{user_id}/tasks | Create a new task |
| GET | /api/{user_id}/tasks/{id} | Get task details |
| PUT | /api/{user_id}/tasks/{id} | Update a task |
| DELETE | /api/{user_id}/tasks/{id} | Delete a task |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion |

## Development Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

## Environment Variables

Create a `.env.local` file with:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

Generate a secret with: `openssl rand -base64 32`

## Key Components

- **TaskList**: Displays all tasks with loading/empty states
- **TaskItem**: Individual task with toggle, edit, delete
- **TaskForm**: Create/edit task dialog
- **TaskFilters**: Filter by status, sort by various fields
- **LoginForm/RegisterForm**: Authentication forms

## Authentication Flow

1. User registers/logs in via Better Auth
2. JWT token is stored and sent with all API requests
3. Protected routes redirect to login if not authenticated
4. Token refresh is handled automatically
