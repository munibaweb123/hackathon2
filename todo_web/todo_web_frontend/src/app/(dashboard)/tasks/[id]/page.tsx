'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { TaskForm } from '@/components/tasks/task-form';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/hooks/use-auth';
import type { Task, UpdateTaskInput } from '@/types';

const priorityColors = {
  low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
};

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const taskId = parseInt(params.id as string, 10);

  const [task, setTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    async function fetchTask() {
      if (!user?.id) return;

      setIsLoading(true);
      try {
        const data = await apiClient.getTask(user.id, taskId);
        setTask(data);
      } catch (err) {
        toast.error('Failed to load task');
        router.push('/tasks');
      } finally {
        setIsLoading(false);
      }
    }

    fetchTask();
  }, [user?.id, taskId, router]);

  const handleToggleComplete = async () => {
    if (!user?.id || !task) return;

    try {
      const updated = await apiClient.toggleTaskComplete(user.id, task.id);
      setTask(updated);
      toast.success(updated.completed ? 'Task completed!' : 'Task reopened');
    } catch (err) {
      toast.error('Failed to update task');
    }
  };

  const handleUpdate = async (data: UpdateTaskInput) => {
    if (!user?.id || !task) return;

    setIsUpdating(true);
    try {
      const updated = await apiClient.updateTask(user.id, task.id, data);
      setTask(updated);
      setIsEditing(false);
      toast.success('Task updated');
    } catch (err) {
      toast.error('Failed to update task');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!user?.id || !task) return;

    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      await apiClient.deleteTask(user.id, task.id);
      toast.success('Task deleted');
      router.push('/tasks');
    } catch (err) {
      toast.error('Failed to delete task');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (!task) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">Task not found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}>
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
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          Back
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <Checkbox
                checked={task.completed}
                onCheckedChange={handleToggleComplete}
                className="mt-1"
              />
              <div>
                <CardTitle className={task.completed ? 'line-through text-muted-foreground' : ''}>
                  {task.title}
                </CardTitle>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="secondary" className={priorityColors[task.priority]}>
                    {task.priority} priority
                  </Badge>
                  <Badge variant={task.completed ? 'default' : 'outline'}>
                    {task.completed ? 'Completed' : 'Pending'}
                  </Badge>
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
              <Button variant="destructive" size="sm" onClick={handleDelete}>
                Delete
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {task.description && (
            <div>
              <h4 className="text-sm font-medium mb-1">Description</h4>
              <p className="text-muted-foreground">{task.description}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4 text-sm">
            {task.due_date && (
              <div>
                <h4 className="font-medium mb-1">Due Date</h4>
                <p className="text-muted-foreground">
                  {format(new Date(task.due_date), 'MMMM d, yyyy')}
                </p>
              </div>
            )}
            <div>
              <h4 className="font-medium mb-1">Created</h4>
              <p className="text-muted-foreground">
                {format(new Date(task.created_at), 'MMMM d, yyyy')}
              </p>
            </div>
            <div>
              <h4 className="font-medium mb-1">Last Updated</h4>
              <p className="text-muted-foreground">
                {format(new Date(task.updated_at), 'MMMM d, yyyy')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <TaskForm
        open={isEditing}
        onOpenChange={setIsEditing}
        task={task}
        onSubmit={handleUpdate}
        isLoading={isUpdating}
      />
    </div>
  );
}
