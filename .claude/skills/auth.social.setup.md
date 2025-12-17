---
description: Setup Social OAuth authentication with Better Auth
---

## Better Auth: Social OAuth Setup

This skill covers the complete setup for Social OAuth (Google, GitHub, Discord, Apple, etc.) authentication with Better Auth.

### Overview

Social OAuth allows users to sign in using their existing accounts from providers like Google, GitHub, Discord, and more.

### Prerequisites

- Better Auth installed
- OAuth credentials from providers
- Database adapter configured

### Server Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "./prisma";

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
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
    apple: {
      clientId: process.env.APPLE_CLIENT_ID!,
      clientSecret: process.env.APPLE_CLIENT_SECRET!,
    },
  },
});
```

### Available Providers

| Provider | Key | Documentation |
|----------|-----|---------------|
| Google | `google` | [Google Cloud Console](https://console.cloud.google.com/) |
| GitHub | `github` | [GitHub Developer Settings](https://github.com/settings/developers) |
| Discord | `discord` | [Discord Developer Portal](https://discord.com/developers/applications) |
| Apple | `apple` | [Apple Developer](https://developer.apple.com/) |
| Microsoft | `microsoft` | [Azure Portal](https://portal.azure.com/) |
| Twitter/X | `twitter` | [Twitter Developer Portal](https://developer.twitter.com/) |
| Facebook | `facebook` | [Facebook Developers](https://developers.facebook.com/) |
| LinkedIn | `linkedin` | [LinkedIn Developers](https://www.linkedin.com/developers/) |

### Single Provider Setup

```typescript
// Google only
export const auth = betterAuth({
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
});
```

### Multiple Providers

```typescript
export const auth = betterAuth({
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
    twitter: {
      clientId: process.env.TWITTER_CLIENT_ID!,
      clientSecret: process.env.TWITTER_CLIENT_SECRET!,
    },
  },
});
```

### Custom Redirect URI

```typescript
export const auth = betterAuth({
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      redirectURI: "https://myapp.com/api/auth/callback/github",
    },
  },
});
```

### Request Additional Scopes

#### Google Scopes

```typescript
google: {
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  scope: [
    "email",
    "profile",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
  ],
},
```

#### GitHub Scopes

```typescript
github: {
  clientId: process.env.GITHUB_CLIENT_ID!,
  clientSecret: process.env.GITHUB_CLIENT_SECRET!,
  scope: [
    "user:email",
    "read:user",
    "repo",
    "read:org",
  ],
},
```

#### Discord Scopes

```typescript
discord: {
  clientId: process.env.DISCORD_CLIENT_ID!,
  clientSecret: process.env.DISCORD_CLIENT_SECRET!,
  scope: [
    "identify",
    "email",
    "guilds",
  ],
},
```

### Auto Link Accounts

Automatically link accounts with matching emails:

```typescript
export const auth = betterAuth({
  account: {
    accountLinking: {
      enabled: true,
      trustedProviders: ["google", "github"],
    },
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
});
```

### Environment Variables

```bash
# .env

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Discord OAuth
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret

# Apple OAuth
APPLE_CLIENT_ID=com.yourapp.auth
APPLE_CLIENT_SECRET=your-apple-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# Twitter/X OAuth
TWITTER_CLIENT_ID=your-twitter-client-id
TWITTER_CLIENT_SECRET=your-twitter-client-secret
```

### API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### Client Configuration

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
});
```

### Callback URL Pattern

The default callback URL pattern is:
```
https://your-app.com/api/auth/callback/{provider}
```

Examples:
- Google: `https://your-app.com/api/auth/callback/google`
- GitHub: `https://your-app.com/api/auth/callback/github`
- Discord: `https://your-app.com/api/auth/callback/discord`

### Combined with Email/Password

```typescript
export const auth = betterAuth({
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
});
```

### Usage

```
/auth.social.setup [provider]
```

**User Input**: $ARGUMENTS

Available providers:
- `google` - Google OAuth setup
- `github` - GitHub OAuth setup
- `discord` - Discord OAuth setup
- `apple` - Apple OAuth setup
- `all` - All providers configuration
