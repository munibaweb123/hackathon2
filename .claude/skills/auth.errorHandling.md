---
description: Error handling patterns for Better Auth authentication
---

## Better Auth: Error Handling

This skill provides comprehensive error handling patterns for Better Auth authentication flows.

### Error Response Structure

Better Auth returns errors in a consistent format:

```typescript
interface AuthError {
  status: number;
  message: string;
  code?: string;
}
```

### Common Error Status Codes

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Bad Request | Invalid request format or missing fields |
| 401 | Unauthorized | Invalid credentials or expired token |
| 403 | Forbidden | Email not verified or account disabled |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (e.g., duplicate email) |
| 422 | Validation Error | Input doesn't meet requirements |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Internal server error |

### Basic Error Handling

```typescript
const { data, error } = await authClient.signIn.email({
  email,
  password,
});

if (error) {
  switch (error.status) {
    case 401:
      setError("Invalid email or password");
      break;
    case 403:
      setError("Please verify your email first");
      break;
    case 429:
      setError("Too many attempts. Please try again later.");
      break;
    default:
      setError("Something went wrong");
  }
}
```

### Comprehensive Error Handler Utility

```typescript
// utils/auth-errors.ts

export type AuthErrorCode =
  | "INVALID_CREDENTIALS"
  | "EMAIL_NOT_VERIFIED"
  | "ACCOUNT_DISABLED"
  | "EMAIL_EXISTS"
  | "INVALID_TOKEN"
  | "TOKEN_EXPIRED"
  | "RATE_LIMITED"
  | "VALIDATION_ERROR"
  | "SERVER_ERROR"
  | "NETWORK_ERROR"
  | "UNKNOWN_ERROR";

interface AuthErrorInfo {
  code: AuthErrorCode;
  message: string;
  userMessage: string;
  action?: string;
}

export function getAuthError(status?: number, message?: string): AuthErrorInfo {
  const errorMap: Record<number, AuthErrorInfo> = {
    400: {
      code: "VALIDATION_ERROR",
      message: message || "Invalid request",
      userMessage: "Please check your input and try again.",
      action: "Fix the input errors",
    },
    401: {
      code: "INVALID_CREDENTIALS",
      message: message || "Invalid credentials",
      userMessage: "The email or password you entered is incorrect.",
      action: "Check your credentials or reset your password",
    },
    403: {
      code: "EMAIL_NOT_VERIFIED",
      message: message || "Email not verified",
      userMessage: "Please verify your email address to continue.",
      action: "Check your email for verification link",
    },
    404: {
      code: "INVALID_TOKEN",
      message: message || "Resource not found",
      userMessage: "This link is invalid or has expired.",
      action: "Request a new link",
    },
    409: {
      code: "EMAIL_EXISTS",
      message: message || "Email already exists",
      userMessage: "An account with this email already exists.",
      action: "Sign in or use a different email",
    },
    422: {
      code: "VALIDATION_ERROR",
      message: message || "Validation failed",
      userMessage: "Please check your input meets the requirements.",
      action: "Review password and email requirements",
    },
    429: {
      code: "RATE_LIMITED",
      message: message || "Too many requests",
      userMessage: "Too many attempts. Please wait a moment.",
      action: "Wait before trying again",
    },
    500: {
      code: "SERVER_ERROR",
      message: message || "Server error",
      userMessage: "Something went wrong. Please try again later.",
      action: "Try again in a few moments",
    },
  };

  return (
    errorMap[status || 0] || {
      code: "UNKNOWN_ERROR",
      message: message || "Unknown error",
      userMessage: "An unexpected error occurred.",
      action: "Please try again",
    }
  );
}
```

### React Hook for Error Handling

```typescript
// hooks/useAuthError.ts
import { useState, useCallback } from "react";
import { getAuthError, AuthErrorInfo } from "@/utils/auth-errors";

export function useAuthError() {
  const [error, setError] = useState<AuthErrorInfo | null>(null);

  const handleError = useCallback((status?: number, message?: string) => {
    const errorInfo = getAuthError(status, message);
    setError(errorInfo);
    return errorInfo;
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    handleError,
    clearError,
    hasError: error !== null,
  };
}
```

### Error Display Component

```tsx
// components/auth/auth-error.tsx
import { AuthErrorInfo } from "@/utils/auth-errors";
import Link from "next/link";

interface AuthErrorProps {
  error: AuthErrorInfo | null;
  onDismiss?: () => void;
}

export function AuthError({ error, onDismiss }: AuthErrorProps) {
  if (!error) return null;

  const getActionLink = () => {
    switch (error.code) {
      case "INVALID_CREDENTIALS":
        return { href: "/forgot-password", text: "Reset password" };
      case "EMAIL_NOT_VERIFIED":
        return { href: "/resend-verification", text: "Resend verification" };
      case "EMAIL_EXISTS":
        return { href: "/login", text: "Sign in instead" };
      case "INVALID_TOKEN":
      case "TOKEN_EXPIRED":
        return { href: "/forgot-password", text: "Request new link" };
      default:
        return null;
    }
  };

  const actionLink = getActionLink();

  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-md">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-red-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm text-red-700">{error.userMessage}</p>
          {actionLink && (
            <p className="mt-2 text-sm">
              <Link
                href={actionLink.href}
                className="text-red-600 hover:text-red-500 underline"
              >
                {actionLink.text}
              </Link>
            </p>
          )}
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="ml-3 text-red-400 hover:text-red-500"
          >
            <span className="sr-only">Dismiss</span>
            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
```

### Form with Error Handling

```tsx
// components/auth/sign-in-with-errors.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useAuthError } from "@/hooks/useAuthError";
import { AuthError } from "@/components/auth/auth-error";

export function SignInWithErrors() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { error, handleError, clearError } = useAuthError();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLoading(true);

    const { error: authError } = await authClient.signIn.email({
      email,
      password,
    });

    setLoading(false);

    if (authError) {
      handleError(authError.status, authError.message);
      return;
    }

    router.push("/dashboard");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <AuthError error={error} onDismiss={clearError} />

      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? "Signing in..." : "Sign In"}
      </button>
    </form>
  );
}
```

### Try-Catch Wrapper

```typescript
// utils/safe-auth.ts
type AsyncAuthFunction<T> = () => Promise<{
  data?: T;
  error?: { status: number; message: string };
}>;

export async function safeAuth<T>(
  fn: AsyncAuthFunction<T>
): Promise<{ data: T | null; error: AuthErrorInfo | null }> {
  try {
    const result = await fn();

    if (result.error) {
      return {
        data: null,
        error: getAuthError(result.error.status, result.error.message),
      };
    }

    return { data: result.data ?? null, error: null };
  } catch (err) {
    // Network or unexpected errors
    return {
      data: null,
      error: {
        code: "NETWORK_ERROR",
        message: err instanceof Error ? err.message : "Network error",
        userMessage: "Unable to connect. Please check your internet connection.",
        action: "Check your connection and try again",
      },
    };
  }
}

// Usage
const { data, error } = await safeAuth(() =>
  authClient.signIn.email({ email, password })
);
```

### Toast Notifications for Errors

```typescript
// utils/auth-toast.ts
import { toast } from "sonner"; // or your preferred toast library
import { AuthErrorInfo } from "./auth-errors";

export function showAuthError(error: AuthErrorInfo) {
  toast.error(error.userMessage, {
    description: error.action,
    action: error.code === "EMAIL_NOT_VERIFIED"
      ? {
          label: "Resend",
          onClick: () => window.location.href = "/resend-verification",
        }
      : undefined,
  });
}

export function showAuthSuccess(message: string) {
  toast.success(message);
}
```

### Form Validation Errors

```typescript
// utils/validation.ts
interface ValidationError {
  field: string;
  message: string;
}

export function validateSignUpForm(data: {
  email: string;
  password: string;
  confirmPassword: string;
}): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!data.email) {
    errors.push({ field: "email", message: "Email is required" });
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push({ field: "email", message: "Invalid email format" });
  }

  if (!data.password) {
    errors.push({ field: "password", message: "Password is required" });
  } else if (data.password.length < 8) {
    errors.push({ field: "password", message: "Password must be at least 8 characters" });
  }

  if (data.password !== data.confirmPassword) {
    errors.push({ field: "confirmPassword", message: "Passwords do not match" });
  }

  return errors;
}
```

### Field-Level Error Display

```tsx
// components/form/field-error.tsx
interface FieldErrorProps {
  error?: string;
}

export function FieldError({ error }: FieldErrorProps) {
  if (!error) return null;

  return (
    <p className="mt-1 text-sm text-red-600" role="alert">
      {error}
    </p>
  );
}

// Usage
<div>
  <input type="email" {...props} />
  <FieldError error={errors.email} />
</div>
```

### Usage

```
/auth.errorHandling [pattern]
```

**User Input**: $ARGUMENTS

Available patterns:
- `basic` - Basic error handling
- `utility` - Error utility functions
- `hook` - React hook for errors
- `component` - Error display component
- `validation` - Form validation
- `toast` - Toast notifications
