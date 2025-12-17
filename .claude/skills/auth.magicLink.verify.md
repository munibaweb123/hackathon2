---
description: Magic Link verification page for Better Auth
---

## Better Auth: Magic Link Verification

This skill covers handling magic link verification when users click the link in their email.

### Overview

When a user clicks the magic link:
1. They are redirected to your app with a token in the URL
2. The token is verified
3. A session is created
4. User is redirected to the callback URL

### Default Behavior

By default, Better Auth handles verification automatically. The user is redirected to the `callbackURL` specified when requesting the magic link.

### Custom Verification Page

If you need custom verification handling:

```tsx
// app/auth/verify/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";

export default function VerifyMagicLinkPage() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState<string>("");
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  useEffect(() => {
    async function verifyToken() {
      if (!token) {
        setStatus("error");
        setError("No verification token found");
        return;
      }

      try {
        const { error } = await authClient.signIn.magicLink({
          token,
        });

        if (error) {
          setStatus("error");
          setError(error.message || "Verification failed");
          return;
        }

        setStatus("success");
        // Redirect after short delay
        setTimeout(() => {
          router.push("/dashboard");
        }, 1500);
      } catch (err) {
        setStatus("error");
        setError("An unexpected error occurred");
      }
    }

    verifyToken();
  }, [token, router]);

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verifying your link...</p>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-md w-full text-center p-8">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Invalid or Expired Link
          </h2>
          <p className="text-gray-600 mb-6">
            {error || "This magic link is invalid or has expired."}
          </p>
          <a
            href="/sign-in"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Request New Link
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg
            className="w-8 h-8 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
          Successfully Signed In!
        </h2>
        <p className="text-gray-600">Redirecting to dashboard...</p>
      </div>
    </div>
  );
}
```

### Loading States Component

```tsx
// components/auth/verify-magic-link.tsx
"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";

type VerifyStatus = "loading" | "success" | "error" | "expired";

export function VerifyMagicLink() {
  const [status, setStatus] = useState<VerifyStatus>("loading");
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      return;
    }

    authClient.signIn
      .magicLink({ token })
      .then(({ error }) => {
        if (error) {
          if (error.status === 401) {
            setStatus("expired");
          } else {
            setStatus("error");
          }
        } else {
          setStatus("success");
          router.push("/dashboard");
        }
      })
      .catch(() => {
        setStatus("error");
      });
  }, [token, router]);

  const statusConfig = {
    loading: {
      icon: <LoadingSpinner />,
      title: "Verifying...",
      description: "Please wait while we verify your link.",
    },
    success: {
      icon: <CheckIcon />,
      title: "Success!",
      description: "Redirecting you now...",
    },
    expired: {
      icon: <ClockIcon />,
      title: "Link Expired",
      description: "This magic link has expired. Please request a new one.",
      action: { href: "/sign-in", label: "Request New Link" },
    },
    error: {
      icon: <ErrorIcon />,
      title: "Something Went Wrong",
      description: "We couldn't verify your link. Please try again.",
      action: { href: "/sign-in", label: "Back to Sign In" },
    },
  };

  const config = statusConfig[status];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="mb-6">{config.icon}</div>
        <h1 className="text-2xl font-bold mb-2">{config.title}</h1>
        <p className="text-gray-600 mb-6">{config.description}</p>
        {config.action && (
          <a
            href={config.action.href}
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            {config.action.label}
          </a>
        )}
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="w-16 h-16 mx-auto">
      <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600"></div>
    </div>
  );
}

function CheckIcon() {
  return (
    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
      <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    </div>
  );
}

function ClockIcon() {
  return (
    <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto">
      <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
  );
}

function ErrorIcon() {
  return (
    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
      <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    </div>
  );
}
```

### Suspense Wrapper

```tsx
// app/auth/verify/page.tsx
import { Suspense } from "react";
import { VerifyMagicLink } from "@/components/auth/verify-magic-link";

function LoadingFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <VerifyMagicLink />
    </Suspense>
  );
}
```

### Server Component Verification

```tsx
// app/auth/verify/page.tsx
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { headers } from "next/headers";

interface PageProps {
  searchParams: { token?: string };
}

export default async function VerifyPage({ searchParams }: PageProps) {
  const { token } = searchParams;

  if (!token) {
    return (
      <div className="text-center p-8">
        <h1>Invalid Link</h1>
        <p>No verification token found.</p>
        <a href="/sign-in">Back to Sign In</a>
      </div>
    );
  }

  try {
    // Verify on server
    const session = await auth.api.signInMagicLink({
      body: { token },
    });

    if (session) {
      redirect("/dashboard");
    }
  } catch (error) {
    return (
      <div className="text-center p-8">
        <h1>Link Expired or Invalid</h1>
        <p>Please request a new magic link.</p>
        <a href="/sign-in">Request New Link</a>
      </div>
    );
  }
}
```

### Hook for Verification Status

```typescript
// hooks/useMagicLinkVerify.ts
import { useState, useEffect, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";

type VerifyStatus = "idle" | "loading" | "success" | "error" | "expired";

interface UseVerifyOptions {
  redirectTo?: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function useMagicLinkVerify(options: UseVerifyOptions = {}) {
  const [status, setStatus] = useState<VerifyStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  const verify = useCallback(async () => {
    if (!token) {
      setStatus("error");
      setError("No token provided");
      return;
    }

    setStatus("loading");
    setError(null);

    try {
      const { error: authError } = await authClient.signIn.magicLink({ token });

      if (authError) {
        setStatus(authError.status === 401 ? "expired" : "error");
        setError(authError.message);
        options.onError?.(authError.message);
        return;
      }

      setStatus("success");
      options.onSuccess?.();

      if (options.redirectTo) {
        router.push(options.redirectTo);
      }
    } catch (err) {
      setStatus("error");
      setError("Verification failed");
      options.onError?.("Verification failed");
    }
  }, [token, router, options]);

  useEffect(() => {
    if (token && status === "idle") {
      verify();
    }
  }, [token, status, verify]);

  return {
    status,
    error,
    hasToken: !!token,
    retry: verify,
  };
}
```

### Usage with Hook

```tsx
// app/auth/verify/page.tsx
"use client";

import { useMagicLinkVerify } from "@/hooks/useMagicLinkVerify";

export default function VerifyPage() {
  const { status, error, retry } = useMagicLinkVerify({
    redirectTo: "/dashboard",
    onSuccess: () => console.log("Verified!"),
    onError: (err) => console.error(err),
  });

  if (status === "loading") {
    return <p>Verifying...</p>;
  }

  if (status === "error" || status === "expired") {
    return (
      <div>
        <p>{error}</p>
        <button onClick={retry}>Try Again</button>
        <a href="/sign-in">Request New Link</a>
      </div>
    );
  }

  if (status === "success") {
    return <p>Success! Redirecting...</p>;
  }

  return null;
}
```

### Usage

```
/auth.magicLink.verify [type]
```

**User Input**: $ARGUMENTS

Available types:
- `page` - Full verification page component
- `component` - Reusable verification component
- `hook` - Verification hook
- `server` - Server component verification
