'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import type { Task } from '@/types';

interface DeleteTaskDialogProps {
  task: Task | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDelete: (taskId: number, deleteOption?: 'single' | 'all_future') => Promise<void>;
  isLoading: boolean;
}

export function DeleteTaskDialog({ task, open, onOpenChange, onDelete, isLoading }: DeleteTaskDialogProps) {
  const [deleteOption, setDeleteOption] = useState<'single' | 'all_future'>('single');

  const handleDelete = async () => {
    if (!task) return;

    await onDelete(task.id, deleteOption);
    onOpenChange(false);
  };

  // Check if the task is a recurring task
  const isRecurringTask = task?.is_recurring || task?.recurrence_pattern;
  const isRecurringInstance = task?.parent_task_id;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Delete Task</DialogTitle>
          <DialogDescription>
            {isRecurringTask
              ? 'This task is part of a recurring series. How would you like to proceed?'
              : isRecurringInstance
              ? 'This task is an instance of a recurring series. How would you like to proceed?'
              : 'Are you sure you want to delete this task? This action cannot be undone.'}
          </DialogDescription>
        </DialogHeader>

        {(isRecurringTask || isRecurringInstance) && (
          <RadioGroup
            value={deleteOption}
            onValueChange={(value: 'single' | 'all_future') => setDeleteOption(value)}
            className="grid gap-2"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="single" id="single" />
              <Label htmlFor="single">
                <span className="font-medium">Delete only this task</span>
                <p className="text-xs text-muted-foreground">
                  {isRecurringTask
                    ? 'Delete this occurrence and future occurrences will continue'
                    : 'Delete only this instance'}
                </p>
              </Label>
            </div>

            {isRecurringTask && (
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="all_future" id="all_future" />
                <Label htmlFor="all_future">
                  <span className="font-medium">Delete all future occurrences</span>
                  <p className="text-xs text-muted-foreground">
                    Cancel the recurring task and delete all future occurrences
                  </p>
                </Label>
              </div>
            )}
          </RadioGroup>
        )}

        <DialogFooter className="sm:justify-start">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleDelete}
            disabled={isLoading}
          >
            {isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}