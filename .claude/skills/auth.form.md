---
description: React form components for Better Auth authentication
---

## Better Auth: React Form Components

This skill provides ready-to-use React form components for authentication with Better Auth.

### Prerequisites

- Better Auth client configured (`@/lib/auth-client`)
- React 18+ with hooks support
- Next.js 13+ (App Router)
- Tailwind CSS (optional, for styling)

### Sign In Form Component

```tsx
// components/auth/sign-in-form.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface SignInFormProps {
  redirectTo?: string;
}

export function SignInForm({ redirectTo = "/dashboard" }: SignInFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const { error } = await authClient.signIn.email({
      email,
      password,
    });

    setLoading(false);

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
      return;
    }

    router.push(redirectTo);
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-2xl font-bold text-center">Sign In</h2>

        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>

        {error && (
          <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign In"}
        </button>

        <div className="text-center text-sm space-y-2">
          <p>
            <Link href="/forgot-password" className="text-blue-600 hover:underline">
              Forgot your password?
            </Link>
          </p>
          <p>
            Don't have an account?{" "}
            <Link href="/signup" className="text-blue-600 hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </form>
    </div>
  );
}
```

### Sign Up Form Component

```tsx
// components/auth/sign-up-form.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface SignUpFormProps {
  redirectTo?: string;
  requireEmailVerification?: boolean;
}

export function SignUpForm({
  redirectTo = "/dashboard",
  requireEmailVerification = true,
}: SignUpFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const validateForm = (): string | null => {
    if (password !== confirmPassword) {
      return "Passwords do not match";
    }
    if (password.length < 8) {
      return "Password must be at least 8 characters";
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    const { data, error } = await authClient.signUp.email({
      email,
      password,
      name,
    });

    setLoading(false);

    if (error) {
      switch (error.status) {
        case 409:
          setError("An account with this email already exists");
          break;
        case 422:
          setError("Please check your email and password requirements");
          break;
        default:
          setError("Sign up failed. Please try again.");
      }
      return;
    }

    if (requireEmailVerification) {
      router.push("/verify-email?email=" + encodeURIComponent(email));
    } else {
      router.push(redirectTo);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-2xl font-bold text-center">Create Account</h2>

        <div className="space-y-2">
          <label htmlFor="name" className="block text-sm font-medium">
            Name
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="John Doe"
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
            minLength={8}
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="confirmPassword" className="block text-sm font-medium">
            Confirm Password
          </label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm your password"
            minLength={8}
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>

        {error && (
          <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Sign Up"}
        </button>

        <p className="text-center text-sm">
          Already have an account?{" "}
          <Link href="/login" className="text-blue-600 hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  );
}
```

### Forgot Password Form

```tsx
// components/auth/forgot-password-form.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import Link from "next/link";

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await authClient.forgetPassword({
        email,
        redirectTo: "/reset-password",
      });
      setSuccess(true);
    } catch (err) {
      setError("Failed to send reset email. Please try again.");
    }

    setLoading(false);
  };

  if (success) {
    return (
      <div className="w-full max-w-md mx-auto text-center space-y-4">
        <div className="p-4 bg-green-50 rounded-md">
          <h3 className="text-lg font-medium text-green-800">Check your email</h3>
          <p className="mt-2 text-sm text-green-700">
            We've sent a password reset link to <strong>{email}</strong>
          </p>
        </div>
        <Link href="/login" className="text-blue-600 hover:underline text-sm">
          Back to sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-2xl font-bold text-center">Forgot Password</h2>
        <p className="text-center text-gray-600 text-sm">
          Enter your email and we'll send you a reset link.
        </p>

        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>

        {error && (
          <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Sending..." : "Send Reset Link"}
        </button>

        <p className="text-center text-sm">
          <Link href="/login" className="text-blue-600 hover:underline">
            Back to sign in
          </Link>
        </p>
      </form>
    </div>
  );
}
```

### Reset Password Form

```tsx
// components/auth/reset-password-form.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

export function ResetPasswordForm() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  if (!token) {
    return (
      <div className="w-full max-w-md mx-auto text-center space-y-4">
        <div className="p-4 bg-red-50 rounded-md">
          <h3 className="text-lg font-medium text-red-800">Invalid Link</h3>
          <p className="mt-2 text-sm text-red-700">
            This password reset link is invalid or has expired.
          </p>
        </div>
        <Link href="/forgot-password" className="text-blue-600 hover:underline">
          Request a new reset link
        </Link>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      await authClient.resetPassword({
        newPassword: password,
        token,
      });
      setSuccess(true);
      setTimeout(() => router.push("/login"), 2000);
    } catch (err) {
      setError("Failed to reset password. The link may have expired.");
    }

    setLoading(false);
  };

  if (success) {
    return (
      <div className="w-full max-w-md mx-auto text-center space-y-4">
        <div className="p-4 bg-green-50 rounded-md">
          <h3 className="text-lg font-medium text-green-800">Password Reset!</h3>
          <p className="mt-2 text-sm text-green-700">
            Your password has been reset. Redirecting to login...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-2xl font-bold text-center">Set New Password</h2>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium">
            New Password
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
            minLength={8}
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="confirmPassword" className="block text-sm font-medium">
            Confirm New Password
          </label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm your new password"
            minLength={8}
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>

        {error && (
          <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Resetting..." : "Reset Password"}
        </button>
      </form>
    </div>
  );
}
```

### Auth Card Wrapper

```tsx
// components/auth/auth-card.tsx
interface AuthCardProps {
  children: React.ReactNode;
  title?: string;
}

export function AuthCard({ children, title }: AuthCardProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white shadow-lg rounded-lg p-8">
          {title && (
            <h1 className="text-2xl font-bold text-center mb-6">{title}</h1>
          )}
          {children}
        </div>
      </div>
    </div>
  );
}
```

### Usage in Pages

```tsx
// app/(auth)/login/page.tsx
import { SignInForm } from "@/components/auth/sign-in-form";
import { AuthCard } from "@/components/auth/auth-card";

export default function LoginPage() {
  return (
    <AuthCard>
      <SignInForm redirectTo="/dashboard" />
    </AuthCard>
  );
}

// app/(auth)/signup/page.tsx
import { SignUpForm } from "@/components/auth/sign-up-form";
import { AuthCard } from "@/components/auth/auth-card";

export default function SignUpPage() {
  return (
    <AuthCard>
      <SignUpForm requireEmailVerification={true} />
    </AuthCard>
  );
}

// app/(auth)/forgot-password/page.tsx
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";
import { AuthCard } from "@/components/auth/auth-card";

export default function ForgotPasswordPage() {
  return (
    <AuthCard>
      <ForgotPasswordForm />
    </AuthCard>
  );
}

// app/(auth)/reset-password/page.tsx
import { ResetPasswordForm } from "@/components/auth/reset-password-form";
import { AuthCard } from "@/components/auth/auth-card";

export default function ResetPasswordPage() {
  return (
    <AuthCard>
      <ResetPasswordForm />
    </AuthCard>
  );
}
```

### Usage

```
/auth.form [componentName]
```

**User Input**: $ARGUMENTS

Available components:
- `SignInForm` - Email/password sign in
- `SignUpForm` - User registration
- `ForgotPasswordForm` - Request password reset
- `ResetPasswordForm` - Set new password
- `AuthCard` - Wrapper component
