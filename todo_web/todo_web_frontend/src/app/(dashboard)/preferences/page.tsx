'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PreferencesForm } from '@/components/preferences/preferences-form';
import { useAuth } from '@/hooks/use-auth';
import { apiClient } from '@/lib/api-client';
import type { UserPreference } from '@/types';

export default function PreferencesPage() {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState<UserPreference | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!user?.id) return;

    const fetchPreferences = async () => {
      try {
        setIsLoading(true);
        const userPrefs = await apiClient.getUserPreferences(user.id);
        setPreferences(userPrefs);
      } catch (error) {
        console.error('Failed to fetch preferences:', error);
        toast.error('Failed to load preferences');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPreferences();
  }, [user?.id]);

  const handleSavePreferences = async (data: Partial<UserPreference>) => {
    if (!user?.id) {
      toast.error('User not authenticated');
      return;
    }

    setIsSaving(true);
    try {
      const updatedPreferences = await apiClient.updateUserPreferences(user.id, data);
      setPreferences(updatedPreferences);
      toast.success('Preferences updated successfully');
    } catch (error) {
      console.error('Failed to update preferences:', error);
      toast.error('Failed to update preferences');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading preferences...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Preferences</h1>
        <p className="text-muted-foreground">
          Customize your todo app experience
        </p>
      </div>

      <PreferencesForm
        preferences={preferences}
        onSubmit={handleSavePreferences}
        isLoading={isSaving}
      />

      {preferences && (
        <Card>
          <CardHeader>
            <CardTitle>About Your Preferences</CardTitle>
            <CardDescription>
              These settings control how the app behaves for you
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h4 className="font-medium">Current Settings</h4>
                <p className="text-sm text-muted-foreground">
                  Theme: <span className="font-mono">{preferences.theme}</span>
                </p>
                <p className="text-sm text-muted-foreground">
                  Language: <span className="font-mono">{preferences.language}</span>
                </p>
                <p className="text-sm text-muted-foreground">
                  Default View: <span className="font-mono">{preferences.default_view}</span>
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium">Notification Settings</h4>
                <p className="text-sm text-muted-foreground">
                  Task Notifications: <span className="font-mono">{preferences.task_notifications}</span>
                </p>
                <p className="text-sm text-muted-foreground">
                  Reminder Notifications: <span className="font-mono">{preferences.reminder_notifications}</span>
                </p>
                <p className="text-sm text-muted-foreground">
                  Email Notifications: <span className="font-mono">{preferences.email_notifications ? 'Enabled' : 'Disabled'}</span>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}