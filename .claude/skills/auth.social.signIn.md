---
description: Sign in with Social OAuth via Better Auth
---

## Better Auth: Social OAuth Sign In

This skill covers client-side social sign-in with Better Auth.

### Prerequisites

- Social providers configured on server (`@/lib/auth`)
- Auth client configured (`@/lib/auth-client`)

### Basic Sign In

```typescript
// Google
await authClient.signIn.social({
  provider: "google",
  callbackURL: "/dashboard",
});

// GitHub
await authClient.signIn.social({
  provider: "github",
  callbackURL: "/dashboard",
});

// Discord
await authClient.signIn.social({
  provider: "discord",
  callbackURL: "/dashboard",
});

// Apple
await authClient.signIn.social({
  provider: "apple",
  callbackURL: "/dashboard",
});
```

### Sign In Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `provider` | string | Yes | OAuth provider name |
| `callbackURL` | string | No | URL to redirect after sign in |
| `errorCallbackURL` | string | No | URL to redirect on error |
| `newUserCallbackURL` | string | No | URL for new users |

### With Callback URLs

```typescript
await authClient.signIn.social({
  provider: "google",
  callbackURL: "/dashboard",
  errorCallbackURL: "/sign-in?error=oauth_failed",
  newUserCallbackURL: "/onboarding",
});
```

### React Hook Implementation

```typescript
// hooks/useSocialSignIn.ts
import { authClient } from "@/lib/auth-client";
import { useState, useCallback } from "react";

type SocialProvider = "google" | "github" | "discord" | "apple" | "twitter";

interface SocialSignInOptions {
  callbackURL?: string;
  errorCallbackURL?: string;
  newUserCallbackURL?: string;
}

export function useSocialSignIn() {
  const [loading, setLoading] = useState<SocialProvider | null>(null);
  const [error, setError] = useState<string | null>(null);

  const signIn = useCallback(
    async (provider: SocialProvider, options: SocialSignInOptions = {}) => {
      setLoading(provider);
      setError(null);

      try {
        await authClient.signIn.social({
          provider,
          callbackURL: options.callbackURL || "/dashboard",
          errorCallbackURL: options.errorCallbackURL,
          newUserCallbackURL: options.newUserCallbackURL,
        });
      } catch (err) {
        setError("Failed to initiate sign in");
        setLoading(null);
      }
    },
    []
  );

  return {
    signIn,
    loading,
    error,
    isLoading: (provider: SocialProvider) => loading === provider,
  };
}
```

### Using the Hook

```tsx
"use client";

import { useSocialSignIn } from "@/hooks/useSocialSignIn";

export function SignInPage() {
  const { signIn, isLoading, error } = useSocialSignIn();

  return (
    <div className="space-y-4">
      {error && <p className="text-red-500">{error}</p>}

      <button
        onClick={() => signIn("google")}
        disabled={isLoading("google")}
      >
        {isLoading("google") ? "Connecting..." : "Continue with Google"}
      </button>

      <button
        onClick={() => signIn("github")}
        disabled={isLoading("github")}
      >
        {isLoading("github") ? "Connecting..." : "Continue with GitHub"}
      </button>
    </div>
  );
}
```

### Error Handling

```typescript
// Handle errors in callback URL
// app/sign-in/page.tsx
"use client";

import { useSearchParams } from "next/navigation";

export default function SignInPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");

  const getErrorMessage = (errorCode: string | null) => {
    switch (errorCode) {
      case "oauth_failed":
        return "OAuth authentication failed. Please try again.";
      case "access_denied":
        return "Access was denied. Please grant the required permissions.";
      case "account_exists":
        return "An account with this email already exists. Try a different sign-in method.";
      default:
        return null;
    }
  };

  const errorMessage = getErrorMessage(error);

  return (
    <div>
      {errorMessage && (
        <div className="bg-red-50 text-red-600 p-4 rounded-md mb-4">
          {errorMessage}
        </div>
      )}
      {/* Sign in buttons */}
    </div>
  );
}
```

### With fetchOptions Callbacks

```typescript
await authClient.signIn.social({
  provider: "google",
  callbackURL: "/dashboard",
  fetchOptions: {
    onRequest() {
      // Called before redirect
      setLoading(true);
    },
    onError(ctx) {
      // Called on error (before redirect if errorCallbackURL not set)
      console.error("OAuth error:", ctx.error);
    },
  },
});
```

### Dynamic Provider Selection

```typescript
type Provider = "google" | "github" | "discord";

async function handleSocialSignIn(provider: Provider) {
  const providerConfig: Record<Provider, { callbackURL: string }> = {
    google: { callbackURL: "/dashboard" },
    github: { callbackURL: "/dashboard" },
    discord: { callbackURL: "/discord-connected" },
  };

  await authClient.signIn.social({
    provider,
    ...providerConfig[provider],
  });
}
```

### Check Session After Sign In

```typescript
// After redirect to callbackURL
const { data: session } = await authClient.getSession();

if (session?.user) {
  console.log("Signed in as:", session.user.email);
  console.log("Provider:", session.user.accounts?.[0]?.provider);
}
```

### Server-Side Sign In (API Route)

```typescript
// app/api/social-signin/route.ts
import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { provider, callbackURL } = await request.json();

  try {
    const url = await auth.api.signInSocial({
      body: { provider, callbackURL },
    });

    return NextResponse.json({ url });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to generate OAuth URL" },
      { status: 500 }
    );
  }
}
```

### TypeScript Types

```typescript
type SocialProvider =
  | "google"
  | "github"
  | "discord"
  | "apple"
  | "microsoft"
  | "twitter"
  | "facebook"
  | "linkedin";

interface SocialSignInParams {
  provider: SocialProvider;
  callbackURL?: string;
  errorCallbackURL?: string;
  newUserCallbackURL?: string;
}

interface SocialSignInResult {
  url?: string;
  error?: {
    message: string;
    status: number;
  };
}
```

### Popup Window Sign In (Optional)

```typescript
// For popup-based OAuth (advanced)
async function signInWithPopup(provider: string) {
  const width = 500;
  const height = 600;
  const left = window.screenX + (window.outerWidth - width) / 2;
  const top = window.screenY + (window.outerHeight - height) / 2;

  const popup = window.open(
    `/api/auth/signin/${provider}`,
    "oauth",
    `width=${width},height=${height},left=${left},top=${top}`
  );

  // Listen for completion
  window.addEventListener("message", (event) => {
    if (event.data.type === "oauth_complete") {
      popup?.close();
      window.location.reload();
    }
  });
}
```

### Usage

```
/auth.social.signIn [provider]
```

**User Input**: $ARGUMENTS

Available providers:
- `google` - Google sign in
- `github` - GitHub sign in
- `discord` - Discord sign in
- `apple` - Apple sign in
- `hook` - React hook implementation
