'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TaskList } from '@/components/tasks/task-list';
import { TaskForm } from '@/components/tasks/task-form';
import { TaskFilters } from '@/components/tasks/task-filters';
import { useAuth } from '@/hooks/use-auth';
import { useTasks } from '@/hooks/use-tasks';
import type { Task, CreateTaskInput, UpdateTaskInput } from '@/types';

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
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    updateFilters,
  } = useTasks(user?.id);

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      toast.success('Task deleted successfully');
    } catch (err) {
      toast.error('Failed to delete task');
    }
  };

  const handleToggleComplete = async (taskId: string) => {
    try {
      await toggleComplete(taskId);
    } catch (err) {
      toast.error('Failed to update task');
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
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

      {/* Actions Row */}
      <div className="flex flex-col sm:flex-row justify-between gap-4">
        <TaskFilters filters={filters} onFilterChange={updateFilters} />
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
          />
        </CardContent>
      </Card>

      {/* Create Task Form */}
      <TaskForm
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        onSubmit={handleCreateTask}
        isLoading={isSubmitting}
      />

      {/* Edit Task Form */}
      <TaskForm
        open={!!editingTask}
        onOpenChange={(open) => !open && setEditingTask(null)}
        task={editingTask}
        onSubmit={handleUpdateTask}
        isLoading={isSubmitting}
      />
    </div>
  );
}
