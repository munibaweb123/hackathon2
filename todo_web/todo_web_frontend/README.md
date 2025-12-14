# Todo Web Frontend

A modern, multi-user todo application built with Next.js 16+, TypeScript, and Tailwind CSS.

## Features

- User authentication (login, register) with Better Auth
- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Filter tasks by status (all, pending, completed)
- Sort tasks by date, priority, or title
- Responsive design for mobile and desktop
- Real-time toast notifications

## Tech Stack

- **Next.js 16+** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **ShadCN UI** - UI components
- **Better Auth** - Authentication
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Sonner** - Toast notifications

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Running FastAPI backend on port 8000

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create `.env.local` from `.env.example`:

```bash
cp .env.example .env.local
```

3. Update environment variables:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<generate-with-openssl-rand-base64-32>
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

4. Run the development server:

```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/                    # Pages and layouts
├── components/             # React components
│   ├── auth/              # Auth forms
│   ├── layout/            # Layout components
│   ├── tasks/             # Task components
│   └── ui/                # ShadCN components
├── hooks/                  # Custom React hooks
├── lib/                    # Utilities and config
└── types/                  # TypeScript types
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## API Integration

The frontend expects a FastAPI backend running on the configured `NEXT_PUBLIC_API_URL`. All task operations require authentication via JWT tokens.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/{user_id}/tasks | List all tasks |
| POST | /api/{user_id}/tasks | Create a new task |
| GET | /api/{user_id}/tasks/{id} | Get task details |
| PUT | /api/{user_id}/tasks/{id} | Update a task |
| DELETE | /api/{user_id}/tasks/{id} | Delete a task |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion |

## Learn More

To learn more about the technologies used:

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [ShadCN UI](https://ui.shadcn.com)
- [Better Auth](https://better-auth.com)

## License

MIT
