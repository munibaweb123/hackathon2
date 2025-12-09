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
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  completed?: boolean;
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
