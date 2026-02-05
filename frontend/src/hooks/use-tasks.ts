'use client';

import { useCallback, useEffect, useState, useRef, useMemo } from 'react';
import { jwtApiClient } from '@/services/auth/api-client';
import type { Task, CreateTaskInput, UpdateTaskInput, TaskFilters, ApiError } from '@/types';

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [filters, setFilters] = useState<TaskFilters>({
    status: 'all',
    sortBy: 'created_at',
    order: 'desc',
    priority: undefined,
    searchQuery: '',
    dueBefore: undefined,
    dueAfter: undefined,
  });

  // Create a stable key for filters to prevent unnecessary fetches
  const filtersKey = useMemo(() => {
    return JSON.stringify({
      status: filters.status,
      priority: filters.priority,
      searchQuery: filters.searchQuery,
      dueBefore: filters.dueBefore,
      dueAfter: filters.dueAfter,
      sortBy: filters.sortBy,
      order: filters.order,
    });
  }, [
    filters.status,
    filters.priority,
    filters.searchQuery,
    filters.dueBefore,
    filters.dueAfter,
    filters.sortBy,
    filters.order
  ]);

  const previousFiltersKeyRef = useRef<string | null>(null);

  useEffect(() => {
    // Fetch on first mount or when filters change
    if (previousFiltersKeyRef.current === filtersKey) {
      return;
    }

    previousFiltersKeyRef.current = filtersKey;

    const fetchTasks = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await jwtApiClient.getTasks(filters);
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
    };

    fetchTasks();
  }, [filtersKey]);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await jwtApiClient.getTasks(filters);
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
  }, [filters]);

  const createTask = useCallback(async (input: CreateTaskInput) => {
    setIsLoading(true);
    setError(null);
    try {
      const newTask = await jwtApiClient.createTask(input);
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
  }, []);

  const updateTask = useCallback(async (taskId: number, input: UpdateTaskInput) => {
    setError(null);

    // Optimistic update: save previous state for rollback
    const previousTasks = [...tasks];

    // Apply optimistic update
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId
          ? { ...task, ...input, updated_at: new Date().toISOString() }
          : task
      )
    );

    try {
      const updatedTask = await jwtApiClient.updateTask(taskId, input);
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
      // Update with actual server response
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? processedTask : task))
      );
      return processedTask;
    } catch (err) {
      // Rollback on error
      setTasks(previousTasks);
      setError(err as ApiError);
      throw err;
    }
  }, [tasks]);

  const deleteTask = useCallback(async (taskId: number) => {
    setError(null);

    // Optimistic delete: save previous state for rollback
    const previousTasks = [...tasks];

    // Apply optimistic delete
    setTasks((prev) => prev.filter((task) => task.id !== taskId));

    try {
      await jwtApiClient.deleteTask(taskId);
    } catch (err) {
      // Rollback on error
      setTasks(previousTasks);
      setError(err as ApiError);
      throw err;
    }
  }, [tasks]);

  const toggleComplete = useCallback(async (taskId: number) => {
    setError(null);

    // Optimistic toggle: save previous state for rollback
    const previousTasks = [...tasks];

    // Apply optimistic toggle
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId
          ? { ...task, completed: !task.completed, updated_at: new Date().toISOString() }
          : task
      )
    );

    try {
      const updatedTask = await jwtApiClient.toggleTaskComplete(taskId);
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
      // Update with actual server response
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? processedTask : task))
      );
      return processedTask;
    } catch (err) {
      // Rollback on error
      setTasks(previousTasks);
      setError(err as ApiError);
      throw err;
    }
  }, [tasks]);

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