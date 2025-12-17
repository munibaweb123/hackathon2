---
description: Setup Two-Factor Authentication (2FA) with Better Auth
---

## Better Auth: 2FA Setup

This skill covers the complete setup for Two-Factor Authentication (TOTP) with Better Auth.

### Overview

Two-Factor Authentication adds an extra layer of security by requiring users to enter a time-based one-time password (TOTP) from an authenticator app in addition to their password.

### Prerequisites

- Better Auth installed
- Database adapter configured
- QR code library for client (e.g., `qrcode.react`)

### Server Setup

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { twoFactor } from "better-auth/plugins";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "./prisma";

export const auth = betterAuth({
  appName: "My App", // Used as TOTP issuer
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  plugins: [
    twoFactor({
      issuer: "My App", // Optional, defaults to appName
      otpLength: 6, // Default: 6 digits
      period: 30, // Default: 30 seconds
    }),
  ],
});
```

### Client Setup

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";
import { twoFactorClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [
    twoFactorClient({
      onTwoFactorRedirect() {
        // Called when 2FA verification is required after sign-in
        window.location.href = "/2fa";
      },
    }),
  ],
});
```

### Configuration Options

```typescript
twoFactor({
  // TOTP settings
  issuer: "My App",           // Displayed in authenticator app
  otpLength: 6,               // Code length (default: 6)
  period: 30,                 // Code validity in seconds (default: 30)

  // Backup codes
  backupCodeLength: 10,       // Length of each backup code
  numberOfBackupCodes: 10,    // Number of backup codes generated

  // Trust device (skip 2FA on trusted devices)
  trustDeviceCookie: {
    name: "trusted_device",
    maxAge: 60 * 60 * 24 * 30, // 30 days
  },

  // Skip verification when first enabling 2FA
  skipVerificationOnEnable: false,
})
```

### Database Migration

After adding the twoFactor plugin, run migrations:

```bash
# Generate migration files
npx @better-auth/cli generate

# Run migrations
npx @better-auth/cli migrate
```

This creates the `twoFactor` table with:
- `id` - Unique identifier
- `userId` - Reference to user
- `secret` - Encrypted TOTP secret
- `backupCodes` - Hashed backup codes

### API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### With Redirect Handling

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";
import { twoFactorClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  plugins: [
    twoFactorClient({
      onTwoFactorRedirect() {
        // Store intended destination for after 2FA
        if (typeof window !== "undefined") {
          sessionStorage.setItem("redirectAfter2FA", window.location.pathname);
          window.location.href = "/2fa";
        }
      },
    }),
  ],
});
```

### Combined with Other Auth Methods

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { twoFactor } from "better-auth/plugins";
import { magicLink } from "better-auth/plugins";

export const auth = betterAuth({
  appName: "My App",
  emailAndPassword: {
    enabled: true,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  plugins: [
    twoFactor({
      issuer: "My App",
    }),
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        // Send magic link email
      },
    }),
  ],
});
```

### Install QR Code Library

```bash
npm install qrcode.react
# or
pnpm add qrcode.react
# or
yarn add qrcode.react
```

### TypeScript Types

```typescript
interface TwoFactorEnableResponse {
  totpURI: string;      // otpauth:// URI for QR code
  backupCodes: string[]; // Backup codes to save
}

interface TwoFactorStatus {
  enabled: boolean;
}

interface TwoFactorVerifyParams {
  code: string;
  trustDevice?: boolean;
}
```

### Environment Variables

```env
# App configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000

# For production
# NEXT_PUBLIC_APP_URL=https://your-app.com
```

### Usage

```
/auth.2fa.setup [option]
```

**User Input**: $ARGUMENTS

Available options:
- `server` - Server configuration
- `client` - Client configuration
- `database` - Database migration
- `full` - Complete setup guide
