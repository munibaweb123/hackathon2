---
description: Reset user password with token via Better Auth API
---

## Better Auth: Reset Password

This skill completes the password reset flow by setting a new password using the reset token.

### Configuration

**Base URL**: `https://your-better-auth-url.com` (update in `.env` or configure via `/auth.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/auth/reset-password`
- **Content-Type**: application/json

### Arguments

Pass token and new password: `/auth.resetPassword <token> <newPassword>`

**Example**: `/auth.resetPassword abc123token NewSecurePassword123!`

### Client-Side Usage (TypeScript)

#### Reset Password with Token

```typescript
// Client-side - on /reset-password page
// Extract token from URL query params
const token = new URLSearchParams(window.location.search).get("token");

await authClient.resetPassword({
  newPassword: "newSecurePassword123",
  token,
});
```

#### React Hook Implementation

```typescript
// hooks/useResetPassword.ts
import { authClient } from "@/lib/auth-client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function useResetPassword() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const resetPassword = async (newPassword: string) => {
    if (!token) {
      setError("Invalid or missing reset token");
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      await authClient.resetPassword({
        newPassword,
        token,
      });
      setSuccess(true);
      // Redirect to login after successful reset
      setTimeout(() => router.push("/login"), 2000);
      return true;
    } catch (err) {
      setError("Failed to reset password. Token may have expired.");
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { resetPassword, loading, error, success, hasToken: !!token };
}
```

#### React Form Component

```tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useSearchParams, useRouter } from "next/navigation";

export function ResetPasswordForm() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate passwords match
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Validate password strength
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    if (!token) {
      setError("Invalid reset link");
      return;
    }

    setLoading(true);

    try {
      await authClient.resetPassword({
        newPassword: password,
        token,
      });
      setSuccess(true);
      // Redirect to login after 2 seconds
      setTimeout(() => router.push("/login"), 2000);
    } catch (err) {
      setError("Failed to reset password. The link may have expired.");
    }

    setLoading(false);
  };

  if (!token) {
    return (
      <div className="error-message">
        <h3>Invalid Reset Link</h3>
        <p>This password reset link is invalid or has expired.</p>
        <a href="/forgot-password">Request a new reset link</a>
      </div>
    );
  }

  if (success) {
    return (
      <div className="success-message">
        <h3>Password Reset Successful</h3>
        <p>Your password has been reset. Redirecting to login...</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Set New Password</h2>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="New password"
        minLength={8}
        required
      />
      <input
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        placeholder="Confirm new password"
        minLength={8}
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "Resetting..." : "Reset Password"}
      </button>
    </form>
  );
}
```

### Execution (curl)

```bash
# Load base URL from environment or use default
BASE_URL="${BETTER_AUTH_BASE_URL:-https://your-better-auth-url.com}"

# Reset password with token
curl -s -X POST "${BASE_URL}/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "{{TOKEN}}",
    "newPassword": "{{NEW_PASSWORD}}"
  }' | jq .
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
| 200 | Success | Password reset successfully |
| 400 | Bad Request | Check request body format |
| 401 | Unauthorized | Token invalid or expired |
| 422 | Validation Error | Password doesn't meet requirements |
| 500 | Server Error | Retry or check backend logs |

### Password Requirements

Ensure the new password meets your configured requirements:

```typescript
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
  },
});
```

### Client-Side Password Validation

```typescript
function validatePassword(password: string): string | null {
  if (password.length < 8) {
    return "Password must be at least 8 characters";
  }
  if (!/[A-Z]/.test(password)) {
    return "Password must contain at least one uppercase letter";
  }
  if (!/[a-z]/.test(password)) {
    return "Password must contain at least one lowercase letter";
  }
  if (!/[0-9]/.test(password)) {
    return "Password must contain at least one number";
  }
  return null;
}
```

### Usage

```
/auth.resetPassword <token> <newPassword>
```

**User Input**: $ARGUMENTS

Parse the token and new password arguments, then execute the password reset.

### Security Notes

- Reset tokens should be single-use
- Tokens should expire (typically 1 hour)
- Always use HTTPS
- Never log or display passwords
- Consider sending a confirmation email after password reset
