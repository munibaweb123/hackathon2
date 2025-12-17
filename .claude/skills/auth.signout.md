---
description: Sign out a user via Better Auth API
---

## Better Auth: Sign Out

This skill signs out the current user and invalidates their session via the Better Auth API.

### Configuration

**Base URL**: `https://your-better-auth-url.com` (update in `.env` or configure via `/auth.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/auth/signout`
- **Content-Type**: application/json

### Arguments

Pass optional redirect URL: `/auth.signout [redirectUrl]`

**Example**: `/auth.signout /login`

### Client-Side Usage (TypeScript)

#### Basic Sign Out

```typescript
// Client-side
await authClient.signOut();
```

#### Sign Out with Redirect

```typescript
await authClient.signOut({
  fetchOptions: {
    onSuccess: () => {
      window.location.href = "/";
    },
  },
});
```

#### React Hook Implementation

```typescript
// hooks/useSignOut.ts
import { authClient } from "@/lib/auth-client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export function useSignOut() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const signOut = async (redirectTo: string = "/") => {
    setLoading(true);

    await authClient.signOut({
      fetchOptions: {
        onSuccess: () => {
          router.push(redirectTo);
        },
      },
    });

    setLoading(false);
  };

  return { signOut, loading };
}
```

#### React Component Example

```tsx
"use client";

import { useSignOut } from "@/hooks/useSignOut";

export function SignOutButton() {
  const { signOut, loading } = useSignOut();

  return (
    <button
      onClick={() => signOut("/")}
      disabled={loading}
      className="btn btn-secondary"
    >
      {loading ? "Signing out..." : "Sign Out"}
    </button>
  );
}
```

### Execution (curl)

```bash
# Load base URL from environment or use default
BASE_URL="${BETTER_AUTH_BASE_URL:-https://your-better-auth-url.com}"
TOKEN="${BETTER_AUTH_TOKEN}"

# Sign out user
curl -s -X POST "${BASE_URL}/auth/signout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" | jq .
```

### Expected Response

**Success (200 OK)**:
```json
{
  "success": true
}
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | User signed out, session invalidated |
| 401 | Unauthorized | Already signed out or invalid token |
| 500 | Server Error | Retry or check backend logs |

### Post-Signout Actions

After signing out:

1. **Clear local state**: Reset any user-related state in your app
2. **Clear stored tokens**: Remove tokens from localStorage/cookies
3. **Redirect**: Navigate to login or home page

```typescript
// Complete sign out flow
const handleSignOut = async () => {
  await authClient.signOut();

  // Clear local storage
  localStorage.removeItem("user");

  // Redirect to login
  window.location.href = "/login";
};
```

### Usage

```
/auth.signout [redirectUrl]
```

**User Input**: $ARGUMENTS

Parse the optional redirect URL argument and execute the signout request.

### Security Notes

- Always invalidate server-side session, not just client-side tokens
- Clear any cached user data after signout
- Consider clearing all browser storage for sensitive applications
