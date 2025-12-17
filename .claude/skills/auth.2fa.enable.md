---
description: Enable Two-Factor Authentication for users with Better Auth
---

## Better Auth: Enable 2FA

This skill covers enabling Two-Factor Authentication for users, including QR code generation and verification.

### Overview

The 2FA enable flow:
1. User initiates 2FA setup
2. Generate TOTP secret and backup codes
3. User scans QR code with authenticator app
4. User verifies with a code from the app
5. 2FA is activated

### Enable 2FA (Basic)

```typescript
// Step 1: Generate TOTP secret
const { data, error } = await authClient.twoFactor.enable();

if (error) {
  console.error("Failed to enable 2FA:", error.message);
  return;
}

// data contains:
// - totpURI: otpauth://totp/... (for QR code)
// - backupCodes: ["abc123", "def456", ...] (save these!)

console.log("TOTP URI:", data.totpURI);
console.log("Backup codes:", data.backupCodes);

// Step 2: Show QR code to user (use qrcode.react)
// Step 3: User enters code from authenticator app

// Step 4: Verify and activate
const { error: verifyError } = await authClient.twoFactor.verifyTotp({
  code: "123456", // From authenticator app
});

if (verifyError) {
  console.error("Verification failed");
}
```

### React Enable 2FA Component

```tsx
// components/auth/enable-2fa.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { QRCodeSVG } from "qrcode.react";

type Step = "start" | "scan" | "verify" | "backup" | "done";

export function Enable2FA() {
  const [step, setStep] = useState<Step>("start");
  const [totpURI, setTotpURI] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [backupCodesSaved, setBackupCodesSaved] = useState(false);

  const handleEnable = async () => {
    setLoading(true);
    setError("");

    const { data, error } = await authClient.twoFactor.enable();

    setLoading(false);

    if (error) {
      setError(error.message);
      return;
    }

    setTotpURI(data.totpURI);
    setBackupCodes(data.backupCodes);
    setStep("scan");
  };

  const handleVerify = async () => {
    if (code.length !== 6) {
      setError("Please enter a 6-digit code");
      return;
    }

    setLoading(true);
    setError("");

    const { error } = await authClient.twoFactor.verifyTotp({ code });

    setLoading(false);

    if (error) {
      setError("Invalid code. Please try again.");
      return;
    }

    setStep("backup");
  };

  const copyBackupCodes = () => {
    navigator.clipboard.writeText(backupCodes.join("\n"));
    setBackupCodesSaved(true);
  };

  const downloadBackupCodes = () => {
    const content = `Two-Factor Authentication Backup Codes
======================================
Save these codes in a safe place. Each code can only be used once.

${backupCodes.join("\n")}

Generated: ${new Date().toISOString()}
`;
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "2fa-backup-codes.txt";
    a.click();
    URL.revokeObjectURL(url);
    setBackupCodesSaved(true);
  };

  // Step 1: Start
  if (step === "start") {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Enable Two-Factor Authentication</h3>
        <p className="text-gray-600">
          Add an extra layer of security to your account by requiring a code
          from your authenticator app when signing in.
        </p>
        {error && <p className="text-red-500">{error}</p>}
        <button
          onClick={handleEnable}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Setting up..." : "Set Up 2FA"}
        </button>
      </div>
    );
  }

  // Step 2: Scan QR Code
  if (step === "scan") {
    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold">Scan QR Code</h3>

        <div className="flex justify-center p-4 bg-white rounded-lg">
          <QRCodeSVG value={totpURI} size={200} level="M" />
        </div>

        <div className="text-center text-sm text-gray-600">
          <p>Scan this QR code with your authenticator app:</p>
          <p className="font-medium">Google Authenticator, Authy, 1Password, etc.</p>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">
            Enter the 6-digit code from your app
          </label>
          <input
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            placeholder="000000"
            className="w-full px-3 py-2 border rounded-md text-center text-2xl tracking-widest"
            maxLength={6}
            autoComplete="one-time-code"
          />
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <button
          onClick={handleVerify}
          disabled={loading || code.length !== 6}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Verifying..." : "Verify & Continue"}
        </button>

        <details className="text-sm">
          <summary className="cursor-pointer text-gray-500">
            Can't scan the QR code?
          </summary>
          <div className="mt-2 p-3 bg-gray-50 rounded-md">
            <p className="mb-2">Enter this key manually:</p>
            <code className="block p-2 bg-gray-100 rounded text-xs break-all">
              {totpURI.split("secret=")[1]?.split("&")[0]}
            </code>
          </div>
        </details>
      </div>
    );
  }

  // Step 3: Save Backup Codes
  if (step === "backup") {
    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold">Save Your Backup Codes</h3>

        <div className="p-4 bg-amber-50 border border-amber-200 rounded-md">
          <p className="text-amber-800 text-sm">
            <strong>Important:</strong> Save these backup codes in a safe place.
            If you lose access to your authenticator app, you can use these codes
            to sign in. Each code can only be used once.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-2 p-4 bg-gray-50 rounded-md">
          {backupCodes.map((code, i) => (
            <code key={i} className="p-2 bg-white rounded text-center font-mono">
              {code}
            </code>
          ))}
        </div>

        <div className="flex gap-2">
          <button
            onClick={copyBackupCodes}
            className="flex-1 px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            Copy Codes
          </button>
          <button
            onClick={downloadBackupCodes}
            className="flex-1 px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            Download
          </button>
        </div>

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={backupCodesSaved}
            onChange={(e) => setBackupCodesSaved(e.target.checked)}
          />
          <span className="text-sm">I have saved my backup codes</span>
        </label>

        <button
          onClick={() => setStep("done")}
          disabled={!backupCodesSaved}
          className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          Complete Setup
        </button>
      </div>
    );
  }

  // Step 4: Done
  if (step === "done") {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold">2FA Enabled!</h3>
        <p className="text-gray-600">
          Your account is now protected with two-factor authentication.
        </p>
      </div>
    );
  }

  return null;
}
```

### Compact Enable 2FA Button

```tsx
// components/auth/enable-2fa-button.tsx
"use client";

import { useState } from "react";
import { Enable2FA } from "./enable-2fa";

export function Enable2FAButton() {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="px-4 py-2 bg-blue-600 text-white rounded-md"
      >
        Enable 2FA
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
            <Enable2FA />
          </div>
        </div>
      )}
    </>
  );
}
```

### React Hook for Enable 2FA

```typescript
// hooks/useEnable2FA.ts
import { authClient } from "@/lib/auth-client";
import { useState, useCallback } from "react";

type Step = "idle" | "generating" | "scanning" | "verifying" | "done" | "error";

interface UseEnable2FAReturn {
  step: Step;
  totpURI: string | null;
  backupCodes: string[];
  error: string | null;
  startSetup: () => Promise<void>;
  verify: (code: string) => Promise<boolean>;
  reset: () => void;
}

export function useEnable2FA(): UseEnable2FAReturn {
  const [step, setStep] = useState<Step>("idle");
  const [totpURI, setTotpURI] = useState<string | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const startSetup = useCallback(async () => {
    setStep("generating");
    setError(null);

    const { data, error } = await authClient.twoFactor.enable();

    if (error) {
      setStep("error");
      setError(error.message);
      return;
    }

    setTotpURI(data.totpURI);
    setBackupCodes(data.backupCodes);
    setStep("scanning");
  }, []);

  const verify = useCallback(async (code: string): Promise<boolean> => {
    setStep("verifying");
    setError(null);

    const { error } = await authClient.twoFactor.verifyTotp({ code });

    if (error) {
      setStep("scanning");
      setError("Invalid code. Please try again.");
      return false;
    }

    setStep("done");
    return true;
  }, []);

  const reset = useCallback(() => {
    setStep("idle");
    setTotpURI(null);
    setBackupCodes([]);
    setError(null);
  }, []);

  return {
    step,
    totpURI,
    backupCodes,
    error,
    startSetup,
    verify,
    reset,
  };
}
```

### Settings Page Integration

```tsx
// app/settings/security/page.tsx
import { Enable2FA } from "@/components/auth/enable-2fa";

export default function SecuritySettingsPage() {
  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Security Settings</h1>

      <section className="bg-white rounded-lg shadow p-6">
        <Enable2FA />
      </section>
    </div>
  );
}
```

### Usage

```
/auth.2fa.enable [variant]
```

**User Input**: $ARGUMENTS

Available variants:
- `basic` - Basic enable flow
- `component` - Full React component
- `hook` - React hook implementation
- `modal` - Modal-based setup
