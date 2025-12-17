---
description: React hooks for Better Auth authentication
---

## Better Auth: React Hooks

This skill provides comprehensive React hooks for authentication with Better Auth.

### Prerequisites

- Better Auth client configured (`@/lib/auth-client`)
- React 18+ with hooks support
- Next.js 13+ (for App Router examples)

### Core Authentication Hook

```typescript
// hooks/useAuth.ts
import { authClient } from "@/lib/auth-client";
import { useState, useEffect, useCallback } from "react";

interface User {
  id: string;
  email: string;
  name: string | null;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
}

interface Session {
  user: User;
  session: {
    id: string;
    userId: string;
    expiresAt: Date;
  };
}

interface AuthState {
  user: User | null;
  session: Session | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    session: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  // Fetch session on mount
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const { data } = await authClient.getSession();
        setState({
          user: data?.user ?? null,
          session: data ?? null,
          isAuthenticated: !!data?.user,
          isLoading: false,
          error: null,
        });
      } catch (err) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: "Failed to fetch session",
        }));
      }
    };

    fetchSession();
  }, []);

  const refresh = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true }));
    try {
      const { data } = await authClient.getSession();
      setState({
        user: data?.user ?? null,
        session: data ?? null,
        isAuthenticated: !!data?.user,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to refresh session",
      }));
    }
  }, []);

  return { ...state, refresh };
}
```

### Sign In Hook

```typescript
// hooks/useSignIn.ts
import { authClient } from "@/lib/auth-client";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";

interface SignInOptions {
  redirectTo?: string;
  rememberMe?: boolean;
}

export function useSignIn() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const signIn = useCallback(
    async (email: string, password: string, options: SignInOptions = {}) => {
      setLoading(true);
      setError(null);

      const { data, error: authError } = await authClient.signIn.email({
        email,
        password,
        rememberMe: options.rememberMe,
      });

      setLoading(false);

      if (authError) {
        const errorMessage = getErrorMessage(authError.status);
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }

      if (options.redirectTo) {
        router.push(options.redirectTo);
      }

      return { success: true, user: data?.user };
    },
    [router]
  );

  const clearError = useCallback(() => setError(null), []);

  return { signIn, loading, error, clearError };
}

function getErrorMessage(status?: number): string {
  switch (status) {
    case 401:
      return "Invalid email or password";
    case 403:
      return "Please verify your email first";
    case 429:
      return "Too many attempts. Please try again later.";
    default:
      return "Something went wrong. Please try again.";
  }
}
```

### Sign Up Hook

```typescript
// hooks/useSignUp.ts
import { authClient } from "@/lib/auth-client";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";

interface SignUpData {
  email: string;
  password: string;
  name?: string;
}

interface SignUpOptions {
  redirectTo?: string;
  requireVerification?: boolean;
}

export function useSignUp() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const signUp = useCallback(
    async (data: SignUpData, options: SignUpOptions = {}) => {
      setLoading(true);
      setError(null);

      const { data: response, error: authError } = await authClient.signUp.email({
        email: data.email,
        password: data.password,
        name: data.name,
      });

      setLoading(false);

      if (authError) {
        const errorMessage = getSignUpErrorMessage(authError.status);
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }

      if (options.redirectTo) {
        router.push(options.redirectTo);
      }

      return {
        success: true,
        user: response?.user,
        requiresVerification: options.requireVerification,
      };
    },
    [router]
  );

  const clearError = useCallback(() => setError(null), []);

  return { signUp, loading, error, clearError };
}

function getSignUpErrorMessage(status?: number): string {
  switch (status) {
    case 409:
      return "An account with this email already exists";
    case 422:
      return "Please check your email and password requirements";
    default:
      return "Sign up failed. Please try again.";
  }
}
```

### Sign Out Hook

```typescript
// hooks/useSignOut.ts
import { authClient } from "@/lib/auth-client";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";

interface SignOutOptions {
  redirectTo?: string;
}

export function useSignOut() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const signOut = useCallback(
    async (options: SignOutOptions = { redirectTo: "/" }) => {
      setLoading(true);

      await authClient.signOut({
        fetchOptions: {
          onSuccess: () => {
            if (options.redirectTo) {
              router.push(options.redirectTo);
            }
          },
        },
      });

      setLoading(false);
    },
    [router]
  );

  return { signOut, loading };
}
```

### Combined Auth Actions Hook

```typescript
// hooks/useAuthActions.ts
import { authClient } from "@/lib/auth-client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export function useAuthActions() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    setError(null);

    const { error } = await authClient.signIn.email({ email, password });

    setLoading(false);

    if (error) {
      setError(error.message);
      return false;
    }

    router.push("/dashboard");
    return true;
  };

  const signUp = async (email: string, password: string, name?: string) => {
    setLoading(true);
    setError(null);

    const { error } = await authClient.signUp.email({ email, password, name });

    setLoading(false);

    if (error) {
      setError(error.message);
      return false;
    }

    router.push("/verify-email");
    return true;
  };

  const signOut = async () => {
    setLoading(true);
    await authClient.signOut();
    setLoading(false);
    router.push("/");
  };

  const forgotPassword = async (email: string) => {
    setLoading(true);
    setError(null);

    try {
      await authClient.forgetPassword({
        email,
        redirectTo: "/reset-password",
      });
      setLoading(false);
      return true;
    } catch (err) {
      setError("Failed to send reset email");
      setLoading(false);
      return false;
    }
  };

  const resetPassword = async (token: string, newPassword: string) => {
    setLoading(true);
    setError(null);

    try {
      await authClient.resetPassword({ token, newPassword });
      setLoading(false);
      router.push("/login");
      return true;
    } catch (err) {
      setError("Failed to reset password");
      setLoading(false);
      return false;
    }
  };

  return {
    signIn,
    signUp,
    signOut,
    forgotPassword,
    resetPassword,
    loading,
    error,
    clearError: () => setError(null),
  };
}
```

### Session Provider (React Context)

```typescript
// providers/auth-provider.tsx
"use client";

import { createContext, useContext, ReactNode } from "react";
import { useAuth } from "@/hooks/useAuth";

interface AuthContextType {
  user: any;
  session: any;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const auth = useAuth();

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
}
```

### Usage in Layout

```tsx
// app/layout.tsx
import { AuthProvider } from "@/providers/auth-provider";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
```

### Protected Route Hook

```typescript
// hooks/useRequireAuth.ts
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/providers/auth-provider";

export function useRequireAuth(redirectTo: string = "/login") {
  const { isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, redirectTo, router]);

  return { isAuthenticated, isLoading };
}
```

### Usage Example

```tsx
// app/dashboard/page.tsx
"use client";

import { useAuthContext } from "@/providers/auth-provider";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useSignOut } from "@/hooks/useSignOut";

export default function DashboardPage() {
  const { isLoading } = useRequireAuth();
  const { user } = useAuthContext();
  const { signOut, loading: signingOut } = useSignOut();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Welcome, {user?.name || user?.email}!</h1>
      <button onClick={() => signOut()} disabled={signingOut}>
        {signingOut ? "Signing out..." : "Sign Out"}
      </button>
    </div>
  );
}
```

### Usage

```
/auth.hook [hookName]
```

**User Input**: $ARGUMENTS

Available hooks:
- `useAuth` - Core authentication state
- `useSignIn` - Sign in functionality
- `useSignUp` - Sign up functionality
- `useSignOut` - Sign out functionality
- `useAuthActions` - Combined auth actions
- `useRequireAuth` - Protected route hook
