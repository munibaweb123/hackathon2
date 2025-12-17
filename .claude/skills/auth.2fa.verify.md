---
description: 2FA verification during sign-in with Better Auth
---

## Better Auth: 2FA Verification

This skill covers the 2FA verification flow during sign-in, including TOTP and backup code verification.

### Overview

When a user with 2FA enabled signs in:
1. User enters email/password (or uses OAuth)
2. If valid, the `onTwoFactorRedirect` callback is triggered
3. User is redirected to 2FA verification page
4. User enters TOTP code or backup code
5. Session is created

### Sign In with 2FA Flow

```typescript
// Normal sign in - triggers onTwoFactorRedirect if 2FA is enabled
const { data, error } = await authClient.signIn.email({
  email: "user@example.com",
  password: "password",
});

// If 2FA is required, onTwoFactorRedirect is called automatically
// On the /2fa page, verify the TOTP:
const { error: verifyError } = await authClient.twoFactor.verifyTotp({
  code: "123456",
});

if (!verifyError) {
  // Redirect to dashboard
  window.location.href = "/dashboard";
}
```

### 2FA Verification Page Component

```tsx
// app/2fa/page.tsx
"use client";

import { TwoFactorVerify } from "@/components/auth/two-factor-verify";

export default function TwoFactorPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8">
        <TwoFactorVerify />
      </div>
    </div>
  );
}
```

### Verification Component

```tsx
// components/auth/two-factor-verify.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

export function TwoFactorVerify() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [useBackup, setUseBackup] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    inputRef.current?.focus();
  }, [useBackup]);

  const handleVerify = async (e?: React.FormEvent) => {
    e?.preventDefault();

    if (!code.trim()) {
      setError("Please enter a code");
      return;
    }

    setLoading(true);
    setError("");

    const { error } = useBackup
      ? await authClient.twoFactor.verifyBackupCode({ code })
      : await authClient.twoFactor.verifyTotp({ code });

    setLoading(false);

    if (error) {
      setError(useBackup ? "Invalid backup code" : "Invalid code. Please try again.");
      setCode("");
      inputRef.current?.focus();
      return;
    }

    // Get redirect destination
    const redirectTo = sessionStorage.getItem("redirectAfter2FA") || "/dashboard";
    sessionStorage.removeItem("redirectAfter2FA");
    router.push(redirectTo);
  };

  const toggleMode = () => {
    setUseBackup(!useBackup);
    setCode("");
    setError("");
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold">Two-Factor Authentication</h2>
        <p className="text-gray-600 mt-2">
          {useBackup
            ? "Enter one of your backup codes"
            : "Enter the 6-digit code from your authenticator app"}
        </p>
      </div>

      <form onSubmit={handleVerify} className="space-y-4">
        <div>
          <input
            ref={inputRef}
            type="text"
            value={code}
            onChange={(e) => {
              const value = useBackup
                ? e.target.value
                : e.target.value.replace(/\D/g, "").slice(0, 6);
              setCode(value);
            }}
            placeholder={useBackup ? "Backup code" : "000000"}
            className={`w-full px-4 py-3 border rounded-lg text-center font-mono ${
              useBackup ? "text-lg" : "text-2xl tracking-widest"
            }`}
            autoComplete="one-time-code"
            autoFocus
          />
        </div>

        {error && (
          <div className="p-3 bg-red-50 text-red-600 rounded-md text-sm text-center">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !code.trim()}
          className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {loading ? "Verifying..." : "Verify"}
        </button>
      </form>

      <div className="text-center">
        <button
          onClick={toggleMode}
          className="text-sm text-blue-600 hover:underline"
        >
          {useBackup ? "Use authenticator app instead" : "Use a backup code"}
        </button>
      </div>

      <div className="text-center text-sm text-gray-500">
        <p>
          Having trouble?{" "}
          <a href="/support" className="text-blue-600 hover:underline">
            Contact support
          </a>
        </p>
      </div>
    </div>
  );
}
```

### OTP Input Component (6 Separate Boxes)

```tsx
// components/auth/otp-input.tsx
"use client";

import { useRef, useState, KeyboardEvent, ClipboardEvent } from "react";

interface OTPInputProps {
  length?: number;
  onComplete: (code: string) => void;
  disabled?: boolean;
}

export function OTPInput({ length = 6, onComplete, disabled }: OTPInputProps) {
  const [values, setValues] = useState<string[]>(Array(length).fill(""));
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;

    const newValues = [...values];
    newValues[index] = value.slice(-1);
    setValues(newValues);

    // Auto-focus next input
    if (value && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }

    // Check if complete
    const code = newValues.join("");
    if (code.length === length) {
      onComplete(code);
    }
  };

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !values[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, length);

    if (pasted.length === length) {
      const newValues = pasted.split("");
      setValues(newValues);
      onComplete(pasted);
    }
  };

  return (
    <div className="flex gap-2 justify-center">
      {values.map((value, index) => (
        <input
          key={index}
          ref={(el) => (inputRefs.current[index] = el)}
          type="text"
          inputMode="numeric"
          value={value}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={handlePaste}
          disabled={disabled}
          className="w-12 h-14 text-center text-2xl font-bold border-2 rounded-lg focus:border-blue-500 focus:outline-none disabled:opacity-50"
          maxLength={1}
        />
      ))}
    </div>
  );
}
```

### Using OTP Input Component

```tsx
// components/auth/two-factor-verify-otp.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { OTPInput } from "./otp-input";

export function TwoFactorVerifyOTP() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleComplete = async (code: string) => {
    setLoading(true);
    setError("");

    const { error } = await authClient.twoFactor.verifyTotp({ code });

    setLoading(false);

    if (error) {
      setError("Invalid code");
      return;
    }

    router.push("/dashboard");
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-center">Enter Verification Code</h2>

      <OTPInput onComplete={handleComplete} disabled={loading} />

      {error && (
        <p className="text-red-500 text-center">{error}</p>
      )}

      {loading && (
        <p className="text-center text-gray-500">Verifying...</p>
      )}
    </div>
  );
}
```

### Trust Device Option

Skip 2FA on trusted devices:

```tsx
// components/auth/two-factor-with-trust.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

export function TwoFactorWithTrust() {
  const [code, setCode] = useState("");
  const [trustDevice, setTrustDevice] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleVerify = async () => {
    setLoading(true);
    setError("");

    const { error } = await authClient.twoFactor.verifyTotp({
      code,
      trustDevice, // Skip 2FA on this device for configured period
    });

    setLoading(false);

    if (error) {
      setError("Invalid code");
      return;
    }

    router.push("/dashboard");
  };

  return (
    <div className="space-y-4">
      <input
        type="text"
        value={code}
        onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
        placeholder="Enter 6-digit code"
        className="w-full px-4 py-3 border rounded-lg text-center text-2xl"
      />

      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={trustDevice}
          onChange={(e) => setTrustDevice(e.target.checked)}
        />
        <span className="text-sm">Trust this device for 30 days</span>
      </label>

      {error && <p className="text-red-500">{error}</p>}

      <button
        onClick={handleVerify}
        disabled={loading || code.length !== 6}
        className="w-full py-3 bg-blue-600 text-white rounded-lg disabled:opacity-50"
      >
        {loading ? "Verifying..." : "Verify"}
      </button>
    </div>
  );
}
```

### React Hook for Verification

```typescript
// hooks/useTwoFactorVerify.ts
import { authClient } from "@/lib/auth-client";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";

interface UseTwoFactorVerifyOptions {
  redirectTo?: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function useTwoFactorVerify(options: UseTwoFactorVerifyOptions = {}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const verifyTotp = useCallback(
    async (code: string, trustDevice?: boolean) => {
      setLoading(true);
      setError(null);

      const { error } = await authClient.twoFactor.verifyTotp({
        code,
        trustDevice,
      });

      setLoading(false);

      if (error) {
        const message = "Invalid code. Please try again.";
        setError(message);
        options.onError?.(message);
        return false;
      }

      options.onSuccess?.();
      const redirectTo =
        options.redirectTo ||
        sessionStorage.getItem("redirectAfter2FA") ||
        "/dashboard";
      sessionStorage.removeItem("redirectAfter2FA");
      router.push(redirectTo);
      return true;
    },
    [router, options]
  );

  const verifyBackupCode = useCallback(
    async (code: string) => {
      setLoading(true);
      setError(null);

      const { error } = await authClient.twoFactor.verifyBackupCode({ code });

      setLoading(false);

      if (error) {
        const message = "Invalid backup code.";
        setError(message);
        options.onError?.(message);
        return false;
      }

      options.onSuccess?.();
      router.push(options.redirectTo || "/dashboard");
      return true;
    },
    [router, options]
  );

  return {
    verifyTotp,
    verifyBackupCode,
    loading,
    error,
    clearError: () => setError(null),
  };
}
```

### Usage

```
/auth.2fa.verify [variant]
```

**User Input**: $ARGUMENTS

Available variants:
- `basic` - Basic verification
- `component` - Full page component
- `otp` - 6-box OTP input
- `trust` - With trust device option
- `hook` - React hook implementation
