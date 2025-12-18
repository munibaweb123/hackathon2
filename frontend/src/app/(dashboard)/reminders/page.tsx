'use client';

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ReminderForm } from '@/components/reminders/reminder-form';
import { useAuth } from '@/hooks/use-auth';
import { jwtApiClient } from '@/services/auth/api-client';
import type { Reminder } from '@/types';

export default function RemindersPage() {
  const { user } = useAuth();
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showReminderForm, setShowReminderForm] = useState(false);
  const [editingReminder, setEditingReminder] = useState<Reminder | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchReminders = async () => {
      try {
        setIsLoading(true);
        const data = await jwtApiClient.getReminders();
        setReminders(data);
      } catch (error: unknown) {
        const errorMessage = error && typeof error === 'object' && 'message' in error
          ? (error as { message: string }).message
          : 'Failed to load reminders';
        console.error('Failed to fetch reminders:', errorMessage, error);
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReminders();
  }, []);

  const handleCreateReminder = async (data: { task_id: number; reminder_time: string; reminder_type?: 'email' | 'push' | 'sms'; message?: string }) => {
    setIsSubmitting(true);
    try {
      const newReminder = await jwtApiClient.createReminder(data);
      setReminders(prev => [...prev, newReminder]);
      toast.success('Reminder created successfully');
      setShowReminderForm(false);
    } catch (error: unknown) {
      const errorMessage = error && typeof error === 'object' && 'message' in error
        ? (error as { message: string }).message
        : 'Failed to create reminder';
      console.error('Failed to create reminder:', errorMessage, error);
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateReminder = async (data: { reminder_time?: string; reminder_type?: 'email' | 'push' | 'sms'; status?: 'pending' | 'sent' | 'cancelled'; message?: string }) => {
    if (!editingReminder) {
      toast.error('No reminder selected');
      return;
    }

    setIsSubmitting(true);
    try {
      const updatedReminder = await jwtApiClient.updateReminder(editingReminder.id, data);
      setReminders(prev => prev.map(r => r.id === editingReminder.id ? updatedReminder : r));
      toast.success('Reminder updated successfully');
      setEditingReminder(null);
    } catch (error: unknown) {
      const errorMessage = error && typeof error === 'object' && 'message' in error
        ? (error as { message: string }).message
        : 'Failed to update reminder';
      console.error('Failed to update reminder:', errorMessage, error);
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteReminder = async (reminderId: string) => {
    try {
      await jwtApiClient.deleteReminder(reminderId);
      setReminders(prev => prev.filter(r => r.id !== reminderId));
      toast.success('Reminder deleted successfully');
    } catch (error: unknown) {
      const errorMessage = error && typeof error === 'object' && 'message' in error
        ? (error as { message: string }).message
        : 'Failed to delete reminder';
      console.error('Failed to delete reminder:', errorMessage, error);
      toast.error(errorMessage);
    }
  };

  const handleCancelReminder = async (reminderId: string) => {
    try {
      const updatedReminder = await jwtApiClient.cancelReminder(reminderId);
      setReminders(prev => prev.map(r => r.id === reminderId ? updatedReminder : r));
      toast.success('Reminder cancelled successfully');
    } catch (error: unknown) {
      const errorMessage = error && typeof error === 'object' && 'message' in error
        ? (error as { message: string }).message
        : 'Failed to cancel reminder';
      console.error('Failed to cancel reminder:', errorMessage, error);
      toast.error(errorMessage);
    }
  };

  const handleEdit = (reminder: Reminder) => {
    setEditingReminder(reminder);
  };

  const reminderStatusColors = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    sent: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    cancelled: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
  };

  const reminderTypeColors = {
    push: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    email: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    sms: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading reminders...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Reminders</h1>
          <p className="text-muted-foreground">
            Manage your task reminders
          </p>
        </div>
        <Button onClick={() => setShowReminderForm(true)}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mr-2"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
          Create Reminder
        </Button>
      </div>

      {reminders.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <div className="mx-auto w-16 h-16 mb-4 text-muted-foreground">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-muted-foreground">No reminders yet</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Create your first reminder to get started
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {reminders.map((reminder) => (
            <Card key={reminder.id} className="relative">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">Task Reminder</CardTitle>
                  <Badge variant="secondary" className={reminderStatusColors[reminder.status as keyof typeof reminderStatusColors]}>
                    {reminder.status}
                  </Badge>
                </div>
                <CardDescription>
                  {format(new Date(reminder.reminder_time), 'MMM d, yyyy h:mm a')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Type:</span>
                    <Badge variant="outline" className={reminderTypeColors[reminder.reminder_type as keyof typeof reminderTypeColors]}>
                      {reminder.reminder_type}
                    </Badge>
                  </div>

                  {reminder.message && (
                    <div>
                      <span className="text-sm text-muted-foreground">Message:</span>
                      <p className="text-sm mt-1">{reminder.message}</p>
                    </div>
                  )}

                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Created:</span>
                    <span>{format(new Date(reminder.created_at), 'MMM d, yyyy')}</span>
                  </div>
                </div>

                <div className="flex gap-2 mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(reminder)}
                    className="flex-1"
                  >
                    Edit
                  </Button>
                  {reminder.status === 'pending' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCancelReminder(reminder.id)}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                  )}
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDeleteReminder(reminder.id)}
                  >
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Reminder Form */}
      <ReminderForm
        open={showReminderForm}
        onOpenChange={setShowReminderForm}
        taskId={0} // Will be set when a task is selected
        onSubmit={handleCreateReminder}
        isLoading={isSubmitting}
      />

      {/* Edit Reminder Form */}
      {editingReminder && (
        <ReminderForm
          open={!!editingReminder}
          onOpenChange={(open) => !open && setEditingReminder(null)}
          reminder={editingReminder}
          onSubmit={handleUpdateReminder}
          isLoading={isSubmitting}
        />
      )}
    </div>
  );
}