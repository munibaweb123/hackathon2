'use client';

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import type { UserPreference } from '@/types';

const preferencesSchema = z.object({
  theme: z.enum(['light', 'dark', 'auto']),
  language: z.string().min(2, 'Language must be at least 2 characters'),
  task_notifications: z.enum(['all', 'mute', 'scheduled']),
  reminder_notifications: z.enum(['all', 'mute', 'scheduled']),
  email_notifications: z.boolean(),
  default_view: z.string(),
  show_completed_tasks: z.boolean(),
  group_by: z.string(),
  auto_archive_completed: z.boolean(),
  auto_snooze_time: z.number().min(1).max(1440).optional(), // 1 minute to 24 hours
  work_hours_start: z.string().regex(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format (HH:MM)'),
  work_hours_end: z.string().regex(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format (HH:MM)'),
});

type PreferencesFormData = z.infer<typeof preferencesSchema>;

interface PreferencesFormProps {
  preferences: UserPreference | null;
  onSubmit: (data: Partial<UserPreference>) => Promise<void>;
  isLoading: boolean;
}

export function PreferencesForm({ preferences, onSubmit, isLoading }: PreferencesFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<PreferencesFormData>({
    resolver: zodResolver(preferencesSchema),
    defaultValues: {
      theme: 'auto',
      language: 'en',
      task_notifications: 'all',
      reminder_notifications: 'all',
      email_notifications: true,
      default_view: 'list',
      show_completed_tasks: true,
      group_by: 'none',
      auto_archive_completed: false,
      auto_snooze_time: undefined,
      work_hours_start: '09:00',
      work_hours_end: '17:00',
    },
  });

  useEffect(() => {
    if (preferences) {
      reset({
        theme: preferences.theme,
        language: preferences.language,
        task_notifications: preferences.task_notifications,
        reminder_notifications: preferences.reminder_notifications,
        email_notifications: preferences.email_notifications,
        default_view: preferences.default_view,
        show_completed_tasks: preferences.show_completed_tasks,
        group_by: preferences.group_by,
        auto_archive_completed: preferences.auto_archive_completed,
        auto_snooze_time: preferences.auto_snooze_time,
        work_hours_start: preferences.work_hours_start,
        work_hours_end: preferences.work_hours_end,
      });
    }
  }, [preferences, reset]);

  const handleFormSubmit = async (data: PreferencesFormData) => {
    await onSubmit(data);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>User Preferences</CardTitle>
        <CardDescription>Customize your todo app experience</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium">Appearance</h3>
              <div className="space-y-2 mt-2">
                <div className="space-y-1">
                  <Label htmlFor="theme">Theme</Label>
                  <select
                    id="theme"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...register('theme')}
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="auto">Auto</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <Label htmlFor="language">Language</Label>
                  <Input
                    id="language"
                    placeholder="e.g., en"
                    {...register('language')}
                  />
                  {errors.language && (
                    <p className="text-sm text-red-600">{errors.language.message}</p>
                  )}
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium">Notifications</h3>
              <div className="space-y-2 mt-2">
                <div className="space-y-1">
                  <Label htmlFor="task_notifications">Task Notifications</Label>
                  <select
                    id="task_notifications"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...register('task_notifications')}
                  >
                    <option value="all">All</option>
                    <option value="mute">Mute</option>
                    <option value="scheduled">Scheduled</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <Label htmlFor="reminder_notifications">Reminder Notifications</Label>
                  <select
                    id="reminder_notifications"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...register('reminder_notifications')}
                  >
                    <option value="all">All</option>
                    <option value="mute">Mute</option>
                    <option value="scheduled">Scheduled</option>
                  </select>
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="email_notifications">Email Notifications</Label>
                  <Switch
                    id="email_notifications"
                    {...register('email_notifications', { value: false })}
                  />
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium">Task Display</h3>
              <div className="space-y-2 mt-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="show_completed_tasks">Show Completed Tasks</Label>
                  <Switch
                    id="show_completed_tasks"
                    {...register('show_completed_tasks', { value: false })}
                  />
                </div>

                <div className="space-y-1">
                  <Label htmlFor="default_view">Default View</Label>
                  <select
                    id="default_view"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...register('default_view')}
                  >
                    <option value="list">List</option>
                    <option value="grid">Grid</option>
                    <option value="calendar">Calendar</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <Label htmlFor="group_by">Group By</Label>
                  <select
                    id="group_by"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...register('group_by')}
                  >
                    <option value="none">None</option>
                    <option value="priority">Priority</option>
                    <option value="due_date">Due Date</option>
                    <option value="category">Category</option>
                  </select>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium">Advanced Settings</h3>
              <div className="space-y-2 mt-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="auto_archive_completed">Auto Archive Completed</Label>
                  <Switch
                    id="auto_archive_completed"
                    {...register('auto_archive_completed', { value: false })}
                  />
                </div>

                <div className="space-y-1">
                  <Label htmlFor="auto_snooze_time">Auto Snooze Time (minutes)</Label>
                  <Input
                    id="auto_snooze_time"
                    type="number"
                    min="1"
                    max="1440"
                    placeholder="e.g., 30"
                    {...register('auto_snooze_time', { valueAsNumber: true })}
                  />
                  <p className="text-sm text-muted-foreground">Time in minutes (1-1440)</p>
                  {errors.auto_snooze_time && (
                    <p className="text-sm text-red-600">{errors.auto_snooze_time.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <Label htmlFor="work_hours_start">Work Hours Start</Label>
                    <Input
                      id="work_hours_start"
                      type="time"
                      {...register('work_hours_start')}
                    />
                    {errors.work_hours_start && (
                      <p className="text-sm text-red-600">{errors.work_hours_start.message}</p>
                    )}
                  </div>

                  <div className="space-y-1">
                    <Label htmlFor="work_hours_end">Work Hours End</Label>
                    <Input
                      id="work_hours_end"
                      type="time"
                      {...register('work_hours_end')}
                    />
                    {errors.work_hours_end && (
                      <p className="text-sm text-red-600">{errors.work_hours_end.message}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? 'Saving...' : 'Save Preferences'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}