---
description: Resend email verification link via Better Auth API
---

## Better Auth: Resend Verification

This skill resends the email verification link to a user via the Better Auth API.

### Configuration

**Base URL**: `https://your-better-auth-url.com` (update in `.env` or configure via `/auth.config`)

### Endpoint Details

- **Method**: POST
- **Path**: `/auth/send-verification-email`
- **Content-Type**: application/json

### Arguments

Pass user email: `/auth.resendVerification <email> [callbackURL]`

**Example**: `/auth.resendVerification user@example.com /dashboard`

### Client-Side Usage (TypeScript)

#### Basic Usage

```typescript
// Client-side
await authClient.sendVerificationEmail({
  email: "user@example.com",
  callbackURL: "/dashboard",
});
```

#### React Hook Implementation

```typescript
// hooks/useResendVerification.ts
import { authClient } from "@/lib/auth-client";
import { useState, useCallback } from "react";

export function useResendVerification() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  const resend = useCallback(async (email: string, callbackURL: string = "/dashboard") => {
    if (cooldown > 0) {
      setError(`Please wait ${cooldown} seconds before requesting again`);
      return false;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await authClient.sendVerificationEmail({
        email,
        callbackURL,
      });
      setSuccess(true);
      // Set 60 second cooldown
      setCooldown(60);
      const timer = setInterval(() => {
        setCooldown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return true;
    } catch (err) {
      setError("Failed to send verification email. Please try again later.");
      return false;
    } finally {
      setLoading(false);
    }
  }, [cooldown]);

  return { resend, loading, error, success, cooldown };
}
```

#### React Component

```tsx
"use client";

import { useState } from "react";
import { useResendVerification } from "@/hooks/useResendVerification";

interface ResendVerificationProps {
  email: string;
}

export function ResendVerificationButton({ email }: ResendVerificationProps) {
  const { resend, loading, error, success, cooldown } = useResendVerification();

  const handleClick = () => {
    resend(email, "/dashboard");
  };

  return (
    <div className="resend-verification">
      <button
        onClick={handleClick}
        disabled={loading || cooldown > 0}
        className="btn btn-secondary"
      >
        {loading
          ? "Sending..."
          : cooldown > 0
          ? `Resend in ${cooldown}s`
          : "Resend Verification Email"}
      </button>

      {success && (
        <p className="success-message">
          Verification email sent! Check your inbox.
        </p>
      )}

      {error && <p className="error-message">{error}</p>}
    </div>
  );
}
```

#### Full Resend Verification Page

```tsx
// app/resend-verification/page.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";

export default function ResendVerificationPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);

    try {
      await authClient.sendVerificationEmail({
        email,
        callbackURL: "/dashboard",
      });
      setSuccess(true);
    } catch (err) {
      setError("Failed to send verification email. Please try again.");
    }

    setLoading(false);
  };

  return (
    <div className="resend-verification-page">
      <h1>Resend Verification Email</h1>

      {success ? (
        <div className="success-card">
          <h2>Email Sent!</h2>
          <p>
            We've sent a verification link to <strong>{email}</strong>.
          </p>
          <p>Please check your inbox and spam folder.</p>
          <button onClick={() => setSuccess(false)}>
            Send to a different email
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <p>Enter your email address to receive a new verification link.</p>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />
          </div>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send Verification Email"}
          </button>
        </form>
      )}

      <div className="help-section">
        <h3>Troubleshooting</h3>
        <ul>
          <li>Check your spam/junk folder</li>
          <li>Make sure you're using the correct email address</li>
          <li>Wait a few minutes for the email to arrive</li>
          <li>
            Contact <a href="/support">support</a> if you continue having issues
          </li>
        </ul>
      </div>
    </div>
  );
}
```

### Execution (curl)

```bash
# Load base URL from environment or use default
BASE_URL="${BETTER_AUTH_BASE_URL:-https://your-better-auth-url.com}"

# Resend verification email
curl -s -X POST "${BASE_URL}/auth/send-verification-email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "{{EMAIL}}",
    "callbackURL": "{{CALLBACK_URL}}"
  }' | jq .
```

### Expected Response

**Success (200 OK)**:
```json
{
  "success": true
}
```

Note: For security, response is the same whether email exists or not.

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Verification email sent |
| 400 | Bad Request | Check email format |
| 429 | Too Many Requests | Rate limited, implement cooldown |
| 500 | Server Error | Retry or check backend logs |

### Rate Limiting

Implement client-side cooldown to prevent abuse:

```typescript
const COOLDOWN_SECONDS = 60;

function ResendButton({ email }: { email: string }) {
  const [cooldown, setCooldown] = useState(0);
  const [lastSent, setLastSent] = useState<Date | null>(null);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleResend = async () => {
    await authClient.sendVerificationEmail({ email, callbackURL: "/dashboard" });
    setCooldown(COOLDOWN_SECONDS);
    setLastSent(new Date());
  };

  return (
    <button onClick={handleResend} disabled={cooldown > 0}>
      {cooldown > 0 ? `Wait ${cooldown}s` : "Resend Email"}
    </button>
  );
}
```

### Usage

```
/auth.resendVerification <email> [callbackURL]
```

**User Input**: $ARGUMENTS

Parse the email and optional callback URL arguments, then send the verification email request.

### Security Notes

- Rate limit resend requests (both client and server side)
- Same response for existing/non-existing emails
- Log verification resend attempts for monitoring
- Consider CAPTCHA for repeated requests
