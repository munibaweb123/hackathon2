---
description: Manage 2FA settings - disable, backup codes, status with Better Auth
---

## Better Auth: Manage 2FA

This skill covers managing 2FA settings including checking status, disabling 2FA, and regenerating backup codes.

### Check 2FA Status

```typescript
const { data } = await authClient.twoFactor.status();

console.log("2FA enabled:", data.enabled);
```

### Disable 2FA

```typescript
const { error } = await authClient.twoFactor.disable({
  password: "currentPassword", // May be required for security
});

if (error) {
  console.error("Failed to disable 2FA:", error.message);
} else {
  console.log("2FA disabled successfully");
}
```

### Regenerate Backup Codes

```typescript
const { data, error } = await authClient.twoFactor.generateBackupCodes();

if (error) {
  console.error("Failed to generate backup codes:", error.message);
  return;
}

// data.backupCodes contains new codes
// Old codes are now invalidated
console.log("New backup codes:", data.backupCodes);
```

### React Hook for 2FA Management

```typescript
// hooks/useTwoFactorManagement.ts
import { authClient } from "@/lib/auth-client";
import { useState, useEffect, useCallback } from "react";

interface TwoFactorStatus {
  enabled: boolean;
  loading: boolean;
}

export function useTwoFactorManagement() {
  const [status, setStatus] = useState<TwoFactorStatus>({
    enabled: false,
    loading: true,
  });
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      const { data, error } = await authClient.twoFactor.status();

      if (error) {
        setStatus({ enabled: false, loading: false });
        return;
      }

      setStatus({ enabled: data.enabled, loading: false });
    };

    fetchStatus();
  }, []);

  // Disable 2FA
  const disable = useCallback(async (password?: string) => {
    setActionLoading(true);
    setError(null);

    const { error } = await authClient.twoFactor.disable({
      password,
    });

    setActionLoading(false);

    if (error) {
      setError(error.message);
      return false;
    }

    setStatus({ enabled: false, loading: false });
    return true;
  }, []);

  // Regenerate backup codes
  const regenerateBackupCodes = useCallback(async () => {
    setActionLoading(true);
    setError(null);

    const { data, error } = await authClient.twoFactor.generateBackupCodes();

    setActionLoading(false);

    if (error) {
      setError(error.message);
      return null;
    }

    return data.backupCodes;
  }, []);

  // Refresh status
  const refresh = useCallback(async () => {
    setStatus((prev) => ({ ...prev, loading: true }));

    const { data } = await authClient.twoFactor.status();

    setStatus({
      enabled: data?.enabled ?? false,
      loading: false,
    });
  }, []);

  return {
    status,
    actionLoading,
    error,
    disable,
    regenerateBackupCodes,
    refresh,
    clearError: () => setError(null),
  };
}
```

### 2FA Settings Component

```tsx
// components/settings/two-factor-settings.tsx
"use client";

import { useState } from "react";
import { useTwoFactorManagement } from "@/hooks/useTwoFactorManagement";
import { Enable2FA } from "@/components/auth/enable-2fa";

export function TwoFactorSettings() {
  const {
    status,
    actionLoading,
    error,
    disable,
    regenerateBackupCodes,
    refresh,
  } = useTwoFactorManagement();

  const [showDisableConfirm, setShowDisableConfirm] = useState(false);
  const [password, setPassword] = useState("");
  const [newBackupCodes, setNewBackupCodes] = useState<string[] | null>(null);

  if (status.loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
      </div>
    );
  }

  // 2FA not enabled - show enable component
  if (!status.enabled) {
    return <Enable2FA />;
  }

  // 2FA is enabled - show management options
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Two-Factor Authentication</h3>
          <p className="text-sm text-green-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            Enabled
          </p>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-red-600 rounded-md text-sm">
          {error}
        </div>
      )}

      {/* Regenerate Backup Codes */}
      <div className="p-4 border rounded-lg">
        <h4 className="font-medium mb-2">Backup Codes</h4>
        <p className="text-sm text-gray-600 mb-4">
          Generate new backup codes. This will invalidate any existing codes.
        </p>

        {newBackupCodes ? (
          <div className="space-y-4">
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-md">
              <p className="text-sm text-amber-800 mb-2">
                <strong>Save these codes now!</strong> They won't be shown again.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {newBackupCodes.map((code, i) => (
                <code
                  key={i}
                  className="p-2 bg-gray-100 rounded text-center font-mono text-sm"
                >
                  {code}
                </code>
              ))}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(newBackupCodes.join("\n"));
                }}
                className="flex-1 px-3 py-2 border rounded-md text-sm hover:bg-gray-50"
              >
                Copy All
              </button>
              <button
                onClick={() => setNewBackupCodes(null)}
                className="flex-1 px-3 py-2 border rounded-md text-sm hover:bg-gray-50"
              >
                Done
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={async () => {
              const codes = await regenerateBackupCodes();
              if (codes) {
                setNewBackupCodes(codes);
              }
            }}
            disabled={actionLoading}
            className="px-4 py-2 border rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            {actionLoading ? "Generating..." : "Generate New Backup Codes"}
          </button>
        )}
      </div>

      {/* Disable 2FA */}
      <div className="p-4 border border-red-200 rounded-lg bg-red-50">
        <h4 className="font-medium text-red-800 mb-2">Disable 2FA</h4>
        <p className="text-sm text-red-700 mb-4">
          Disabling 2FA will make your account less secure.
        </p>

        {showDisableConfirm ? (
          <div className="space-y-3">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password to confirm"
              className="w-full px-3 py-2 border rounded-md"
            />
            <div className="flex gap-2">
              <button
                onClick={async () => {
                  const success = await disable(password);
                  if (success) {
                    setShowDisableConfirm(false);
                    setPassword("");
                  }
                }}
                disabled={actionLoading || !password}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                {actionLoading ? "Disabling..." : "Confirm Disable"}
              </button>
              <button
                onClick={() => {
                  setShowDisableConfirm(false);
                  setPassword("");
                }}
                className="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setShowDisableConfirm(true)}
            className="px-4 py-2 border border-red-300 text-red-700 rounded-md hover:bg-red-100"
          >
            Disable Two-Factor Authentication
          </button>
        )}
      </div>
    </div>
  );
}
```

### Compact 2FA Status Badge

```tsx
// components/auth/two-factor-badge.tsx
"use client";

import { useTwoFactorManagement } from "@/hooks/useTwoFactorManagement";
import Link from "next/link";

export function TwoFactorBadge() {
  const { status } = useTwoFactorManagement();

  if (status.loading) {
    return null;
  }

  if (status.enabled) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
            clipRule="evenodd"
          />
        </svg>
        2FA Enabled
      </span>
    );
  }

  return (
    <Link
      href="/settings/security"
      className="inline-flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs hover:bg-amber-200"
    >
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
      Enable 2FA
    </Link>
  );
}
```

### Backup Codes Modal

```tsx
// components/auth/backup-codes-modal.tsx
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";

interface BackupCodesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function BackupCodesModal({ isOpen, onClose }: BackupCodesModalProps) {
  const [codes, setCodes] = useState<string[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const generateCodes = async () => {
    setLoading(true);
    setError("");

    const { data, error } = await authClient.twoFactor.generateBackupCodes();

    setLoading(false);

    if (error) {
      setError(error.message);
      return;
    }

    setCodes(data.backupCodes);
  };

  const copyToClipboard = () => {
    if (codes) {
      navigator.clipboard.writeText(codes.join("\n"));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-md w-full p-6">
        <h3 className="text-lg font-semibold mb-4">Backup Codes</h3>

        {!codes ? (
          <div className="space-y-4">
            <p className="text-gray-600 text-sm">
              Generate new backup codes. Your existing codes will be invalidated.
            </p>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <div className="flex gap-2">
              <button
                onClick={generateCodes}
                disabled={loading}
                className="flex-1 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50"
              >
                {loading ? "Generating..." : "Generate New Codes"}
              </button>
              <button
                onClick={onClose}
                className="px-4 py-2 border rounded-md"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-md text-sm text-amber-800">
              Save these codes in a safe place. They won't be shown again.
            </div>

            <div className="grid grid-cols-2 gap-2">
              {codes.map((code, i) => (
                <code
                  key={i}
                  className="p-2 bg-gray-100 rounded text-center font-mono"
                >
                  {code}
                </code>
              ))}
            </div>

            <div className="flex gap-2">
              <button
                onClick={copyToClipboard}
                className="flex-1 py-2 border rounded-md hover:bg-gray-50"
              >
                {copied ? "Copied!" : "Copy All"}
              </button>
              <button
                onClick={onClose}
                className="flex-1 py-2 bg-blue-600 text-white rounded-md"
              >
                Done
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

### Settings Page Integration

```tsx
// app/settings/security/page.tsx
import { TwoFactorSettings } from "@/components/settings/two-factor-settings";

export default function SecuritySettingsPage() {
  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Security Settings</h1>

      <section className="bg-white rounded-lg shadow p-6">
        <TwoFactorSettings />
      </section>
    </div>
  );
}
```

### TypeScript Types

```typescript
interface TwoFactorStatusResponse {
  enabled: boolean;
}

interface BackupCodesResponse {
  backupCodes: string[];
}

interface DisableParams {
  password?: string;
}
```

### Usage

```
/auth.2fa.manage [action]
```

**User Input**: $ARGUMENTS

Available actions:
- `status` - Check 2FA status
- `disable` - Disable 2FA
- `backup` - Regenerate backup codes
- `component` - Full settings component
- `hook` - React hook implementation
