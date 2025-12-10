'use client';

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { Reminder, ReminderType } from '@/types';

const reminderSchema = z.object({
  task_id: z.string().min(1, 'Task ID is required'),
  reminder_time: z.string().min(1, 'Reminder time is required'),
  reminder_type: z.enum(['email', 'push', 'sms']).default('push'),
  message: z.string().max(500, 'Message is too long').optional(),
});

type ReminderFormData = z.infer<typeof reminderSchema>;

interface CreateReminderFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  taskId: string; // Required when creating a new reminder
  reminder?: null;
  onSubmit: (data: { task_id: string; reminder_time: string; reminder_type?: ReminderType; message?: string }) => Promise<void>;
  isLoading: boolean;
}

interface EditReminderFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  reminder: Reminder;
  onSubmit: (data: { reminder_time?: string; reminder_type?: ReminderType; status?: string; message?: string }) => Promise<void>;
  isLoading: boolean;
}

type ReminderFormProps = CreateReminderFormProps | EditReminderFormProps;

export function ReminderForm({ open, onOpenChange, reminder, onSubmit, isLoading }: ReminderFormProps) {
  const isEditing = !!reminder;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ReminderFormData>({
    resolver: zodResolver(reminderSchema),
    defaultValues: {
      task_id: '',
      reminder_time: '',
      reminder_type: 'push',
      message: '',
    },
  });

  useEffect(() => {
    if (reminder) {
      reset({
        task_id: reminder.task_id,
        reminder_time: reminder.reminder_time,
        reminder_type: reminder.reminder_type,
        message: reminder.message || '',
      });
    } else {
      reset({
        task_id: '',
        reminder_time: '',
        reminder_type: 'push',
        message: '',
      });
    }
  }, [reminder, reset]);

  const handleFormSubmit = async (data: ReminderFormData) => {
    // Convert the datetime-local string to ISO string format for the backend
    // The datetime-local input returns format like "YYYY-MM-DDTHH:mm", we need to convert to ISO
    const formatDateTime = (dateTimeStr: string): string => {
      if (!dateTimeStr) return dateTimeStr;
      // If it's already in ISO format, return as is
      if (dateTimeStr.includes('T') && dateTimeStr.includes(':')) {
        // Add seconds and 'Z' if needed to make it ISO format
        if (dateTimeStr.length === 16) { // "YYYY-MM-DDTHH:mm" format
          return new Date(dateTimeStr).toISOString();
        }
      }
      return dateTimeStr;
    };

    if (isEditing) {
      // For editing, only update allowed fields
      const submitData = {
        reminder_time: formatDateTime(data.reminder_time),
        reminder_type: data.reminder_type,
        message: data.message || undefined,
      };
      await (onSubmit as (data: { reminder_time?: string; reminder_type?: ReminderType; status?: string; message?: string }) => Promise<void>)(submitData);
    } else {
      // For creating, include task_id
      const submitData = {
        task_id: data.task_id,
        reminder_time: formatDateTime(data.reminder_time),
        reminder_type: data.reminder_type,
        message: data.message || undefined,
      };
      await (onSubmit as (data: { task_id: string; reminder_time: string; reminder_type?: ReminderType; message?: string }) => Promise<void>)(submitData);
    }
    onOpenChange(false);
    reset();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Reminder' : 'Create New Reminder'}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Update your reminder settings here.'
              : 'Set up a reminder for your task.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(handleFormSubmit)}>
          <div className="grid gap-4 py-4">
            {!isEditing && (
              <div className="space-y-2">
                <Label htmlFor="task_id">Task ID</Label>
                <Input
                  id="task_id"
                  placeholder="Enter task ID"
                  {...register('task_id')}
                  disabled={isLoading}
                />
                {errors.task_id && (
                  <p className="text-sm text-red-600">{errors.task_id.message}</p>
                )}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="reminder_time">Reminder Time *</Label>
              <Input
                id="reminder_time"
                type="datetime-local"
                {...register('reminder_time')}
                disabled={isLoading}
              />
              {errors.reminder_time && (
                <p className="text-sm text-red-600">{errors.reminder_time.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="reminder_type">Reminder Type</Label>
              <select
                id="reminder_type"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register('reminder_type')}
                disabled={isLoading}
              >
                <option value="push">Push Notification</option>
                <option value="email">Email</option>
                <option value="sms">SMS</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="message">Message (optional)</Label>
              <Textarea
                id="message"
                placeholder="Custom reminder message"
                {...register('message')}
                disabled={isLoading}
                rows={3}
              />
              {errors.message && (
                <p className="text-sm text-red-600">{errors.message.message}</p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading
                ? isEditing
                  ? 'Saving...'
                  : 'Creating...'
                : isEditing
                ? 'Save Changes'
                : 'Create Reminder'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}