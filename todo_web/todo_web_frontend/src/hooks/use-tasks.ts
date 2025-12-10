'use client';

import { useCallback, useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import type { Task, CreateTaskInput, UpdateTaskInput, TaskFilters, ApiError } from '@/types';

export function useTasks(userId: string | undefined) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [filters, setFilters] = useState<TaskFilters>({
    status: 'all',
    sortBy: 'created_at',
    order: 'desc',
  });

  const fetchTasks = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.getTasks(userId, filters);
      // Ensure all tasks have the required fields with default values
      const processedTasks = data.map(task => ({
        ...task,
        is_recurring: task.is_recurring ?? false,
        recurrence_pattern: task.recurrence_pattern,
        recurrence_interval: task.recurrence_interval,
        recurrence_end_date: task.recurrence_end_date,
        parent_task_id: task.parent_task_id,
        reminders: task.reminders ?? [],
      }));
      setTasks(processedTasks);
    } catch (err) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  }, [userId, filters]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = useCallback(async (input: CreateTaskInput) => {
    if (!userId) throw new Error('User not authenticated');

    setIsLoading(true);
    setError(null);
    try {
      const newTask = await apiClient.createTask(userId, input);
      // Ensure the new task has the required fields with default values
      const processedTask = {
        ...newTask,
        is_recurring: newTask.is_recurring ?? false,
        recurrence_pattern: newTask.recurrence_pattern,
        recurrence_interval: newTask.recurrence_interval,
        recurrence_end_date: newTask.recurrence_end_date,
        parent_task_id: newTask.parent_task_id,
        reminders: newTask.reminders ?? [],
      };
      setTasks((prev) => [processedTask, ...prev]);
      return processedTask;
    } catch (err) {
      setError(err as ApiError);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const updateTask = useCallback(async (taskId: string, input: UpdateTaskInput) => {
    if (!userId) throw new Error('User not authenticated');

    setIsLoading(true);
    setError(null);
    try {
      const updatedTask = await apiClient.updateTask(userId, taskId, input);
      // Ensure the updated task has the required fields with default values
      const processedTask = {
        ...updatedTask,
        is_recurring: updatedTask.is_recurring ?? false,
        recurrence_pattern: updatedTask.recurrence_pattern,
        recurrence_interval: updatedTask.recurrence_interval,
        recurrence_end_date: updatedTask.recurrence_end_date,
        parent_task_id: updatedTask.parent_task_id,
        reminders: updatedTask.reminders ?? [],
      };
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? processedTask : task))
      );
      return processedTask;
    } catch (err) {
      setError(err as ApiError);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const deleteTask = useCallback(async (taskId: string) => {
    if (!userId) throw new Error('User not authenticated');

    setIsLoading(true);
    setError(null);
    try {
      await apiClient.deleteTask(userId, taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err) {
      setError(err as ApiError);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const toggleComplete = useCallback(async (taskId: string) => {
    if (!userId) throw new Error('User not authenticated');

    try {
      const updatedTask = await apiClient.toggleTaskComplete(userId, taskId);
      // Ensure the updated task has the required fields with default values
      const processedTask = {
        ...updatedTask,
        is_recurring: updatedTask.is_recurring ?? false,
        recurrence_pattern: updatedTask.recurrence_pattern,
        recurrence_interval: updatedTask.recurrence_interval,
        recurrence_end_date: updatedTask.recurrence_end_date,
        parent_task_id: updatedTask.parent_task_id,
        reminders: updatedTask.reminders ?? [],
      };
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? processedTask : task))
      );
      return processedTask;
    } catch (err) {
      setError(err as ApiError);
      throw err;
    }
  }, [userId]);

  const updateFilters = useCallback((newFilters: Partial<TaskFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

  // Computed values
  const completedCount = tasks.filter((t) => t.completed).length;
  const pendingCount = tasks.filter((t) => !t.completed).length;

  return {
    tasks,
    isLoading,
    error,
    filters,
    completedCount,
    pendingCount,
    totalCount: tasks.length,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    updateFilters,
  };
}
