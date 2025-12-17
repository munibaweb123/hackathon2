---
description: Better Auth TypeScript/JavaScript authentication library - master reference for Next.js, React, Express projects
---

## Better Auth: Master Reference

Better Auth is a framework-agnostic authentication and authorization library for TypeScript. This skill provides the core setup and references to specific authentication patterns.

### Installation

```bash
# npm
npm install better-auth

# pnpm
pnpm add better-auth

# yarn
yarn add better-auth

# bun
bun add better-auth
```

### Basic Server Setup

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: yourDatabaseAdapter, // See ORM guides below
  emailAndPassword: { enabled: true },
});
```

### Basic Client Setup

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
});
```

### Database Schema Commands

**IMPORTANT**: Always use CLI to generate/migrate schema after configuration changes:

```bash
# See current schema
npx @better-auth/cli generate

# Create/update tables
npx @better-auth/cli migrate
```

### ORM Integration

#### Drizzle

```typescript
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "./db";

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg", // or "mysql", "sqlite"
  }),
});
```

#### Prisma

```typescript
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "./prisma";

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql", // or "mysql", "sqlite"
  }),
});
```

#### Kysely

```typescript
import { betterAuth } from "better-auth";
import { kyselyAdapter } from "better-auth/adapters/kysely";
import { db } from "./db";

export const auth = betterAuth({
  database: kyselyAdapter(db, {
    provider: "pg",
  }),
});
```

#### MongoDB

```typescript
import { betterAuth } from "better-auth";
import { mongodbAdapter } from "better-auth/adapters/mongodb";
import { client } from "./mongodb";

export const auth = betterAuth({
  database: mongodbAdapter(client),
});
```

#### Direct PostgreSQL

```typescript
import { betterAuth } from "better-auth";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: pool,
});
```

---

## Next.js Integration

### API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth.handler);
```

### Next.js 15+ Middleware

```typescript
// middleware.ts
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  if (!session) {
    return NextResponse.redirect(new URL("/sign-in", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/settings/:path*"],
};
```

### Next.js 16 Proxy (Replaces Middleware)

In Next.js 16, `middleware.ts` is replaced by `proxy.ts`:

```typescript
// proxy.ts
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function proxy(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    return NextResponse.redirect(new URL("/sign-in", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
```

Migration command:
```bash
npx @next/codemod@canary middleware-to-proxy .
```

### Server Component

```typescript
// app/dashboard/page.tsx
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/sign-in");
  }

  return <h1>Welcome {session.user.name}</h1>;
}
```

---

## Quick Examples

### Sign In

```typescript
const { data, error } = await authClient.signIn.email({
  email: "user@example.com",
  password: "password",
});

if (error) {
  console.error(error.message);
}
```

### Sign Up

```typescript
const { data, error } = await authClient.signUp.email({
  email: "user@example.com",
  password: "password",
  name: "John Doe",
});
```

### Social OAuth

```typescript
await authClient.signIn.social({
  provider: "google", // or "github", "discord", etc.
  callbackURL: "/dashboard",
});
```

### Sign Out

```typescript
await authClient.signOut();
```

### Get Session

```typescript
// Client-side
const { data: session } = await authClient.getSession();

// Server-side
const session = await auth.api.getSession({
  headers: await headers(),
});
```

---

## Plugins

```typescript
import { betterAuth } from "better-auth";
import {
  twoFactor,
  magicLink,
  jwt,
  organization,
} from "better-auth/plugins";

export const auth = betterAuth({
  database: yourAdapter,
  plugins: [
    twoFactor({
      issuer: "My App",
    }),
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        await sendEmail({ to: email, subject: "Sign in", html: `<a href="${url}">Sign in</a>` });
      },
    }),
    jwt(),
    organization(),
  ],
});
```

**After adding plugins, always run:**
```bash
npx @better-auth/cli migrate
```

### Client Plugin Setup

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";
import { twoFactorClient, magicLinkClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [
    twoFactorClient({
      onTwoFactorRedirect() {
        window.location.href = "/2fa";
      },
    }),
    magicLinkClient(),
  ],
});
```

---

## Full Server Configuration Template

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { twoFactor, magicLink } from "better-auth/plugins";
import { prisma } from "./prisma";

export const auth = betterAuth({
  appName: "My App",
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),

  // Email/Password
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    minPasswordLength: 8,
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

  // Social Providers
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
    discord: {
      clientId: process.env.DISCORD_CLIENT_ID!,
      clientSecret: process.env.DISCORD_CLIENT_SECRET!,
    },
  },

  // Account Linking
  account: {
    accountLinking: {
      enabled: true,
      trustedProviders: ["google", "github"],
    },
  },

  // Plugins
  plugins: [
    twoFactor({
      issuer: "My App",
    }),
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        await sendEmail({
          to: email,
          subject: "Sign in to My App",
          html: `<a href="${url}">Sign In</a>`,
        });
      },
    }),
  ],
});

export type Session = typeof auth.$Infer.Session;
```

---

## Full Client Configuration Template

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";
import { twoFactorClient, magicLinkClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [
    twoFactorClient({
      onTwoFactorRedirect() {
        if (typeof window !== "undefined") {
          sessionStorage.setItem("redirectAfter2FA", window.location.pathname);
          window.location.href = "/2fa";
        }
      },
    }),
    magicLinkClient(),
  ],
});

// Export typed functions
export const {
  signIn,
  signUp,
  signOut,
  getSession,
  useSession,
} = authClient;
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# App URLs
NEXT_PUBLIC_APP_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-random-secret-min-32-chars

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Discord OAuth
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret

# Email (Resend example)
RESEND_API_KEY=re_xxxxx
```

---

## Error Handling

### Client-Side

```typescript
const { data, error } = await authClient.signIn.email({ email, password });

if (error) {
  switch (error.status) {
    case 401:
      console.error("Invalid credentials");
      break;
    case 403:
      console.error("Email not verified");
      break;
    case 429:
      console.error("Too many requests");
      break;
    default:
      console.error(error.message);
  }
}
```

### Server-Side

```typescript
import { APIError } from "better-auth/api";

try {
  await auth.api.signInEmail({
    body: { email, password },
  });
} catch (error) {
  if (error instanceof APIError) {
    console.log(error.message, error.status);
  }
}
```

---

## Related Skills

| Category | Skills |
|----------|--------|
| **Email/Password** | `auth.form`, `auth.hook`, `auth.serverAction`, `auth.signout` |
| **Password Reset** | `auth.forgotPassword`, `auth.resetPassword` |
| **Email Verification** | `auth.emailVerification`, `auth.resendVerification` |
| **Magic Link** | `auth.magicLink.setup`, `auth.magicLink.signIn`, `auth.magicLink.form`, `auth.magicLink.email`, `auth.magicLink.verify` |
| **Social OAuth** | `auth.social.setup`, `auth.social.signIn`, `auth.social.buttons`, `auth.social.linking`, `auth.social.providers` |
| **Two-Factor (2FA)** | `auth.2fa.setup`, `auth.2fa.enable`, `auth.2fa.verify`, `auth.2fa.manage` |
| **Error Handling** | `auth.errorHandling` |

---

## Key CLI Commands

```bash
# Generate schema preview
npx @better-auth/cli generate

# Run database migrations
npx @better-auth/cli migrate

# Next.js 16 middleware migration
npx @next/codemod@canary middleware-to-proxy .
```

---

## Version & Documentation

- **Docs**: https://www.better-auth.com/docs
- **Releases**: https://github.com/better-auth/better-auth/releases

**Always check latest docs before implementation - APIs may change between versions.**

### Usage

```
/auth.betterAuth [topic]
```

**User Input**: $ARGUMENTS

Available topics:
- `setup` - Basic setup guide
- `nextjs` - Next.js integration
- `plugins` - Plugin configuration
- `orm` - ORM/database adapters
- `env` - Environment variables
