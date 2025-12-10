'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { ReminderForm } from '@/components/reminders/reminder-form';
import type { Task, Reminder } from '@/types';

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => Promise<void>;
  onAddReminder: (task: Task) => void;
  onManageReminders: (task: Task) => void;
}

const priorityColors = {
  low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
};

export function TaskItem({ task, onToggleComplete, onEdit, onDelete, onAddReminder, onManageReminders }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [showReminderForm, setShowReminderForm] = useState(false);

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleAddReminder = () => {
    onAddReminder(task);
  };

  const handleManageReminders = () => {
    onManageReminders(task);
  };

  return (
    <div className={`flex items-start gap-4 p-4 border rounded-lg transition-all hover:shadow-sm ${
      task.completed ? 'bg-muted/50' : 'bg-card'
    }`}>
      <Checkbox
        checked={task.completed}
        onCheckedChange={handleToggle}
        disabled={isToggling}
        className="mt-1"
      />

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className={`font-medium ${task.completed ? 'line-through text-muted-foreground' : ''}`}>
            {task.title}
          </h3>
          <Badge variant="secondary" className={priorityColors[task.priority]}>
            {task.priority}
          </Badge>
          {task.is_recurring && (
            <Badge variant="outline" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="mr-1"
              >
                <path d="M21 12a9 9 0 1 0-9 9" />
                <path d="M3 12a9 9 0 0 1 9-9 9 9 0 0 1 6.5 2.5" />
                <path d="M12 7v5l3 3" />
              </svg>
              Recurring
            </Badge>
          )}
          {task.reminders && task.reminders.length > 0 && (
            <Badge variant="outline" className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="mr-1"
              >
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
              {task.reminders.length} Reminder{task.reminders.length !== 1 ? 's' : ''}
            </Badge>
          )}
        </div>

        {task.description && (
          <p className={`mt-1 text-sm ${task.completed ? 'text-muted-foreground' : 'text-muted-foreground'}`}>
            {task.description}
          </p>
        )}

        <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
          {task.due_date && (
            <span>Due: {format(new Date(task.due_date), 'MMM d, yyyy')}</span>
          )}
          <span>Created: {format(new Date(task.created_at), 'MMM d, yyyy')}</span>
        </div>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <span className="sr-only">Open menu</span>
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
            >
              <circle cx="12" cy="12" r="1" />
              <circle cx="12" cy="5" r="1" />
              <circle cx="12" cy="19" r="1" />
            </svg>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => onEdit(task)}>
            Edit
          </DropdownMenuItem>
          <DropdownMenuItem onClick={handleAddReminder}>
            Add Reminder
          </DropdownMenuItem>
          {task.reminders && task.reminders.length > 0 && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleManageReminders}>
                Manage Reminders
              </DropdownMenuItem>
            </>
          )}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-red-600 focus:text-red-600"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
