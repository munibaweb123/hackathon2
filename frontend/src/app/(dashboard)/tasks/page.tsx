'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TaskList } from '@/components/tasks/task-list';
import { TaskForm } from '@/components/tasks/task-form';
import { TaskFiltersComponent } from '@/components/tasks/TaskFilters';
import { SearchBar } from '@/components/tasks/SearchBar';
import { SortSelector } from '@/components/tasks/SortSelector';
import { DateRangeFilter } from '@/components/tasks/DateRangeFilter';
import { ReminderForm } from '@/components/reminders/reminder-form';
import { useAuth } from '@/hooks/use-auth';
import { useTasks } from '@/hooks/use-tasks';
import { jwtApiClient } from '@/services/auth/api-client';
import type { Task, CreateTaskInput, UpdateTaskInput, TaskSortBy, SortOrder } from '@/types';
import { X, Filter } from 'lucide-react';

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
    hasActiveFilters,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    updateFilters,
    setSearch,
    setDateRange,
    clearFilters,
  } = useTasks();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showReminderForm, setShowReminderForm] = useState(false);
  const [selectedTaskForReminder, setSelectedTaskForReminder] = useState<Task | null>(null);
  const [showFilters, setShowFilters] = useState(false);

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
    toast.info(`Managing reminders for task: ${task.title}`);
  };

  const handleCreateReminder = async (data: { task_id: number; reminder_time: string; reminder_type?: 'email' | 'push' | 'sms'; message?: string }) => {
    try {
      await jwtApiClient.createReminder(data);
      toast.success('Reminder created successfully');
      setShowReminderForm(false);
      setSelectedTaskForReminder(null);
      fetchTasks();
    } catch (err) {
      console.error('Failed to create reminder:', err);
      toast.error('Failed to create reminder');
    }
  };

  const handleSortChange = (sortBy: TaskSortBy, order: SortOrder) => {
    updateFilters({ sortBy, order });
  };

  return (
    <div className="space-y-6">
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

      {/* Search and Actions Row */}
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          {/* Search Bar */}
          <SearchBar
            value={filters.search}
            onChange={setSearch}
            placeholder="Search tasks..."
          />

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className={hasActiveFilters ? 'bg-primary/10' : ''}
            >
              <Filter className="mr-2 h-4 w-4" />
              Filters
              {hasActiveFilters && (
                <span className="ml-1 rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
                  Active
                </span>
              )}
            </Button>
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
        </div>

        {/* Filters Row (Collapsible) */}
        {showFilters && (
          <div className="flex flex-col gap-4 p-4 bg-muted/50 rounded-lg">
            <div className="flex flex-wrap items-center gap-4">
              {/* Status and Priority Filters */}
              <TaskFiltersComponent filters={filters} onFilterChange={updateFilters} />

              {/* Date Range Filter */}
              <DateRangeFilter
                dueAfter={filters.dueAfter}
                dueBefore={filters.dueBefore}
                onDateRangeChange={setDateRange}
              />

              {/* Sort Selector */}
              <SortSelector
                sortBy={filters.sortBy}
                order={filters.order}
                onSortChange={handleSortChange}
              />
            </div>

            {/* Clear All Filters */}
            {hasActiveFilters && (
              <div className="flex justify-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearFilters}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="mr-1 h-4 w-4" />
                  Clear All Filters
                </Button>
              </div>
            )}
          </div>
        )}
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
            {hasActiveFilters
              ? `Showing ${totalCount} filtered results`
              : 'Manage your tasks and stay organized'}
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
        allTags={[]}
        onSubmit={handleCreateTask}
        isLoading={isSubmitting}
      />

      {/* Edit Task Form */}
      <TaskForm
        open={!!editingTask}
        onOpenChange={(open) => !open && setEditingTask(null)}
        task={editingTask}
        allTags={[]}
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
