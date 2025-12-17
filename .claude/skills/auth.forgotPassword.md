---
description: Request a password reset email via Better Auth API
---

## Better Auth: Forgot Password

This skill initiates the password reset flow by sending a reset email to the user.

### Configuration

**Base URL**: `https://your-better-auth-url.com` (update in `.env` or configure via `/auth.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/auth/forget-password`
- **Content-Type**: application/json

### Arguments

Pass user email: `/auth.forgotPassword <email> [redirectTo]`

**Example**: `/auth.forgotPassword user@example.com /reset-password`

### Client-Side Usage (TypeScript)

#### Request Password Reset

```typescript
// Client-side
await authClient.forgetPassword({
  email: "user@example.com",
  redirectTo: "/reset-password", // URL where user will reset password
});
```

#### React Hook Implementation

```typescript
// hooks/useForgotPassword.ts
import { authClient } from "@/lib/auth-client";
import { useState } from "react";

export function useForgotPassword() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const requestReset = async (email: string, redirectTo: string = "/reset-password") => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await authClient.forgetPassword({
        email,
        redirectTo,
      });
      setSuccess(true);
    } catch (err) {
      setError("Failed to send reset email. Please try again.");
    }

    setLoading(false);
  };

  return { requestReset, loading, error, success };
}
```

#### React Form Component

```tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";

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
      setError("Failed to send reset email");
    }

    setLoading(false);
  };

  if (success) {
    return (
      <div className="success-message">
        <h3>Check your email</h3>
        <p>We've sent a password reset link to {email}</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Forgot Password</h2>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "Sending..." : "Send Reset Link"}
      </button>
    </form>
  );
}
```

### Server Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    sendResetPassword: async ({ user, url }) => {
      // Integrate with your email provider (e.g., Resend, SendGrid)
      await sendEmail({
        to: user.email,
        subject: "Reset your password",
        html: `
          <h1>Reset Your Password</h1>
          <p>Click the link below to reset your password:</p>
          <a href="${url}">Reset Password</a>
          <p>This link will expire in 1 hour.</p>
          <p>If you didn't request this, please ignore this email.</p>
        `,
      });
    },
  },
});
```

### Execution (curl)

```bash
# Load base URL from environment or use default
BASE_URL="${BETTER_AUTH_BASE_URL:-https://your-better-auth-url.com}"

# Request password reset
curl -s -X POST "${BASE_URL}/auth/forget-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "{{EMAIL}}",
    "redirectTo": "{{REDIRECT_TO}}"
  }' | jq .
```

### Expected Response

**Success (200 OK)**:
```json
{
  "success": true
}
```

Note: For security, the response is the same whether the email exists or not.

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Reset email sent (or email doesn't exist - same response for security) |
| 400 | Bad Request | Check request body format |
| 429 | Too Many Requests | Rate limited, wait before retrying |
| 500 | Server Error | Retry or check backend logs |

### Security Considerations

- **Same response for existing/non-existing emails**: Prevents email enumeration
- **Rate limiting**: Implement rate limits to prevent abuse
- **Token expiration**: Reset tokens should expire (typically 1 hour)
- **Single use**: Tokens should be invalidated after use

### Usage

```
/auth.forgotPassword <email> [redirectTo]
```

**User Input**: $ARGUMENTS

Parse the email and optional redirect URL arguments, then execute the password reset request.
