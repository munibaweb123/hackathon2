'use client';

import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { Task, CreateTaskInput, UpdateTaskInput, RecurrencePattern } from '@/types';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title is too long'),
  description: z.string().max(1000, 'Description is too long').optional(),
  priority: z.enum(['low', 'medium', 'high']),
  due_date: z.string().optional(),
  is_recurring: z.boolean().optional(),
  recurrence_pattern: z.string().nullable().optional(),
  recurrence_interval: z.number().min(1).optional(),
  recurrence_end_date: z.string().optional(),
}).refine((data) => {
  // If the task is recurring (true), recurrence_pattern is required and must be valid
  if (data.is_recurring === true) {
    const allowedValues = ['daily', 'weekly', 'biweekly', 'monthly', 'yearly', 'custom'];
    return data.recurrence_pattern && allowedValues.includes(data.recurrence_pattern);
  }
  return true; // If not recurring, validation passes
}, {
  message: 'Recurrence pattern is required for recurring tasks',
  path: ['recurrence_pattern'],
});

type TaskFormData = z.infer<typeof taskSchema>;

interface CreateTaskFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  task?: null;
  onSubmit: (data: CreateTaskInput) => Promise<void>;
  isLoading: boolean;
}

interface EditTaskFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  task: Task;
  onSubmit: (data: UpdateTaskInput) => Promise<void>;
  isLoading: boolean;
}

type TaskFormProps = CreateTaskFormProps | EditTaskFormProps;

export function TaskForm({ open, onOpenChange, task, onSubmit, isLoading }: TaskFormProps) {
  const isEditing = !!task;

  const {
    register,
    handleSubmit,
    reset,
    watch,
    control,
    trigger,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    mode: 'onSubmit', // Only validate on submit
    reValidateMode: 'onChange', // Re-validate after first submission
    defaultValues: {
      title: '',
      description: '',
      priority: 'medium',
      due_date: '',
      is_recurring: false,
      recurrence_pattern: undefined,
      recurrence_interval: 1,
      recurrence_end_date: '',
    },
  });

  // Watch the is_recurring field to conditionally show recurrence fields
  const isRecurring = watch('is_recurring');

  useEffect(() => {
    if (task) {
      reset({
        title: task.title,
        description: task.description || '',
        priority: task.priority,
        due_date: task.due_date ? task.due_date.split('T')[0] : '',
        is_recurring: task.is_recurring || false,
        recurrence_pattern: task.recurrence_pattern,
        recurrence_interval: task.recurrence_interval || 1,
        recurrence_end_date: task.recurrence_end_date ? task.recurrence_end_date.split('T')[0] : '',
      }, { keepErrors: true }); // Don't clear errors when resetting form
    } else {
      reset({
        title: '',
        description: '',
        priority: 'medium',
        due_date: '',
        is_recurring: false,
        recurrence_pattern: undefined,
        recurrence_interval: 1,
        recurrence_end_date: '',
      }, { keepErrors: true }); // Don't clear errors when resetting form
    }
  }, [task, reset]);

  const handleFormSubmit = async (data: TaskFormData) => {
    // Convert date strings to datetime strings (backend expects ISO format)
    const convertDateToDateTime = (dateStr: string | undefined): string | undefined => {
      if (!dateStr) return undefined;
      // Create a date object and convert to ISO string
      // The date string from input is in local time, so we need to convert to ISO properly
      const date = new Date(dateStr);
      return date.toISOString();
    };

    const submitData: CreateTaskInput | UpdateTaskInput = {
      title: data.title,
      description: data.description || undefined,
      priority: data.priority,
      due_date: data.due_date ? convertDateToDateTime(data.due_date) : undefined,
      is_recurring: data.is_recurring,
      recurrence_pattern: (data.recurrence_pattern as RecurrencePattern) || undefined,
      recurrence_interval: data.recurrence_interval,
      recurrence_end_date: data.recurrence_end_date ? convertDateToDateTime(data.recurrence_end_date) : undefined,
    };

    await onSubmit(submitData as any);
    onOpenChange(false);
    reset();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Task' : 'Create New Task'}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Make changes to your task here.'
              : 'Add a new task to your list.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(handleFormSubmit, (errors) => {
          // Check if errors is a valid object with keys
          if (errors && typeof errors === 'object' && Object.keys(errors).length > 0) {
            console.error('Task form validation errors:', errors);
          } else if (errors) {
            console.error('Task form validation errors (raw):', typeof errors, errors);
          } else {
            console.error('Task form validation failed: No specific validation errors provided');
          }
          // Trigger form validation to show errors
          trigger();
        })}>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                placeholder="Enter task title"
                {...register('title')}
                disabled={isLoading}
              />
              {errors.title && (
                <p className="text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <textarea
                id="description"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Enter task description (optional)"
                {...register('description')}
                disabled={isLoading}
              />
              {errors.description && (
                <p className="text-sm text-red-600">{errors.description.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <select
                id="priority"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register('priority')}
                disabled={isLoading}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="due_date">Due Date</Label>
              <Input
                id="due_date"
                type="date"
                {...register('due_date')}
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Controller
                  name="is_recurring"
                  control={control}
                  render={({ field }) => (
                    <Checkbox
                      id="is_recurring"
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      disabled={isLoading}
                    />
                  )}
                />
                <Label htmlFor="is_recurring">Recurring Task</Label>
              </div>
            </div>

            {isRecurring && (
              <div className="space-y-4 border-t pt-4">
                <div className="space-y-2">
                  <Label htmlFor="recurrence_pattern">Recurrence Pattern *</Label>
                  <select
                    id="recurrence_pattern"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...register('recurrence_pattern')}
                    disabled={isLoading}
                  >
                    <option value="">Select pattern</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="biweekly">Bi-weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                    <option value="custom">Custom</option>
                  </select>
                  {errors.recurrence_pattern && (
                    <p className="text-sm text-red-600">{errors.recurrence_pattern.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="recurrence_interval">Interval</Label>
                  <Input
                    id="recurrence_interval"
                    type="number"
                    min="1"
                    {...register('recurrence_interval', { valueAsNumber: true })}
                    disabled={isLoading}
                  />
                  <p className="text-sm text-muted-foreground">e.g., every 2 weeks</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="recurrence_end_date">End Date (optional)</Label>
                  <Input
                    id="recurrence_end_date"
                    type="date"
                    {...register('recurrence_end_date')}
                    disabled={isLoading}
                  />
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || isSubmitting}>
              {isLoading || isSubmitting
                ? isEditing
                  ? 'Saving...'
                  : 'Creating...'
                : isEditing
                ? 'Save Changes'
                : 'Create Task'}
            </Button>
          </DialogFooter>
          {/* Debug: Show all errors - only showing message fields to avoid circular references */}
          {Object.keys(errors).length > 0 && (
            <div className="text-xs text-orange-600 bg-orange-50 p-2 rounded mb-2">
              <strong>Debug - Error Messages:</strong>
              <pre>{JSON.stringify(
                Object.fromEntries(
                  Object.entries(errors).map(([key, value]: [string, any]) => [key, value?.message])
                ),
                null,
                2
              )}</pre>
            </div>
          )}
        </form>
      </DialogContent>
    </Dialog>
  );
}
