---
description: Next.js Server Actions for Better Auth authentication
---

## Better Auth: Next.js Server Actions

This skill provides server-side authentication actions using Next.js Server Actions with Better Auth.

### Prerequisites

- Next.js 13+ with App Router
- Better Auth server configured (`@/lib/auth`)
- TypeScript enabled

### Server-Side Auth Instance

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "./prisma";

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    sendResetPassword: async ({ user, url }) => {
      await sendEmail({
        to: user.email,
        subject: "Reset your password",
        html: `<a href="${url}">Reset Password</a>`,
      });
    },
    sendVerificationEmail: async ({ user, url }) => {
      await sendEmail({
        to: user.email,
        subject: "Verify your email",
        html: `<a href="${url}">Verify Email</a>`,
      });
    },
  },
});
```

### Sign In Server Action

```typescript
// app/actions/auth/sign-in.ts
"use server";

import { auth } from "@/lib/auth";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

interface SignInResult {
  success: boolean;
  error?: string;
}

export async function signIn(formData: FormData): Promise<SignInResult> {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  if (!email || !password) {
    return { success: false, error: "Email and password are required" };
  }

  try {
    const response = await auth.api.signInEmail({
      body: { email, password },
    });

    if (!response) {
      return { success: false, error: "Invalid credentials" };
    }

    // Set session cookie
    const cookieStore = await cookies();
    if (response.headers) {
      const setCookie = response.headers.get("set-cookie");
      if (setCookie) {
        // Parse and set cookies
        const cookieParts = setCookie.split(";")[0].split("=");
        cookieStore.set(cookieParts[0], cookieParts[1], {
          httpOnly: true,
          secure: process.env.NODE_ENV === "production",
          sameSite: "lax",
        });
      }
    }

    return { success: true };
  } catch (error) {
    console.error("Sign in error:", error);
    return { success: false, error: "Invalid email or password" };
  }
}

export async function signInWithRedirect(formData: FormData) {
  const result = await signIn(formData);

  if (result.success) {
    redirect("/dashboard");
  }

  return result;
}
```

### Sign Up Server Action

```typescript
// app/actions/auth/sign-up.ts
"use server";

import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

interface SignUpData {
  email: string;
  password: string;
  name?: string;
}

interface SignUpResult {
  success: boolean;
  error?: string;
  requiresVerification?: boolean;
}

export async function signUp(formData: FormData): Promise<SignUpResult> {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const name = formData.get("name") as string | undefined;

  // Server-side validation
  if (!email || !password) {
    return { success: false, error: "Email and password are required" };
  }

  if (password.length < 8) {
    return { success: false, error: "Password must be at least 8 characters" };
  }

  try {
    await auth.api.signUpEmail({
      body: { email, password, name },
    });

    return {
      success: true,
      requiresVerification: true,
    };
  } catch (error: any) {
    console.error("Sign up error:", error);

    if (error?.status === 409) {
      return { success: false, error: "An account with this email already exists" };
    }

    return { success: false, error: "Sign up failed. Please try again." };
  }
}

export async function signUpWithRedirect(formData: FormData) {
  const result = await signUp(formData);

  if (result.success) {
    const email = formData.get("email") as string;
    redirect(`/verify-email?email=${encodeURIComponent(email)}`);
  }

  return result;
}
```

### Sign Out Server Action

```typescript
// app/actions/auth/sign-out.ts
"use server";

import { auth } from "@/lib/auth";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function signOut() {
  try {
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get("better-auth.session_token");

    if (sessionCookie) {
      await auth.api.signOut({
        headers: {
          cookie: `better-auth.session_token=${sessionCookie.value}`,
        },
      });
    }

    // Clear cookies
    cookieStore.delete("better-auth.session_token");
  } catch (error) {
    console.error("Sign out error:", error);
  }

  redirect("/");
}
```

### Password Reset Server Actions

```typescript
// app/actions/auth/password-reset.ts
"use server";

import { auth } from "@/lib/auth";

interface PasswordResetResult {
  success: boolean;
  error?: string;
}

export async function requestPasswordReset(formData: FormData): Promise<PasswordResetResult> {
  const email = formData.get("email") as string;

  if (!email) {
    return { success: false, error: "Email is required" };
  }

  try {
    await auth.api.forgetPassword({
      body: {
        email,
        redirectTo: "/reset-password",
      },
    });

    // Always return success to prevent email enumeration
    return { success: true };
  } catch (error) {
    console.error("Password reset request error:", error);
    return { success: true }; // Still return success for security
  }
}

export async function resetPassword(formData: FormData): Promise<PasswordResetResult> {
  const token = formData.get("token") as string;
  const newPassword = formData.get("newPassword") as string;

  if (!token || !newPassword) {
    return { success: false, error: "Token and new password are required" };
  }

  if (newPassword.length < 8) {
    return { success: false, error: "Password must be at least 8 characters" };
  }

  try {
    await auth.api.resetPassword({
      body: { token, newPassword },
    });

    return { success: true };
  } catch (error) {
    console.error("Password reset error:", error);
    return { success: false, error: "Failed to reset password. Link may have expired." };
  }
}
```

### Email Verification Server Action

```typescript
// app/actions/auth/email-verification.ts
"use server";

import { auth } from "@/lib/auth";

interface VerificationResult {
  success: boolean;
  error?: string;
}

export async function verifyEmail(token: string): Promise<VerificationResult> {
  if (!token) {
    return { success: false, error: "Verification token is required" };
  }

  try {
    await auth.api.verifyEmail({
      body: { token },
    });

    return { success: true };
  } catch (error) {
    console.error("Email verification error:", error);
    return { success: false, error: "Verification failed. Link may have expired." };
  }
}

export async function resendVerificationEmail(formData: FormData): Promise<VerificationResult> {
  const email = formData.get("email") as string;

  if (!email) {
    return { success: false, error: "Email is required" };
  }

  try {
    await auth.api.sendVerificationEmail({
      body: {
        email,
        callbackURL: "/dashboard",
      },
    });

    return { success: true };
  } catch (error) {
    console.error("Resend verification error:", error);
    return { success: true }; // Return success for security
  }
}
```

### Get Session Server Action

```typescript
// app/actions/auth/session.ts
"use server";

import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function getSession() {
  try {
    const headersList = await headers();
    const session = await auth.api.getSession({
      headers: headersList,
    });

    return session;
  } catch (error) {
    console.error("Get session error:", error);
    return null;
  }
}

export async function requireAuth() {
  const session = await getSession();

  if (!session?.user) {
    redirect("/login");
  }

  return session;
}

export async function requireVerifiedEmail() {
  const session = await getSession();

  if (!session?.user) {
    redirect("/login");
  }

  if (!session.user.emailVerified) {
    redirect(`/verify-email?email=${encodeURIComponent(session.user.email)}`);
  }

  return session;
}
```

### Centralized Auth Actions Export

```typescript
// app/actions/auth/index.ts
"use server";

export { signIn, signInWithRedirect } from "./sign-in";
export { signUp, signUpWithRedirect } from "./sign-up";
export { signOut } from "./sign-out";
export { requestPasswordReset, resetPassword } from "./password-reset";
export { verifyEmail, resendVerificationEmail } from "./email-verification";
export { getSession, requireAuth, requireVerifiedEmail } from "./session";
```

### Using Server Actions in Forms

```tsx
// app/(auth)/login/page.tsx
import { signInWithRedirect } from "@/app/actions/auth";

export default function LoginPage() {
  return (
    <form action={signInWithRedirect}>
      <input type="email" name="email" placeholder="Email" required />
      <input type="password" name="password" placeholder="Password" required />
      <button type="submit">Sign In</button>
    </form>
  );
}
```

### Server Action with useFormState

```tsx
// components/auth/sign-in-form-server.tsx
"use client";

import { useFormState, useFormStatus } from "react-dom";
import { signIn } from "@/app/actions/auth";

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? "Signing in..." : "Sign In"}
    </button>
  );
}

export function SignInFormServer() {
  const [state, formAction] = useFormState(signIn, { success: false });

  return (
    <form action={formAction}>
      <input type="email" name="email" placeholder="Email" required />
      <input type="password" name="password" placeholder="Password" required />

      {state.error && <p className="error">{state.error}</p>}

      <SubmitButton />
    </form>
  );
}
```

### Protected Server Components

```tsx
// app/dashboard/page.tsx
import { requireAuth } from "@/app/actions/auth";

export default async function DashboardPage() {
  const session = await requireAuth();

  return (
    <div>
      <h1>Welcome, {session.user.name || session.user.email}!</h1>
    </div>
  );
}
```

### Middleware with Server Actions

```typescript
// middleware.ts
import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  const isAuthPage = request.nextUrl.pathname.startsWith("/login") ||
                     request.nextUrl.pathname.startsWith("/signup");

  const isProtectedPage = request.nextUrl.pathname.startsWith("/dashboard") ||
                          request.nextUrl.pathname.startsWith("/settings");

  // Redirect authenticated users away from auth pages
  if (isAuthPage && session?.user) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Redirect unauthenticated users to login
  if (isProtectedPage && !session?.user) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/settings/:path*", "/login", "/signup"],
};
```

### Usage

```
/auth.serverAction [actionName]
```

**User Input**: $ARGUMENTS

Available actions:
- `signIn` - Sign in with email/password
- `signUp` - Create new account
- `signOut` - Sign out current user
- `requestPasswordReset` - Request password reset email
- `resetPassword` - Reset password with token
- `verifyEmail` - Verify email with token
- `resendVerificationEmail` - Resend verification email
- `getSession` - Get current session
- `requireAuth` - Require authenticated user
- `requireVerifiedEmail` - Require verified email
