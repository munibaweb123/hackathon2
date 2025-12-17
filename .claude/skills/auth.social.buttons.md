---
description: React button components for Social OAuth authentication
---

## Better Auth: Social Button Components

This skill provides ready-to-use React button components for Social OAuth authentication.

### Prerequisites

- Auth client configured (`@/lib/auth-client`)
- React 18+
- Tailwind CSS (optional, for styling)

### Basic Social Buttons

```tsx
// components/auth/social-buttons.tsx
"use client";

import { authClient } from "@/lib/auth-client";

export function SocialButtons() {
  const handleSocialSignIn = async (provider: string) => {
    await authClient.signIn.social({
      provider: provider as "google" | "github" | "discord",
      callbackURL: "/dashboard",
    });
  };

  return (
    <div className="flex flex-col gap-3">
      <button
        onClick={() => handleSocialSignIn("google")}
        className="flex items-center justify-center gap-3 px-4 py-2.5 border rounded-lg hover:bg-gray-50 transition"
      >
        <GoogleIcon />
        <span>Continue with Google</span>
      </button>

      <button
        onClick={() => handleSocialSignIn("github")}
        className="flex items-center justify-center gap-3 px-4 py-2.5 border rounded-lg hover:bg-gray-50 transition"
      >
        <GitHubIcon />
        <span>Continue with GitHub</span>
      </button>

      <button
        onClick={() => handleSocialSignIn("discord")}
        className="flex items-center justify-center gap-3 px-4 py-2.5 border rounded-lg hover:bg-gray-50 transition"
      >
        <DiscordIcon />
        <span>Continue with Discord</span>
      </button>
    </div>
  );
}
```

### Provider Icons

```tsx
// components/icons/social-icons.tsx
export function GoogleIcon({ className = "w-5 h-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  );
}

export function GitHubIcon({ className = "w-5 h-5" }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path
        fillRule="evenodd"
        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function DiscordIcon({ className = "w-5 h-5" }) {
  return (
    <svg className={className} fill="#5865F2" viewBox="0 0 24 24">
      <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
    </svg>
  );
}

export function AppleIcon({ className = "w-5 h-5" }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701z" />
    </svg>
  );
}

export function TwitterIcon({ className = "w-5 h-5" }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}
```

### Styled Social Buttons with Loading

```tsx
// components/auth/social-buttons-styled.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { GoogleIcon, GitHubIcon, DiscordIcon, AppleIcon } from "./icons";

type Provider = "google" | "github" | "discord" | "apple";

interface SocialButtonProps {
  provider: Provider;
  children: React.ReactNode;
  icon: React.ReactNode;
  className?: string;
}

function SocialButton({ provider, children, icon, className }: SocialButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    await authClient.signIn.social({
      provider,
      callbackURL: "/dashboard",
    });
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`
        flex items-center justify-center gap-3 w-full px-4 py-3
        border border-gray-300 rounded-lg font-medium
        hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed
        transition-colors ${className}
      `}
    >
      {loading ? (
        <div className="w-5 h-5 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
      ) : (
        icon
      )}
      <span>{loading ? "Connecting..." : children}</span>
    </button>
  );
}

export function StyledSocialButtons() {
  return (
    <div className="space-y-3">
      <SocialButton provider="google" icon={<GoogleIcon />}>
        Continue with Google
      </SocialButton>

      <SocialButton
        provider="github"
        icon={<GitHubIcon />}
        className="bg-gray-900 text-white border-gray-900 hover:bg-gray-800"
      >
        Continue with GitHub
      </SocialButton>

      <SocialButton
        provider="discord"
        icon={<DiscordIcon />}
        className="bg-[#5865F2] text-white border-[#5865F2] hover:bg-[#4752C4]"
      >
        Continue with Discord
      </SocialButton>

      <SocialButton
        provider="apple"
        icon={<AppleIcon />}
        className="bg-black text-white border-black hover:bg-gray-900"
      >
        Continue with Apple
      </SocialButton>
    </div>
  );
}
```

### Compact Icon-Only Buttons

```tsx
// components/auth/social-icons-row.tsx
"use client";

import { authClient } from "@/lib/auth-client";
import { GoogleIcon, GitHubIcon, DiscordIcon } from "./icons";

export function SocialIconsRow() {
  const signIn = (provider: string) => {
    authClient.signIn.social({
      provider: provider as "google" | "github" | "discord",
      callbackURL: "/dashboard",
    });
  };

  return (
    <div className="flex justify-center gap-4">
      <button
        onClick={() => signIn("google")}
        className="p-3 border rounded-full hover:bg-gray-50 transition"
        aria-label="Sign in with Google"
      >
        <GoogleIcon className="w-6 h-6" />
      </button>

      <button
        onClick={() => signIn("github")}
        className="p-3 border rounded-full hover:bg-gray-50 transition"
        aria-label="Sign in with GitHub"
      >
        <GitHubIcon className="w-6 h-6" />
      </button>

      <button
        onClick={() => signIn("discord")}
        className="p-3 border rounded-full hover:bg-gray-50 transition"
        aria-label="Sign in with Discord"
      >
        <DiscordIcon className="w-6 h-6" />
      </button>
    </div>
  );
}
```

### With Divider (Combined Form)

```tsx
// components/auth/auth-form.tsx
"use client";

import { SocialButtons } from "./social-buttons";
import { SignInForm } from "./sign-in-form";

export function AuthForm() {
  return (
    <div className="w-full max-w-md mx-auto space-y-6">
      <SocialButtons />

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-4 bg-white text-gray-500">or continue with</span>
        </div>
      </div>

      <SignInForm />
    </div>
  );
}
```

### Dynamic Provider List

```tsx
// components/auth/dynamic-social-buttons.tsx
"use client";

import { authClient } from "@/lib/auth-client";
import { GoogleIcon, GitHubIcon, DiscordIcon, AppleIcon } from "./icons";

const providers = [
  { id: "google", name: "Google", icon: GoogleIcon, bgClass: "" },
  { id: "github", name: "GitHub", icon: GitHubIcon, bgClass: "bg-gray-900 text-white" },
  { id: "discord", name: "Discord", icon: DiscordIcon, bgClass: "bg-[#5865F2] text-white" },
  { id: "apple", name: "Apple", icon: AppleIcon, bgClass: "bg-black text-white" },
] as const;

interface DynamicSocialButtonsProps {
  enabledProviders?: typeof providers[number]["id"][];
}

export function DynamicSocialButtons({
  enabledProviders = ["google", "github"],
}: DynamicSocialButtonsProps) {
  const filteredProviders = providers.filter((p) =>
    enabledProviders.includes(p.id)
  );

  const handleSignIn = (provider: string) => {
    authClient.signIn.social({
      provider: provider as "google" | "github" | "discord" | "apple",
      callbackURL: "/dashboard",
    });
  };

  return (
    <div className="space-y-3">
      {filteredProviders.map(({ id, name, icon: Icon, bgClass }) => (
        <button
          key={id}
          onClick={() => handleSignIn(id)}
          className={`
            flex items-center justify-center gap-3 w-full px-4 py-3
            border rounded-lg font-medium transition-colors
            hover:opacity-90 ${bgClass}
          `}
        >
          <Icon className="w-5 h-5" />
          <span>Continue with {name}</span>
        </button>
      ))}
    </div>
  );
}
```

### Usage in Pages

```tsx
// app/(auth)/login/page.tsx
import { StyledSocialButtons } from "@/components/auth/social-buttons-styled";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-2xl font-bold text-center mb-6">Sign In</h1>
        <StyledSocialButtons />
      </div>
    </div>
  );
}
```

### Usage

```
/auth.social.buttons [variant]
```

**User Input**: $ARGUMENTS

Available variants:
- `basic` - Basic text buttons
- `styled` - Styled buttons with loading
- `icons` - Icon-only compact buttons
- `dynamic` - Configurable provider list
