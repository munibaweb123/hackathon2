# Frontend Development Guidelines

This is the Next.js 14 frontend for the hackathon-todo application.

## Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (optional)
- **Authentication**: Better Auth
- **State Management**: React hooks / Zustand (if needed)

## Project Structure

```
frontend/
├── src/
│   ├── app/             # App Router pages
│   ├── components/      # UI components (auth, tasks, layout, etc.)
│   ├── hooks/           # Custom hooks (use-auth, use-tasks)
│   ├── lib/             # Utilities (auth-client, api-client)
│   ├── services/        # Service layer
│   └── types/           # TypeScript types
├── public/              # Static assets
├── .env.local           # Environment variables
├── .env.example         # Environment variables template
├── package.json         # Node.js dependencies
├── tsconfig.json        # TypeScript configuration
├── next.config.ts       # Next.js configuration
├── postcss.config.mjs   # PostCSS configuration
├── components.json      # Component library configuration
└── CLAUDE.md           # This file
```

## Code Standards

### Components

- Use functional components with TypeScript
- Keep components small and focused
- Use proper prop typing with interfaces
- Follow naming conventions: PascalCase for components

```tsx
interface TaskCardProps {
  task: Task;
  onComplete?: (id: string) => void;
}

export function TaskCard({ task, onComplete }: TaskCardProps) {
  // Component implementation
}
```

### API Integration

- Use the API client in `lib/api.ts` for all backend calls
- Handle loading and error states consistently
- Use React Query or SWR for data fetching (optional)

```tsx
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchTasks(): Promise<Task[]> {
  const response = await fetch(`${API_BASE}/api/tasks`);
  if (!response.ok) throw new Error('Failed to fetch tasks');
  return response.json();
}
```

### Styling

- Use Tailwind CSS utility classes
- Create custom components for repeated patterns
- Use CSS variables for theming
- Keep responsive design in mind

### Authentication

- Use Better Auth for session management
- Protect routes with middleware
- Store tokens securely (httpOnly cookies preferred)

## Running the Frontend

```bash
# Development
cd frontend && npm install && npm run dev

# Build
cd frontend && npm run build

# Production
cd frontend && npm start

# With Docker
docker-compose up
```

## Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
```

## References

- UI Specs: `@specs/ui/`
- API Contract: `@specs/api/rest-endpoints.md`
- Task Features: `@specs/features/task-crud.md`
