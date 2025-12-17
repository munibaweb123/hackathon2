---
description: OAuth provider setup guides for Better Auth
---

## Better Auth: Provider Setup Guides

This skill provides step-by-step setup guides for each OAuth provider.

### Google OAuth Setup

#### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name and click "Create"

#### 2. Configure OAuth Consent Screen

1. Navigate to "APIs & Services" → "OAuth consent screen"
2. Select "External" user type
3. Fill in required fields:
   - App name
   - User support email
   - Developer contact email
4. Add scopes: `email`, `profile`, `openid`
5. Add test users (for testing before verification)

#### 3. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Add authorized redirect URI:
   ```
   https://your-app.com/api/auth/callback/google
   ```
   For development:
   ```
   http://localhost:3000/api/auth/callback/google
   ```
5. Copy Client ID and Client Secret

#### 4. Configuration

```typescript
// lib/auth.ts
google: {
  clientId: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
},
```

```env
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx
```

---

### GitHub OAuth Setup

#### 1. Create OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in:
   - Application name
   - Homepage URL: `https://your-app.com`
   - Authorization callback URL:
     ```
     https://your-app.com/api/auth/callback/github
     ```

#### 2. Get Credentials

1. After creating, click "Generate a new client secret"
2. Copy Client ID and Client Secret immediately (secret shown only once)

#### 3. Configuration

```typescript
// lib/auth.ts
github: {
  clientId: process.env.GITHUB_CLIENT_ID!,
  clientSecret: process.env.GITHUB_CLIENT_SECRET!,
},
```

```env
GITHUB_CLIENT_ID=Iv1.xxxxxxxxxx
GITHUB_CLIENT_SECRET=xxxxxxxxxxxxxxxx
```

#### Additional Scopes

```typescript
github: {
  clientId: process.env.GITHUB_CLIENT_ID!,
  clientSecret: process.env.GITHUB_CLIENT_SECRET!,
  scope: ["user:email", "read:user", "repo"],
},
```

---

### Discord OAuth Setup

#### 1. Create Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Enter application name

#### 2. Configure OAuth2

1. Go to "OAuth2" → "General"
2. Add redirect:
   ```
   https://your-app.com/api/auth/callback/discord
   ```
3. Copy Client ID
4. Click "Reset Secret" to get Client Secret

#### 3. Configuration

```typescript
// lib/auth.ts
discord: {
  clientId: process.env.DISCORD_CLIENT_ID!,
  clientSecret: process.env.DISCORD_CLIENT_SECRET!,
},
```

```env
DISCORD_CLIENT_ID=123456789012345678
DISCORD_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Additional Scopes

```typescript
discord: {
  clientId: process.env.DISCORD_CLIENT_ID!,
  clientSecret: process.env.DISCORD_CLIENT_SECRET!,
  scope: ["identify", "email", "guilds"],
},
```

---

### Apple OAuth Setup

#### 1. Apple Developer Account

1. Go to [Apple Developer](https://developer.apple.com/)
2. Enroll in Apple Developer Program ($99/year)

#### 2. Create App ID

1. Go to "Certificates, Identifiers & Profiles"
2. Click "Identifiers" → "+"
3. Select "App IDs" → "App"
4. Enable "Sign In with Apple"

#### 3. Create Service ID

1. Click "Identifiers" → "+"
2. Select "Services IDs"
3. Configure domains and redirect URLs:
   ```
   https://your-app.com/api/auth/callback/apple
   ```

#### 4. Create Key

1. Go to "Keys" → "+"
2. Enable "Sign In with Apple"
3. Download the key file (.p8)

#### 5. Generate Client Secret

Apple requires a JWT-based client secret:

```typescript
import jwt from "jsonwebtoken";
import fs from "fs";

function generateAppleClientSecret() {
  const privateKey = fs.readFileSync("AuthKey_XXXXX.p8");

  return jwt.sign({}, privateKey, {
    algorithm: "ES256",
    expiresIn: "180d",
    audience: "https://appleid.apple.com",
    issuer: process.env.APPLE_TEAM_ID,
    subject: process.env.APPLE_CLIENT_ID,
    keyid: process.env.APPLE_KEY_ID,
  });
}
```

#### 6. Configuration

```typescript
// lib/auth.ts
apple: {
  clientId: process.env.APPLE_CLIENT_ID!,
  clientSecret: process.env.APPLE_CLIENT_SECRET!,
},
```

```env
APPLE_CLIENT_ID=com.yourapp.auth
APPLE_TEAM_ID=XXXXXXXXXX
APPLE_KEY_ID=XXXXXXXXXX
APPLE_CLIENT_SECRET=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Microsoft/Azure OAuth Setup

#### 1. Register Application

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Configure:
   - Name
   - Supported account types (usually "Accounts in any organizational directory and personal Microsoft accounts")
   - Redirect URI: `https://your-app.com/api/auth/callback/microsoft`

#### 2. Get Credentials

1. Copy "Application (client) ID"
2. Go to "Certificates & secrets" → "New client secret"
3. Copy the secret value

#### 3. Configuration

```typescript
// lib/auth.ts
microsoft: {
  clientId: process.env.MICROSOFT_CLIENT_ID!,
  clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
},
```

```env
MICROSOFT_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MICROSOFT_CLIENT_SECRET=xxxxxx~xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Twitter/X OAuth Setup

#### 1. Create Project

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a project and app
3. Set up OAuth 2.0

#### 2. Configure OAuth 2.0

1. Enable OAuth 2.0
2. Set callback URL:
   ```
   https://your-app.com/api/auth/callback/twitter
   ```
3. Copy Client ID and Client Secret

#### 3. Configuration

```typescript
// lib/auth.ts
twitter: {
  clientId: process.env.TWITTER_CLIENT_ID!,
  clientSecret: process.env.TWITTER_CLIENT_SECRET!,
},
```

```env
TWITTER_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Facebook OAuth Setup

#### 1. Create App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "Create App"
3. Select "Consumer" or "Business" type

#### 2. Add Facebook Login

1. Add "Facebook Login" product
2. Configure Valid OAuth Redirect URIs:
   ```
   https://your-app.com/api/auth/callback/facebook
   ```

#### 3. Get Credentials

1. Go to "Settings" → "Basic"
2. Copy App ID and App Secret

#### 4. Configuration

```typescript
// lib/auth.ts
facebook: {
  clientId: process.env.FACEBOOK_CLIENT_ID!,
  clientSecret: process.env.FACEBOOK_CLIENT_SECRET!,
},
```

```env
FACEBOOK_CLIENT_ID=123456789012345
FACEBOOK_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Environment Variables Template

```env
# OAuth Providers

# Google
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# GitHub
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Discord
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=

# Apple
APPLE_CLIENT_ID=
APPLE_CLIENT_SECRET=
APPLE_TEAM_ID=
APPLE_KEY_ID=

# Microsoft
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

# Twitter
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=

# Facebook
FACEBOOK_CLIENT_ID=
FACEBOOK_CLIENT_SECRET=

# LinkedIn
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
```

### Common Issues

#### Redirect URI Mismatch

Ensure your callback URL exactly matches:
- Protocol (http vs https)
- Domain (including www or not)
- Path (/api/auth/callback/{provider})
- No trailing slash

#### Development vs Production

```typescript
// Use environment-based redirect
const baseURL = process.env.NODE_ENV === "production"
  ? "https://your-app.com"
  : "http://localhost:3000";

// Add both URLs to provider console
```

### Usage

```
/auth.social.providers [provider]
```

**User Input**: $ARGUMENTS

Available providers:
- `google` - Google setup guide
- `github` - GitHub setup guide
- `discord` - Discord setup guide
- `apple` - Apple setup guide
- `microsoft` - Microsoft/Azure setup guide
- `twitter` - Twitter/X setup guide
- `facebook` - Facebook setup guide
