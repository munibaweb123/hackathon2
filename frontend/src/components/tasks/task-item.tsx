'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { motion } from 'framer-motion';
import { MoreVertical, Edit, Trash2, Bell, Clock, Calendar, Repeat } from 'lucide-react';
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
import type { Task } from '@/types';

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: number) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: number) => Promise<void>;
  onAddReminder: (task: Task) => void;
  onManageReminders: (task: Task) => void;
}

const priorityConfig = {
  low: {
    color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
    dot: 'bg-emerald-500',
  },
  medium: {
    color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    dot: 'bg-amber-500',
  },
  high: {
    color: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400',
    dot: 'bg-rose-500',
  },
  none: {
    color: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    dot: 'bg-gray-500',
  },
};

// Helper function to determine if a color is light or dark
function isColorLight(hexColor: string): boolean {
  // Remove the # if present
  const hex = hexColor.replace('#', '');

  // Convert to RGB
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  // Calculate the brightness (luminance)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;

  // Return true if the color is light (brightness > 128)
  return brightness > 128;
}

export function TaskItem({ task, onToggleComplete, onEdit, onDelete, onAddReminder, onManageReminders }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

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

  const priority = priorityConfig[task.priority];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      whileHover={{ scale: 1.01 }}
      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      className={`group relative flex items-start gap-4 p-4 rounded-xl border transition-all ${
        task.completed
          ? 'bg-muted/30 border-border/50'
          : 'bg-card hover:bg-card/80 border-border hover:border-primary/20 hover:shadow-lg hover:shadow-primary/5'
      }`}
    >
      {/* Priority indicator */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-xl ${priority.dot} opacity-60`} />

      <motion.div whileTap={{ scale: 0.9 }}>
        <Checkbox
          checked={task.completed}
          onCheckedChange={handleToggle}
          disabled={isToggling}
          className="mt-1 h-5 w-5 rounded-full border-2 data-[state=checked]:bg-primary data-[state=checked]:border-primary"
        />
      </motion.div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className={`font-medium text-base ${task.completed ? 'line-through text-muted-foreground' : ''}`}>
            {task.title}
          </h3>
          <Badge variant="secondary" className={`text-xs ${priority.color}`}>
            {task.priority}
          </Badge>
          {task.is_recurring && (
            <Badge variant="outline" className="text-xs bg-blue-100/50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800">
              <Repeat className="h-3 w-3 mr-1" />
              Recurring
            </Badge>
          )}
          {task.reminders && task.reminders.length > 0 && (
            <Badge variant="outline" className="text-xs bg-purple-100/50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200 dark:border-purple-800">
              <Bell className="h-3 w-3 mr-1" />
              {task.reminders.length}
            </Badge>
          )}
          {task.tags && task.tags.length > 0 && (
            <div className="flex gap-1 flex-wrap">
              {task.tags.map((tag) => {
                const bgColor = tag.color || '#6b7280'; // Default to gray if no color
                const textColor = isColorLight(bgColor) ? '#000000' : '#ffffff';
                return (
                  <Badge
                    key={tag.id}
                    variant="secondary"
                    style={{ backgroundColor: `${bgColor}20`, color: textColor, border: `1px solid ${bgColor}` }}
                    className="text-xs px-2 py-0.5"
                  >
                    {tag.name}
                  </Badge>
                );
              })}
            </div>
          )}
        </div>

        {task.description && (
          <p className={`mt-1.5 text-sm line-clamp-2 ${task.completed ? 'text-muted-foreground/60' : 'text-muted-foreground'}`}>
            {task.description}
          </p>
        )}

        <div className="mt-3 flex items-center gap-4 text-xs">
          {task.due_date && (
            <span className={`flex items-center gap-1 ${task.is_overdue && !task.completed ? 'text-red-600 font-medium' : 'text-muted-foreground'}`}>
              <Calendar className={`h-3.5 w-3.5 ${task.is_overdue && !task.completed ? 'text-red-500' : ''}`} />
              {format(new Date(task.due_date), 'MMM d, yyyy')}
              {task.is_overdue && !task.completed && (
                <span className="ml-1 text-[10px] bg-red-100 text-red-800 px-1 py-0.5 rounded-full dark:bg-red-900/30 dark:text-red-300">
                  OVERDUE
                </span>
              )}
            </span>
          )}
          {task.reminder_at && (
            <span className="flex items-center gap-1 text-muted-foreground">
              <Bell className="h-3.5 w-3.5" />
              {format(new Date(task.reminder_at), 'HH:mm')}
            </span>
          )}
          <span className="flex items-center gap-1 text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            {format(new Date(task.created_at), 'MMM d')}
          </span>
        </div>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <MoreVertical className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuItem onClick={() => onEdit(task)} className="cursor-pointer">
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => onAddReminder(task)} className="cursor-pointer">
            <Bell className="mr-2 h-4 w-4" />
            Add Reminder
          </DropdownMenuItem>
          {task.reminders && task.reminders.length > 0 && (
            <DropdownMenuItem onClick={() => onManageReminders(task)} className="cursor-pointer">
              <Clock className="mr-2 h-4 w-4" />
              Manage Reminders
            </DropdownMenuItem>
          )}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={handleDelete}
            disabled={isDeleting}
            className="cursor-pointer text-destructive focus:text-destructive"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            {isDeleting ? 'Deleting...' : 'Delete'}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </motion.div>
  );
}
