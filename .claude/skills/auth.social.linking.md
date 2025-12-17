---
description: Account linking for Social OAuth with Better Auth
---

## Better Auth: Account Linking

This skill covers linking, listing, and unlinking social accounts with Better Auth.

### Overview

Account linking allows users to connect multiple OAuth providers to a single account, enabling them to sign in with any linked provider.

### Link Additional Account

```typescript
// Link GitHub to existing account
await authClient.linkSocial({
  provider: "github",
  callbackURL: "/settings/accounts",
});

// Link Google
await authClient.linkSocial({
  provider: "google",
  callbackURL: "/settings/accounts",
});

// Link Discord
await authClient.linkSocial({
  provider: "discord",
  callbackURL: "/settings/accounts",
});
```

### List Linked Accounts

```typescript
const { data: accounts } = await authClient.listAccounts();

if (accounts) {
  accounts.forEach((account) => {
    console.log(`Provider: ${account.provider}`);
    console.log(`Provider ID: ${account.providerId}`);
    console.log(`Account ID: ${account.id}`);
  });
}
```

### Unlink Account

```typescript
await authClient.unlinkAccount({
  accountId: "acc_123456",
});
```

### React Hook Implementation

```typescript
// hooks/useLinkedAccounts.ts
import { authClient } from "@/lib/auth-client";
import { useState, useEffect, useCallback } from "react";

interface Account {
  id: string;
  provider: string;
  providerId: string;
  createdAt?: Date;
}

type SocialProvider = "google" | "github" | "discord" | "apple" | "twitter";

export function useLinkedAccounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Fetch accounts
  const fetchAccounts = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const { data } = await authClient.listAccounts();
      setAccounts(data || []);
    } catch (err) {
      setError("Failed to load accounts");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  // Check if provider is linked
  const hasProvider = useCallback(
    (provider: string) => accounts.some((a) => a.provider === provider),
    [accounts]
  );

  // Get account by provider
  const getAccount = useCallback(
    (provider: string) => accounts.find((a) => a.provider === provider),
    [accounts]
  );

  // Link account
  const linkAccount = useCallback(async (provider: SocialProvider) => {
    setActionLoading(provider);
    try {
      await authClient.linkSocial({
        provider,
        callbackURL: window.location.href,
      });
    } catch (err) {
      setError(`Failed to link ${provider}`);
      setActionLoading(null);
    }
  }, []);

  // Unlink account
  const unlinkAccount = useCallback(
    async (accountId: string, provider: string) => {
      setActionLoading(provider);
      try {
        await authClient.unlinkAccount({ accountId });
        setAccounts((prev) => prev.filter((a) => a.id !== accountId));
      } catch (err) {
        setError("Failed to unlink account");
      } finally {
        setActionLoading(null);
      }
    },
    []
  );

  return {
    accounts,
    loading,
    error,
    actionLoading,
    hasProvider,
    getAccount,
    linkAccount,
    unlinkAccount,
    refresh: fetchAccounts,
  };
}
```

### Account Linking Settings Page

```tsx
// components/settings/linked-accounts.tsx
"use client";

import { useLinkedAccounts } from "@/hooks/useLinkedAccounts";
import { GoogleIcon, GitHubIcon, DiscordIcon } from "@/components/icons";

const providers = [
  { id: "google", name: "Google", icon: GoogleIcon },
  { id: "github", name: "GitHub", icon: GitHubIcon },
  { id: "discord", name: "Discord", icon: DiscordIcon },
] as const;

export function LinkedAccounts() {
  const {
    accounts,
    loading,
    error,
    actionLoading,
    hasProvider,
    getAccount,
    linkAccount,
    unlinkAccount,
  } = useLinkedAccounts();

  if (loading) {
    return <div className="animate-pulse">Loading accounts...</div>;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Linked Accounts</h2>
      <p className="text-gray-600 text-sm">
        Connect your accounts to enable additional sign-in options.
      </p>

      {error && (
        <div className="p-3 bg-red-50 text-red-600 rounded-md text-sm">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {providers.map(({ id, name, icon: Icon }) => {
          const isLinked = hasProvider(id);
          const account = getAccount(id);
          const isLoading = actionLoading === id;

          return (
            <div
              key={id}
              className="flex items-center justify-between p-4 border rounded-lg"
            >
              <div className="flex items-center gap-3">
                <Icon className="w-6 h-6" />
                <div>
                  <p className="font-medium">{name}</p>
                  {isLinked && account && (
                    <p className="text-sm text-gray-500">
                      Connected as {account.providerId}
                    </p>
                  )}
                </div>
              </div>

              {isLinked ? (
                <button
                  onClick={() => unlinkAccount(account!.id, id)}
                  disabled={isLoading || accounts.length <= 1}
                  className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                  title={
                    accounts.length <= 1
                      ? "Cannot unlink last account"
                      : "Unlink account"
                  }
                >
                  {isLoading ? "Unlinking..." : "Unlink"}
                </button>
              ) : (
                <button
                  onClick={() => linkAccount(id as any)}
                  disabled={isLoading}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {isLoading ? "Connecting..." : "Connect"}
                </button>
              )}
            </div>
          );
        })}
      </div>

      {accounts.length === 1 && (
        <p className="text-sm text-amber-600 bg-amber-50 p-3 rounded-md">
          You must have at least one linked account. Add another account before
          unlinking this one.
        </p>
      )}
    </div>
  );
}
```

### Compact Account Link Cards

```tsx
// components/settings/account-link-cards.tsx
"use client";

import { useLinkedAccounts } from "@/hooks/useLinkedAccounts";

const providerColors: Record<string, string> = {
  google: "border-l-red-500",
  github: "border-l-gray-800",
  discord: "border-l-indigo-500",
  apple: "border-l-black",
};

export function AccountLinkCards() {
  const { accounts, loading, unlinkAccount, actionLoading } = useLinkedAccounts();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (accounts.length === 0) {
    return (
      <p className="text-gray-500">No accounts linked yet.</p>
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {accounts.map((account) => (
        <div
          key={account.id}
          className={`p-4 border-l-4 bg-gray-50 rounded-r-lg ${
            providerColors[account.provider] || "border-l-gray-400"
          }`}
        >
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium capitalize">{account.provider}</p>
              <p className="text-sm text-gray-500">{account.providerId}</p>
            </div>
            <button
              onClick={() => unlinkAccount(account.id, account.provider)}
              disabled={actionLoading === account.provider || accounts.length <= 1}
              className="text-xs text-red-500 hover:underline disabled:opacity-50"
            >
              Remove
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Auto Link Configuration

Enable automatic account linking for trusted providers:

```typescript
// lib/auth.ts (server)
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

### Access OAuth Tokens

```typescript
// Access stored tokens from linked account
import { db } from "@/db";

async function getGitHubToken(userId: string) {
  const account = await db.query.account.findFirst({
    where: (account, { and, eq }) =>
      and(
        eq(account.userId, userId),
        eq(account.provider, "github")
      ),
  });

  return account?.accessToken;
}

// Use token to call provider API
async function getGitHubRepos(userId: string) {
  const token = await getGitHubToken(userId);

  if (!token) {
    throw new Error("GitHub not linked");
  }

  const response = await fetch("https://api.github.com/user/repos", {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github.v3+json",
    },
  });

  return response.json();
}
```

### Settings Page Integration

```tsx
// app/settings/accounts/page.tsx
import { LinkedAccounts } from "@/components/settings/linked-accounts";

export default function AccountsSettingsPage() {
  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Account Settings</h1>

      <section className="bg-white rounded-lg shadow p-6">
        <LinkedAccounts />
      </section>
    </div>
  );
}
```

### TypeScript Types

```typescript
interface LinkedAccount {
  id: string;
  userId: string;
  provider: string;
  providerId: string;
  accessToken?: string;
  refreshToken?: string;
  accessTokenExpiresAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

type SocialProvider =
  | "google"
  | "github"
  | "discord"
  | "apple"
  | "twitter"
  | "microsoft";

interface LinkSocialParams {
  provider: SocialProvider;
  callbackURL?: string;
}

interface UnlinkAccountParams {
  accountId: string;
}
```

### Usage

```
/auth.social.linking [action]
```

**User Input**: $ARGUMENTS

Available actions:
- `link` - Link account examples
- `list` - List accounts
- `unlink` - Unlink account
- `hook` - React hook implementation
- `component` - Settings page component
