---
description: Setup Magic Link authentication with Better Auth
---

## Better Auth: Magic Link Setup

This skill covers the complete setup for Magic Link (passwordless) authentication with Better Auth.

### Overview

Magic Link authentication allows users to sign in by clicking a link sent to their email, eliminating the need for passwords.

### Prerequisites

- Better Auth installed
- Email provider configured (Resend, SendGrid, Nodemailer, etc.)
- Database adapter configured

### Server Setup

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { magicLink } from "better-auth/plugins";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "./prisma";

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, token, url }, request) => {
        // Send email with magic link
        await sendEmail({
          to: email,
          subject: "Sign in to My App",
          html: `
            <h1>Sign in to My App</h1>
            <p>Click the link below to sign in:</p>
            <a href="${url}">Sign In</a>
            <p>This link expires in 5 minutes.</p>
            <p>If you didn't request this, you can ignore this email.</p>
          `,
        });
      },
      expiresIn: 60 * 5, // 5 minutes (default)
      disableSignUp: false, // Allow new users to sign up via magic link
    }),
  ],
});
```

### Client Setup

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";
import { magicLinkClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [magicLinkClient()],
});
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sendMagicLink` | Function | Required | Async function to send the magic link email |
| `expiresIn` | Number | 300 | Token expiration in seconds (5 minutes default) |
| `disableSignUp` | Boolean | false | If true, only existing users can use magic link |

### sendMagicLink Parameters

```typescript
interface MagicLinkParams {
  email: string;      // User's email address
  token: string;      // The magic link token
  url: string;        // Complete magic link URL
}

// The function also receives the request object
sendMagicLink: async (params: MagicLinkParams, request: Request) => {
  // Send email logic
}
```

### With Resend

```typescript
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export const auth = betterAuth({
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        await resend.emails.send({
          from: "noreply@myapp.com",
          to: email,
          subject: "Sign in to My App",
          html: `
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
              <h1 style="color: #333;">Sign in to My App</h1>
              <p>Click the button below to sign in:</p>
              <a href="${url}" style="
                display: inline-block;
                background: #0070f3;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                margin: 16px 0;
              ">Sign In</a>
              <p style="color: #666; font-size: 14px;">
                This link expires in 5 minutes.
              </p>
              <p style="color: #999; font-size: 12px;">
                If you didn't request this, you can safely ignore this email.
              </p>
            </div>
          `,
        });
      },
    }),
  ],
});
```

### With Nodemailer

```typescript
import nodemailer from "nodemailer";

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT),
  secure: process.env.SMTP_SECURE === "true",
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

export const auth = betterAuth({
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        await transporter.sendMail({
          from: '"My App" <noreply@myapp.com>',
          to: email,
          subject: "Sign in to My App",
          html: `<a href="${url}">Click here to sign in</a>`,
          text: `Sign in to My App: ${url}`,
        });
      },
    }),
  ],
});
```

### With SendGrid

```typescript
import sgMail from "@sendgrid/mail";

sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

export const auth = betterAuth({
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        await sgMail.send({
          to: email,
          from: "noreply@myapp.com",
          subject: "Sign in to My App",
          html: `<a href="${url}">Sign in</a>`,
          text: `Sign in to My App: ${url}`,
        });
      },
    }),
  ],
});
```

### Disable Sign Up (Existing Users Only)

```typescript
magicLink({
  sendMagicLink: async ({ email, url }) => {
    await sendEmail({
      to: email,
      subject: "Sign in",
      html: `<a href="${url}">Sign in</a>`,
    });
  },
  disableSignUp: true, // Only existing users can use magic link
})
```

### Custom Expiration Time

```typescript
magicLink({
  sendMagicLink: async ({ email, url }) => {
    await sendEmail({ to: email, subject: "Sign in", html: `<a href="${url}">Sign in</a>` });
  },
  expiresIn: 60 * 15, // 15 minutes
})
```

### Combine with Password Auth

```typescript
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
  },
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        await sendEmail({ to: email, subject: "Sign in", html: `<a href="${url}">Sign in</a>` });
      },
    }),
  ],
});
```

### Environment Variables

```bash
# .env
RESEND_API_KEY=re_xxxxx
# or
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user
SMTP_PASS=password
SMTP_SECURE=false
# or
SENDGRID_API_KEY=SG.xxxxx
```

### API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### Usage

```
/auth.magicLink.setup [provider]
```

**User Input**: $ARGUMENTS

Available providers:
- `resend` - Setup with Resend
- `nodemailer` - Setup with Nodemailer
- `sendgrid` - Setup with SendGrid
