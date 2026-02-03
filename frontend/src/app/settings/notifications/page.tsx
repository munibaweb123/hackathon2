"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";

interface NotificationPreferences {
  in_app_enabled: boolean;
  email_enabled: boolean;
  reminder_lead_time: number;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
}

export default function NotificationSettingsPage() {
  const [prefs, setPrefs] = useState<NotificationPreferences>({
    in_app_enabled: true,
    email_enabled: true,
    reminder_lead_time: 60,
    quiet_hours_start: null,
    quiet_hours_end: null,
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    apiClient
      .getNotificationPreferences()
      .then(setPrefs)
      .catch(() => {});
  }, []);

  const save = async () => {
    setSaving(true);
    setMessage("");
    try {
      const updated = await apiClient.updateNotificationPreferences(prefs);
      setPrefs(updated);
      setMessage("Preferences saved.");
    } catch {
      setMessage("Failed to save preferences.");
    }
    setSaving(false);
  };

  const sendTest = async () => {
    try {
      await apiClient.sendTestNotification();
      setMessage("Test notification sent.");
    } catch {
      setMessage("Failed to send test notification.");
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Notification Settings</h1>

      <div className="space-y-4">
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={prefs.in_app_enabled}
            onChange={(e) =>
              setPrefs({ ...prefs, in_app_enabled: e.target.checked })
            }
            className="h-4 w-4"
          />
          <span>In-app notifications</span>
        </label>

        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={prefs.email_enabled}
            onChange={(e) =>
              setPrefs({ ...prefs, email_enabled: e.target.checked })
            }
            className="h-4 w-4"
          />
          <span>Email notifications</span>
        </label>

        <div>
          <label className="block text-sm font-medium mb-1">
            Reminder lead time (minutes before due date)
          </label>
          <input
            type="number"
            min={0}
            value={prefs.reminder_lead_time}
            onChange={(e) =>
              setPrefs({
                ...prefs,
                reminder_lead_time: parseInt(e.target.value) || 0,
              })
            }
            className="border rounded px-3 py-2 w-32"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Quiet hours start
            </label>
            <input
              type="time"
              value={prefs.quiet_hours_start || ""}
              onChange={(e) =>
                setPrefs({
                  ...prefs,
                  quiet_hours_start: e.target.value || null,
                })
              }
              className="border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Quiet hours end
            </label>
            <input
              type="time"
              value={prefs.quiet_hours_end || ""}
              onChange={(e) =>
                setPrefs({
                  ...prefs,
                  quiet_hours_end: e.target.value || null,
                })
              }
              className="border rounded px-3 py-2"
            />
          </div>
        </div>
      </div>

      <div className="flex gap-3 mt-6">
        <button
          onClick={save}
          disabled={saving}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save Preferences"}
        </button>
        <button
          onClick={sendTest}
          className="border px-4 py-2 rounded hover:bg-gray-50"
        >
          Send Test Notification
        </button>
      </div>

      {message && (
        <p className="mt-4 text-sm text-gray-600">{message}</p>
      )}
    </div>
  );
}
