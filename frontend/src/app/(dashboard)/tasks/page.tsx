'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TaskList } from '@/components/tasks/task-list';
import { TaskForm } from '@/components/tasks/task-form';
import { TaskFilters } from '@/components/tasks/task-filters';
import { ReminderForm } from '@/components/reminders/reminder-form';
import { SearchBar } from '@/components/tasks/SearchBar';
import { DateRangeFilter } from '@/components/tasks/DateRangeFilter';
import { ConnectionStatusBadge } from '@/components/layout/ConnectionStatus';
import { useAuth } from '@/hooks/use-auth';
import { useTasks } from '@/hooks/use-tasks';
import { useRealtimeSync, TaskUpdateEvent } from '@/hooks/use-realtime-sync';
import { jwtApiClient } from '@/services/auth/api-client';
import { apiClient } from '@/lib/api-client';
import type { Task, CreateTaskInput, UpdateTaskInput, Reminder, Tag, TaskFilters as TaskFiltersType } from '@/types';

export default function TasksPage() {
  const { user } = useAuth();
  const {
    tasks,
    isLoading,
    error,
    filters,
    completedCount,
    pendingCount,
    totalCount,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    updateFilters,
  } = useTasks();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showReminderForm, setShowReminderForm] = useState(false);
  const [selectedTaskForReminder, setSelectedTaskForReminder] = useState<Task | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [dueBefore, setDueBefore] = useState<Date | undefined>(undefined);
  const [dueAfter, setDueAfter] = useState<Date | undefined>(undefined);
  const [allTags, setAllTags] = useState<Tag[]>([]);

  // Real-time sync handlers
  const handleTaskCreated = useCallback((event: TaskUpdateEvent) => {
    toast.info(`New task added: ${event.task_id}`);
    fetchTasks(); // Refetch to get the new task
  }, [fetchTasks]);

  const handleTaskUpdated = useCallback((event: TaskUpdateEvent) => {
    toast.info(`Task updated: ${event.task_id}`);
    fetchTasks(); // Refetch to get updated data
  }, [fetchTasks]);

  const handleTaskDeleted = useCallback((event: TaskUpdateEvent) => {
    toast.info(`Task deleted: ${event.task_id}`);
    fetchTasks(); // Refetch to remove deleted task
  }, [fetchTasks]);

  const handleTaskCompleted = useCallback((event: TaskUpdateEvent) => {
    toast.success(`Task completed: ${event.task_id}`);
    fetchTasks(); // Refetch to update status
  }, [fetchTasks]);

  // Set up real-time sync
  const { isConnected } = useRealtimeSync({
    onTaskCreated: handleTaskCreated,
    onTaskUpdated: handleTaskUpdated,
    onTaskDeleted: handleTaskDeleted,
    onTaskCompleted: handleTaskCompleted,
    autoConnect: true,
  });

  // Fetch tags on component mount
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const tags = await apiClient.getTags();
        setAllTags(tags);
      } catch (err) {
        console.error('Failed to fetch tags:', err);
        // Don't show error toast - tags are optional
      }
    };

    fetchTags();
  }, []);

  // Enhanced updateFilters to handle search and date range
  const handleUpdateFilters = (newFilters: Partial<TaskFiltersType>) => {
    // Update search and date range filters separately
    if (newFilters.searchQuery !== undefined) {
      setSearchQuery(newFilters.searchQuery);
    }
    if (newFilters.dueBefore !== undefined) {
      setDueBefore(newFilters.dueBefore ? new Date(newFilters.dueBefore) : undefined);
    }
    if (newFilters.dueAfter !== undefined) {
      setDueAfter(newFilters.dueAfter ? new Date(newFilters.dueAfter) : undefined);
    }

    // Update the main filters
    updateFilters(newFilters);
  };

  const handleSearchChange = useCallback((query: string) => {
    updateFilters({ searchQuery: query });
  }, [updateFilters]);

  const handleDueBeforeChange = useCallback((date: Date | undefined) => {
    setDueBefore(date);
    updateFilters({ dueBefore: date ? date.toISOString() : undefined });
  }, [updateFilters]);

  const handleDueAfterChange = useCallback((date: Date | undefined) => {
    setDueAfter(date);
    updateFilters({ dueAfter: date ? date.toISOString() : undefined });
  }, [updateFilters]);

  const handleCreateTask = async (data: CreateTaskInput) => {
    setIsSubmitting(true);
    try {
      await createTask(data);
      toast.success('Task created successfully');
    } catch (err) {
      toast.error('Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateTask = async (data: UpdateTaskInput) => {
    if (!editingTask) return;
    setIsSubmitting(true);
    try {
      await updateTask(editingTask.id, data);
      setEditingTask(null);
      toast.success('Task updated successfully');
    } catch (err) {
      toast.error('Failed to update task');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      toast.success('Task deleted successfully');
    } catch (err) {
      toast.error('Failed to delete task');
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    try {
      await toggleComplete(taskId);
    } catch (err) {
      toast.error('Failed to update task');
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
  };

  const handleAddReminder = (task: Task) => {
    setSelectedTaskForReminder(task);
    setShowReminderForm(true);
  };

  const handleManageReminders = (task: Task) => {
    // In a real implementation, this would navigate to a reminders page
    // For now, we'll just show a toast
    toast.info(`Managing reminders for task: ${task.title}`);
  };

  const handleCreateReminder = async (data: { task_id: number; reminder_time: string; reminder_type?: 'email' | 'push' | 'sms'; message?: string }) => {
    try {
      await jwtApiClient.createReminder(data);
      toast.success('Reminder created successfully');
      setShowReminderForm(false);
      setSelectedTaskForReminder(null);

      // Refetch tasks to update the list with the new reminder
      fetchTasks();
    } catch (err) {
      console.error('Failed to create reminder:', err);
      toast.error('Failed to create reminder');
    }
  };

  return (
    <div className="space-y-6">
      {/* Connection Status Badge */}
      <ConnectionStatusBadge />

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Tasks</CardDescription>
            <CardTitle className="text-3xl">{totalCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Pending</CardDescription>
            <CardTitle className="text-3xl text-orange-600">{pendingCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Completed</CardDescription>
            <CardTitle className="text-3xl text-green-600">{completedCount}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Filters Row */}
      <div className="flex flex-col lg:flex-row gap-4 justify-between">
        <div className="flex flex-col gap-4 w-full lg:w-auto">
          <div className="flex flex-col sm:flex-row gap-2">
            <TaskFilters filters={filters} onFilterChange={updateFilters} />
          </div>

          {/* Search and Date Range */}
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="flex-1 max-w-md">
              <SearchBar
                value={filters.searchQuery || ''}
                onChange={handleSearchChange}
                placeholder="Search tasks..."
              />
            </div>
            <DateRangeFilter
              startDate={dueAfter}
              endDate={dueBefore}
              onStartDateChange={handleDueAfterChange}
              onEndDateChange={handleDueBeforeChange}
            />
          </div>
        </div>
        <Button onClick={() => setIsFormOpen(true)}>
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
          Add Task
        </Button>
      </div>

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error.message}</p>
          </CardContent>
        </Card>
      )}

      {/* Task List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Tasks</CardTitle>
          <CardDescription>
            Manage your tasks and stay organized
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TaskList
            tasks={tasks}
            isLoading={isLoading}
            onToggleComplete={handleToggleComplete}
            onEdit={handleEdit}
            onDelete={handleDeleteTask}
            onAddReminder={handleAddReminder}
            onManageReminders={handleManageReminders}
          />
        </CardContent>
      </Card>

      {/* Create Task Form */}
      <TaskForm
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        allTags={allTags}
        onSubmit={handleCreateTask}
        isLoading={isSubmitting}
      />

      {/* Edit Task Form */}
      <TaskForm
        open={!!editingTask}
        onOpenChange={(open) => !open && setEditingTask(null)}
        task={editingTask}
        allTags={allTags}
        onSubmit={handleUpdateTask}
        isLoading={isSubmitting}
      />

      {/* Reminder Form */}
      <ReminderForm
        open={showReminderForm}
        onOpenChange={setShowReminderForm}
        taskId={selectedTaskForReminder?.id || 0}
        onSubmit={handleCreateReminder}
        isLoading={false}
      />
    </div>
  );
}
