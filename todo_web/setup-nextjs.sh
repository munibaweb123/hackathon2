#!/bin/bash

# Setup script for Next.js Todo Web Frontend
# This script will create a complete Next.js project with TypeScript, Tailwind, and ShadCN

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/mnt/c/Users/YOusuf Traders/Documents/quarter-4/hackathon_2/todo_web/todo_web_frontend"
PROJECT_NAME="todo-web-frontend"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Next.js Todo Frontend Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if directory already exists
if [ -d "$PROJECT_DIR" ]; then
  echo -e "${YELLOW}Warning: Directory $PROJECT_DIR already exists${NC}"
  read -p "Do you want to remove it and continue? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$PROJECT_DIR"
    echo -e "${GREEN}Removed existing directory${NC}"
  else
    echo -e "${RED}Setup cancelled${NC}"
    exit 1
  fi
fi

# Create parent directory if it doesn't exist
mkdir -p "/mnt/c/Users/YOusuf Traders/Documents/quarter-4/hackathon_2/todo_web"

# Step 1: Create Next.js app with TypeScript and Tailwind
echo -e "${GREEN}[1/8] Creating Next.js app with create-next-app...${NC}"
cd "/mnt/c/Users/YOusuf Traders/Documents/quarter-4/hackathon_2/todo_web"
npx create-next-app@latest "$PROJECT_NAME" \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*" \
  --use-npm \
  --no-git

cd "$PROJECT_DIR"
echo -e "${GREEN}Next.js app created successfully${NC}"
echo ""

# Step 2: Install dependencies
echo -e "${GREEN}[2/8] Installing dependencies...${NC}"
npm install \
  better-auth \
  axios \
  date-fns \
  clsx \
  tailwind-merge \
  class-variance-authority \
  lucide-react \
  @radix-ui/react-checkbox \
  @radix-ui/react-label \
  @radix-ui/react-select \
  @radix-ui/react-slot \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  zod \
  next-themes

echo -e "${GREEN}Dependencies installed${NC}"
echo ""

# Step 3: Install dev dependencies
echo -e "${GREEN}[3/8] Installing dev dependencies...${NC}"
npm install -D \
  vitest \
  @vitejs/plugin-react \
  @testing-library/react \
  @testing-library/jest-dom \
  jsdom \
  tailwindcss-animate

echo -e "${GREEN}Dev dependencies installed${NC}"
echo ""

# Step 4: Initialize ShadCN UI
echo -e "${GREEN}[4/8] Initializing ShadCN UI...${NC}"

# Create components.json
cat > components.json << 'EOF'
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
EOF

# Install ShadCN components
npx shadcn@latest add button card input label checkbox select -y || echo -e "${YELLOW}Note: Manual ShadCN setup may be required${NC}"

echo -e "${GREEN}ShadCN UI initialized${NC}"
echo ""

# Step 5: Create folder structure
echo -e "${GREEN}[5/8] Creating folder structure...${NC}"

mkdir -p app/api/auth/[...auth]
mkdir -p app/dashboard
mkdir -p app/login
mkdir -p app/signup
mkdir -p components/ui
mkdir -p components/auth
mkdir -p components/todo
mkdir -p components/layout
mkdir -p components/providers
mkdir -p lib
mkdir -p hooks
mkdir -p tests/components
mkdir -p public

echo -e "${GREEN}Folder structure created${NC}"
echo ""

# Step 6: Create core files
echo -e "${GREEN}[6/8] Creating core application files...${NC}"

# Create lib/utils.ts
cat > lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF

# Create lib/types.ts
cat > lib/types.ts << 'EOF'
export interface Todo {
  id: string
  title: string
  description?: string
  status: 'pending' | 'completed'
  priority: 'low' | 'medium' | 'high'
  dueDate?: string
  category?: string
  tags?: string[]
  recurrence?: {
    frequency: 'daily' | 'weekly' | 'monthly'
    interval: number
  }
  reminder?: string
  createdAt: string
  updatedAt: string
}

export interface User {
  id: string
  email: string
  name?: string
  createdAt: string
}

export interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

export interface TodoFilters {
  status?: 'all' | 'pending' | 'completed'
  priority?: 'low' | 'medium' | 'high'
  category?: string
  search?: string
}
EOF

# Create lib/api-client.ts
cat > lib/api-client.ts << 'EOF'
import axios from 'axios'
import type { Todo, User } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const todoApi = {
  getAll: async (filters?: Record<string, any>) => {
    const { data } = await apiClient.get<Todo[]>('/todos', { params: filters })
    return data
  },
  getById: async (id: string) => {
    const { data } = await apiClient.get<Todo>(`/todos/${id}`)
    return data
  },
  create: async (todo: Partial<Todo>) => {
    const { data } = await apiClient.post<Todo>('/todos', todo)
    return data
  },
  update: async (id: string, todo: Partial<Todo>) => {
    const { data } = await apiClient.put<Todo>(`/todos/${id}`, todo)
    return data
  },
  delete: async (id: string) => {
    await apiClient.delete(`/todos/${id}`)
  },
}

export const authApi = {
  me: async () => {
    const { data } = await apiClient.get<User>('/auth/me')
    return data
  },
}
EOF

# Create providers
cat > components/providers/auth-provider.tsx << 'EOF'
'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { authApi } from '@/lib/api-client'
import type { User, AuthState } from '@/lib/types'

const AuthContext = createContext<AuthState & {
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name?: string) => Promise<void>
  logout: () => Promise<void>
}>(
  {
    user: null,
    isLoading: true,
    isAuthenticated: false,
    login: async () => {},
    signup: async () => {},
    logout: async () => {},
  }
)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    authApi.me()
      .then((userData) => setUser(userData))
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false))
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const userData = await authApi.me()
      setUser(userData)
    } finally {
      setIsLoading(false)
    }
  }

  const signup = async (email: string, password: string, name?: string) => {
    setIsLoading(true)
    try {
      const userData = await authApi.me()
      setUser(userData)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
EOF

cat > components/providers/theme-provider.tsx << 'EOF'
'use client'

import * as React from 'react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'
import { type ThemeProviderProps } from 'next-themes/dist/types'

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
EOF

# Update app/layout.tsx
cat > app/layout.tsx << 'EOF'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/components/providers/auth-provider'
import { ThemeProvider } from '@/components/providers/theme-provider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Todo App - Manage Your Tasks',
  description: 'A powerful todo application with advanced features',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
EOF

# Update app/page.tsx
cat > app/page.tsx << 'EOF'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-2xl text-center space-y-6">
        <h1 className="text-6xl font-bold tracking-tight">
          Todo App
        </h1>
        <p className="text-xl text-muted-foreground">
          Manage your tasks efficiently with advanced features like recurring tasks, reminders, and priority levels.
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <Link href="/login">
            <Button size="lg">Login</Button>
          </Link>
          <Link href="/signup">
            <Button size="lg" variant="outline">Sign Up</Button>
          </Link>
        </div>
      </div>
    </main>
  )
}
EOF

# Create vitest.config.ts
cat > vitest.config.ts << 'EOF'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    globals: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
})
EOF

# Create tests/setup.ts
cat > tests/setup.ts << 'EOF'
import '@testing-library/jest-dom'
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
})
EOF

echo -e "${GREEN}Core files created${NC}"
echo ""

# Step 7: Create environment files
echo -e "${GREEN}[7/8] Creating environment files...${NC}"

cat > .env.example << 'EOF'
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-generate-with-openssl-rand-base64-32
BETTER_AUTH_URL=http://localhost:3000

# Optional: Production Configuration
# NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
# BETTER_AUTH_URL=https://yourdomain.com
EOF

cp .env.example .env.local

echo -e "${GREEN}Environment files created${NC}"
echo ""

# Step 8: Update package.json scripts
echo -e "${GREEN}[8/8] Updating package.json scripts...${NC}"

npm pkg set scripts.test="vitest"
npm pkg set scripts.test:ui="vitest --ui"
npm pkg set scripts.test:coverage="vitest --coverage"

echo -e "${GREEN}Package.json updated${NC}"
echo ""

# Final steps
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Navigate to the project:"
echo -e "   ${GREEN}cd \"$PROJECT_DIR\"${NC}"
echo ""
echo "2. Update environment variables in .env.local"
echo ""
echo "3. Start the development server:"
echo -e "   ${GREEN}npm run dev${NC}"
echo ""
echo "4. Open your browser at: http://localhost:3000"
echo ""
echo -e "${YELLOW}TODO: Manual configuration required${NC}"
echo ""
echo "- Configure Better Auth by following: https://better-auth.com/docs"
echo "- Update BETTER_AUTH_SECRET in .env.local (generate with: openssl rand -base64 32)"
echo "- Create login and signup pages in app/login and app/signup"
echo "- Implement todo components in components/todo/"
echo "- Add authentication middleware for protected routes"
echo "- Connect to your backend API"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
