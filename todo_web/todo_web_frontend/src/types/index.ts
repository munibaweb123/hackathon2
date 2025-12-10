// Recurrence Types
export type RecurrencePattern = 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'yearly' | 'custom';

// Reminder Types
export type ReminderType = 'email' | 'push' | 'sms';
export type ReminderStatus = 'pending' | 'sent' | 'cancelled';

export interface Reminder {
  id: string;
  task_id: string;
  user_id: string;
  reminder_time: string; // ISO date string
  reminder_type: ReminderType;
  status: ReminderStatus;
  message?: string;
  created_at: string;
  updated_at: string;
}

// User Preference Types
export type Theme = 'light' | 'dark' | 'auto';
export type NotificationPreference = 'all' | 'mute' | 'scheduled';

export interface UserPreference {
  id: string;
  user_id: string;
  theme: Theme;
  language: string;
  task_notifications: NotificationPreference;
  reminder_notifications: NotificationPreference;
  email_notifications: boolean;
  default_view: string;
  show_completed_tasks: boolean;
  group_by: string;
  auto_archive_completed: boolean;
  auto_snooze_time?: number;
  work_hours_start: string;
  work_hours_end: string;
  custom_settings?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Task Types
export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  created_at: string;
  updated_at: string;
  user_id: string;

  // Recurring task fields
  is_recurring: boolean;
  recurrence_pattern?: RecurrencePattern;
  recurrence_interval?: number;
  recurrence_end_date?: string;
  parent_task_id?: string;

  // Include reminders in the response
  reminders?: Reminder[];
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;

  // Recurring task fields
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
  recurrence_interval?: number;
  recurrence_end_date?: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  completed?: boolean;

  // Recurring task fields
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
  recurrence_interval?: number;
  recurrence_end_date?: string;
}

// User Types
export interface User {
  id: string;
  email: string;
  name?: string;
  image?: string;
  created_at: string;
}

// Auth Types
export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  message: string;
  status: number;
}

// Filter Types
export type TaskStatus = 'all' | 'pending' | 'completed';
export type TaskSortBy = 'created_at' | 'due_date' | 'priority' | 'title';
export type SortOrder = 'asc' | 'desc';

export interface TaskFilters {
  status: TaskStatus;
  sortBy: TaskSortBy;
  order: SortOrder;
}
