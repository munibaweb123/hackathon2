---
description: Sign in with Magic Link via Better Auth
---

## Better Auth: Magic Link Sign In

This skill covers requesting and handling Magic Link sign-in with Better Auth.

### Prerequisites

- Magic Link plugin configured on server (`@/lib/auth`)
- Magic Link client plugin configured (`@/lib/auth-client`)

### Basic Usage

```typescript
const { error } = await authClient.signIn.magicLink({
  email: "user@example.com",
  callbackURL: "/dashboard",
});

if (error) {
  console.error("Failed to send magic link:", error.message);
}
```

### Request Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `email` | string | Yes | User's email address |
| `callbackURL` | string | No | URL to redirect after sign in |
| `newUserCallbackURL` | string | No | URL for new users (if different) |
| `name` | string | No | Name for new users |

### With Callback URL

```typescript
await authClient.signIn.magicLink({
  email: "user@example.com",
  callbackURL: "/dashboard", // Redirect here after sign in
});
```

### With New User Callback

Redirect new users to a different page (e.g., onboarding):

```typescript
await authClient.signIn.magicLink({
  email: "new@example.com",
  callbackURL: "/dashboard",        // Existing users go here
  newUserCallbackURL: "/welcome",   // New users go here
});
```

### With Name for New Users

Pre-fill name when creating new accounts:

```typescript
await authClient.signIn.magicLink({
  email: "new@example.com",
  name: "John Doe", // Used if user doesn't exist
  callbackURL: "/dashboard",
});
```

### React Hook Implementation

```typescript
// hooks/useMagicLink.ts
import { authClient } from "@/lib/auth-client";
import { useState, useCallback } from "react";

interface MagicLinkOptions {
  callbackURL?: string;
  newUserCallbackURL?: string;
  name?: string;
}

export function useMagicLink() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);
  const [email, setEmail] = useState<string>("");

  const sendMagicLink = useCallback(
    async (emailAddress: string, options: MagicLinkOptions = {}) => {
      setLoading(true);
      setError(null);
      setSent(false);
      setEmail(emailAddress);

      const { error } = await authClient.signIn.magicLink({
        email: emailAddress,
        callbackURL: options.callbackURL || "/dashboard",
        newUserCallbackURL: options.newUserCallbackURL,
        name: options.name,
      });

      setLoading(false);

      if (error) {
        const errorMessage = getMagicLinkError(error.status);
        setError(errorMessage);
        return { success: false, error: errorMessage };
      }

      setSent(true);
      return { success: true };
    },
    []
  );

  const reset = useCallback(() => {
    setSent(false);
    setError(null);
    setEmail("");
  }, []);

  return {
    sendMagicLink,
    loading,
    error,
    sent,
    email,
    reset,
  };
}

function getMagicLinkError(status?: number): string {
  switch (status) {
    case 404:
      return "No account found with this email";
    case 429:
      return "Too many requests. Please wait a moment.";
    case 400:
      return "Invalid email address";
    default:
      return "Failed to send magic link. Please try again.";
  }
}
```

### Error Handling

```typescript
const { error } = await authClient.signIn.magicLink({
  email,
  callbackURL: "/dashboard",
});

if (error) {
  switch (error.status) {
    case 400:
      setError("Invalid email address");
      break;
    case 404:
      // Only if disableSignUp is true
      setError("No account found with this email");
      break;
    case 429:
      setError("Too many requests. Please wait a moment.");
      break;
    default:
      setError("Failed to send magic link");
  }
}
```

### With fetchOptions Callbacks

```typescript
await authClient.signIn.magicLink({
  email,
  callbackURL: "/dashboard",
  fetchOptions: {
    onRequest() {
      // Called before request
      setLoading(true);
    },
    onSuccess() {
      // Called on success
      setSent(true);
      setLoading(false);
    },
    onError(ctx) {
      // Called on error
      setLoading(false);
      if (ctx.error.status === 404) {
        setError("No account found with this email");
      } else if (ctx.error.status === 429) {
        setError("Too many requests. Please wait a moment.");
      } else {
        setError("Failed to send magic link");
      }
    },
  },
});
```

### Verify Magic Link Token

When user clicks the link, verify the token:

```typescript
// Usually handled automatically by Better Auth
// But can be done manually if needed:

const { error } = await authClient.signIn.magicLink({
  token: "token-from-url",
});

if (error) {
  console.error("Invalid or expired link");
}
```

### Complete Sign In Flow

```typescript
// 1. Request magic link
async function requestMagicLink(email: string) {
  const { error } = await authClient.signIn.magicLink({
    email,
    callbackURL: "/dashboard",
  });

  if (error) {
    throw new Error("Failed to send magic link");
  }

  return { success: true, message: "Check your email!" };
}

// 2. User clicks link in email -> Better Auth handles verification
// 3. User is redirected to callbackURL with session

// 4. Check session
const { data: session } = await authClient.getSession();
if (session?.user) {
  console.log("Signed in as:", session.user.email);
}
```

### Rate Limiting Consideration

```typescript
// Implement client-side rate limiting
const COOLDOWN_SECONDS = 60;
const [cooldown, setCooldown] = useState(0);

const sendMagicLink = async (email: string) => {
  if (cooldown > 0) {
    setError(`Please wait ${cooldown} seconds`);
    return;
  }

  const { error } = await authClient.signIn.magicLink({ email });

  if (!error) {
    // Start cooldown
    setCooldown(COOLDOWN_SECONDS);
    const timer = setInterval(() => {
      setCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }
};
```

### TypeScript Types

```typescript
interface MagicLinkSignInParams {
  email: string;
  callbackURL?: string;
  newUserCallbackURL?: string;
  name?: string;
  token?: string; // For verification
}

interface MagicLinkResponse {
  data?: {
    user: {
      id: string;
      email: string;
      name: string | null;
      emailVerified: boolean;
    };
  };
  error?: {
    status: number;
    message: string;
  };
}
```

### Usage

```
/auth.magicLink.signIn [option]
```

**User Input**: $ARGUMENTS

Available options:
- `basic` - Basic magic link request
- `callback` - With callback URLs
- `newUser` - With new user handling
- `hook` - React hook implementation
- `error` - Error handling patterns
