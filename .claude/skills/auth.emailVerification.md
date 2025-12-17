---
description: Configure and manage email verification via Better Auth API
---

## Better Auth: Email Verification

This skill configures email verification and handles verification flows in Better Auth.

### Configuration

**Base URL**: `https://your-better-auth-url.com` (update in `.env` or configure via `/auth.config`)

### Server Configuration

#### Enable Email Verification

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    sendVerificationEmail: async ({ user, url }) => {
      // Integrate with your email provider (e.g., Resend, SendGrid)
      await sendEmail({
        to: user.email,
        subject: "Verify your email address",
        html: `
          <h1>Welcome!</h1>
          <p>Please verify your email address by clicking the link below:</p>
          <a href="${url}">Verify Email</a>
          <p>This link will expire in 24 hours.</p>
          <p>If you didn't create an account, please ignore this email.</p>
        `,
      });
    },
  },
});
```

#### Email Provider Integration (Resend Example)

```typescript
// lib/email.ts
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendEmail({
  to,
  subject,
  html,
}: {
  to: string;
  subject: string;
  html: string;
}) {
  await resend.emails.send({
    from: "noreply@yourdomain.com",
    to,
    subject,
    html,
  });
}
```

### Client-Side Usage

#### Resend Verification Email

```typescript
// Client-side
await authClient.sendVerificationEmail({
  email: "user@example.com",
  callbackURL: "/dashboard", // Where to redirect after verification
});
```

#### React Hook Implementation

```typescript
// hooks/useEmailVerification.ts
import { authClient } from "@/lib/auth-client";
import { useState } from "react";

export function useEmailVerification() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const resendVerification = async (email: string, callbackURL: string = "/dashboard") => {
    setLoading(true);
    setError(null);

    try {
      await authClient.sendVerificationEmail({
        email,
        callbackURL,
      });
      setSent(true);
      return true;
    } catch (err) {
      setError("Failed to send verification email. Please try again.");
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { resendVerification, loading, error, sent };
}
```

#### Verification Pending Component

```tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";

interface VerificationPendingProps {
  email: string;
}

export function VerificationPending({ email }: VerificationPendingProps) {
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleResend = async () => {
    setLoading(true);
    setError("");

    try {
      await authClient.sendVerificationEmail({
        email,
        callbackURL: "/dashboard",
      });
      setSent(true);
    } catch (err) {
      setError("Failed to resend verification email");
    }

    setLoading(false);
  };

  return (
    <div className="verification-pending">
      <h2>Verify Your Email</h2>
      <p>
        We've sent a verification email to <strong>{email}</strong>.
      </p>
      <p>Please check your inbox and click the verification link.</p>

      {sent ? (
        <p className="success">Verification email resent!</p>
      ) : (
        <button onClick={handleResend} disabled={loading}>
          {loading ? "Sending..." : "Resend Verification Email"}
        </button>
      )}

      {error && <p className="error">{error}</p>}

      <div className="tips">
        <h4>Didn't receive the email?</h4>
        <ul>
          <li>Check your spam/junk folder</li>
          <li>Make sure {email} is correct</li>
          <li>Wait a few minutes and try again</li>
        </ul>
      </div>
    </div>
  );
}
```

#### Check Verification Status

```typescript
// Check if current user's email is verified
const { data: session } = await authClient.getSession();

if (session?.user && !session.user.emailVerified) {
  // Show verification pending UI
  return <VerificationPending email={session.user.email} />;
}
```

### Verification Page Component

```tsx
// app/verify-email/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";

export default function VerifyEmailPage() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  useEffect(() => {
    async function verifyEmail() {
      if (!token) {
        setStatus("error");
        return;
      }

      try {
        await authClient.verifyEmail({ token });
        setStatus("success");
        // Redirect to dashboard after 2 seconds
        setTimeout(() => router.push("/dashboard"), 2000);
      } catch (err) {
        setStatus("error");
      }
    }

    verifyEmail();
  }, [token, router]);

  if (status === "loading") {
    return <div>Verifying your email...</div>;
  }

  if (status === "success") {
    return (
      <div className="success">
        <h2>Email Verified!</h2>
        <p>Your email has been verified. Redirecting to dashboard...</p>
      </div>
    );
  }

  return (
    <div className="error">
      <h2>Verification Failed</h2>
      <p>This verification link is invalid or has expired.</p>
      <a href="/resend-verification">Request a new verification email</a>
    </div>
  );
}
```

### Protected Routes (Require Verification)

```tsx
// middleware.ts
import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";

export async function middleware(request: Request) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  if (session?.user && !session.user.emailVerified) {
    // Redirect unverified users to verification pending page
    return NextResponse.redirect(new URL("/verify-pending", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/settings/:path*"],
};
```

### Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Email sent or verified |
| 400 | Bad Request | Invalid token or request format |
| 401 | Unauthorized | Token expired or invalid |
| 429 | Too Many Requests | Rate limited, wait before retrying |
| 500 | Server Error | Retry or check backend logs |

### Usage

```
/auth.emailVerification [resend|status]
```

**User Input**: $ARGUMENTS

- `resend` - Resend verification email to current user
- `status` - Check verification status

### Security Notes

- Verification tokens should expire (typically 24 hours)
- Rate limit verification email requests
- Use secure, random tokens
- Always verify email before allowing sensitive operations
