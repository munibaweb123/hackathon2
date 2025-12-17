---
description: React form components for Magic Link authentication
---

## Better Auth: Magic Link Form Components

This skill provides ready-to-use React form components for Magic Link authentication.

### Prerequisites

- Magic Link client configured (`@/lib/auth-client`)
- React 18+
- Next.js 13+ (App Router)

### Basic Magic Link Form

```tsx
// components/auth/magic-link-form.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";

export function MagicLinkForm() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const { error } = await authClient.signIn.magicLink({
      email,
      callbackURL: "/dashboard",
    });

    setLoading(false);

    if (error) {
      setError(error.message);
      return;
    }

    setSent(true);
  };

  if (sent) {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold">Check your email</h2>
        <p className="text-gray-600">
          We sent a magic link to <strong>{email}</strong>
        </p>
        <p className="text-sm text-gray-500">
          Click the link in the email to sign in.
        </p>
        <button
          onClick={() => setSent(false)}
          className="text-blue-600 hover:underline text-sm"
        >
          Use a different email
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center">Sign in with Magic Link</h2>
      <p className="text-center text-gray-600 text-sm">
        We'll send you a link to sign in instantly.
      </p>

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email
        </label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? "Sending..." : "Send Magic Link"}
      </button>
    </form>
  );
}
```

### Magic Link Form with Rate Limiting

```tsx
// components/auth/magic-link-form-with-cooldown.tsx
"use client";

import { useState, useEffect } from "react";
import { authClient } from "@/lib/auth-client";

const COOLDOWN_SECONDS = 60;

export function MagicLinkFormWithCooldown() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (cooldown > 0) {
      setError(`Please wait ${cooldown} seconds before requesting again`);
      return;
    }

    setLoading(true);
    setError("");

    const { error } = await authClient.signIn.magicLink({
      email,
      callbackURL: "/dashboard",
    });

    setLoading(false);

    if (error) {
      if (error.status === 429) {
        setError("Too many requests. Please wait a moment.");
        setCooldown(COOLDOWN_SECONDS);
      } else {
        setError(error.message);
      }
      return;
    }

    setSent(true);
    setCooldown(COOLDOWN_SECONDS);
  };

  const handleResend = () => {
    if (cooldown === 0) {
      setSent(false);
    }
  };

  if (sent) {
    return (
      <div className="text-center space-y-4">
        <h2 className="text-xl font-semibold">Check your email</h2>
        <p className="text-gray-600">
          We sent a magic link to <strong>{email}</strong>
        </p>

        <div className="space-y-2">
          <button
            onClick={handleResend}
            disabled={cooldown > 0}
            className="text-blue-600 hover:underline text-sm disabled:text-gray-400 disabled:no-underline"
          >
            {cooldown > 0
              ? `Resend in ${cooldown}s`
              : "Didn't receive it? Resend"}
          </button>

          <p className="text-sm">
            <button
              onClick={() => {
                setSent(false);
                setEmail("");
              }}
              className="text-gray-500 hover:text-gray-700"
            >
              Use a different email
            </button>
          </p>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
        className="w-full px-3 py-2 border rounded-md"
      />

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={loading || cooldown > 0}
        className="w-full py-2 bg-blue-600 text-white rounded-md disabled:opacity-50"
      >
        {loading
          ? "Sending..."
          : cooldown > 0
          ? `Wait ${cooldown}s`
          : "Send Magic Link"}
      </button>
    </form>
  );
}
```

### Combined Auth Form (Password + Magic Link)

```tsx
// components/auth/combined-sign-in-form.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

type AuthMode = "password" | "magic-link";

export function CombinedSignInForm() {
  const [mode, setMode] = useState<AuthMode>("magic-link");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [magicLinkSent, setMagicLinkSent] = useState(false);
  const router = useRouter();

  const handlePasswordSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const { error } = await authClient.signIn.email({
      email,
      password,
    });

    setLoading(false);

    if (error) {
      setError("Invalid email or password");
      return;
    }

    router.push("/dashboard");
  };

  const handleMagicLinkSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const { error } = await authClient.signIn.magicLink({
      email,
      callbackURL: "/dashboard",
    });

    setLoading(false);

    if (error) {
      setError("Failed to send magic link");
      return;
    }

    setMagicLinkSent(true);
  };

  if (magicLinkSent) {
    return (
      <div className="text-center space-y-4">
        <h2 className="text-xl font-semibold">Check your email</h2>
        <p>We sent a magic link to <strong>{email}</strong></p>
        <button
          onClick={() => setMagicLinkSent(false)}
          className="text-blue-600 hover:underline"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Mode Toggle */}
      <div className="flex rounded-lg bg-gray-100 p-1">
        <button
          type="button"
          onClick={() => setMode("magic-link")}
          className={`flex-1 py-2 text-sm font-medium rounded-md transition ${
            mode === "magic-link"
              ? "bg-white shadow text-gray-900"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Magic Link
        </button>
        <button
          type="button"
          onClick={() => setMode("password")}
          className={`flex-1 py-2 text-sm font-medium rounded-md transition ${
            mode === "password"
              ? "bg-white shadow text-gray-900"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Password
        </button>
      </div>

      {/* Forms */}
      <form
        onSubmit={mode === "password" ? handlePasswordSignIn : handleMagicLinkSignIn}
        className="space-y-4"
      >
        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
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

        {mode === "password" && (
          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-1">
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
        )}

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
          {loading
            ? "Loading..."
            : mode === "password"
            ? "Sign In"
            : "Send Magic Link"}
        </button>
      </form>
    </div>
  );
}
```

### Magic Link with New User Name

```tsx
// components/auth/magic-link-with-name.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";

export function MagicLinkWithName() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [showNameField, setShowNameField] = useState(false);
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const { error } = await authClient.signIn.magicLink({
      email,
      name: name || undefined,
      callbackURL: "/dashboard",
      newUserCallbackURL: "/welcome",
    });

    setLoading(false);

    if (error) {
      setError(error.message);
      return;
    }

    setSent(true);
  };

  if (sent) {
    return (
      <div className="text-center space-y-4">
        <h2 className="text-xl font-semibold">Check your email</h2>
        <p>We sent a magic link to <strong>{email}</strong></p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center">Sign In</h2>

      <div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email address"
          className="w-full px-3 py-2 border rounded-md"
          required
        />
      </div>

      {showNameField ? (
        <div>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name (for new accounts)"
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setShowNameField(true)}
          className="text-sm text-blue-600 hover:underline"
        >
          New here? Add your name
        </button>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="w-full py-2 bg-blue-600 text-white rounded-md disabled:opacity-50"
      >
        {loading ? "Sending..." : "Send Magic Link"}
      </button>
    </form>
  );
}
```

### Styled Card Component

```tsx
// components/auth/magic-link-card.tsx
interface MagicLinkCardProps {
  children: React.ReactNode;
}

export function MagicLinkCard({ children }: MagicLinkCardProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        {children}
      </div>
    </div>
  );
}

// Usage
export default function SignInPage() {
  return (
    <MagicLinkCard>
      <MagicLinkForm />
    </MagicLinkCard>
  );
}
```

### Usage in Pages

```tsx
// app/(auth)/sign-in/page.tsx
import { MagicLinkForm } from "@/components/auth/magic-link-form";
import { MagicLinkCard } from "@/components/auth/magic-link-card";

export default function SignInPage() {
  return (
    <MagicLinkCard>
      <MagicLinkForm />
    </MagicLinkCard>
  );
}
```

### Usage

```
/auth.magicLink.form [component]
```

**User Input**: $ARGUMENTS

Available components:
- `basic` - Basic magic link form
- `cooldown` - Form with rate limiting
- `combined` - Password + Magic Link toggle
- `withName` - Form with name for new users
- `card` - Styled card wrapper
