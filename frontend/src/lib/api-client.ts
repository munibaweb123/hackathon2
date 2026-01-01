import axios, { AxiosInstance, AxiosError } from 'axios';
import { Task, CreateTaskInput, UpdateTaskInput, TaskFilters, ApiError, Reminder, ReminderType, ReminderStatus, UserPreference } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add JWT token to requests
    this.client.interceptors.request.use(
      async (config) => {
        // Try to get JWT token from Better Auth session
        try {
          const { getJwtToken } = await import('./auth-client');
          const token = await getJwtToken();

          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          } else {
            // If no JWT token, fall back to cookie-based auth
            config.withCredentials = true;
          }
        } catch (error) {
          console.error('Error getting JWT token:', error);
          // Fall back to cookie-based auth
          config.withCredentials = true;
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    // NOTE: We intentionally do NOT redirect on 401 here.
    // The auth layer (DashboardLayout) handles showing login prompt.
    // Redirecting here causes race conditions during initial page load.
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Session expired or invalid - log but DON'T redirect
          console.warn('[apiClient] 401 Unauthorized - auth layer will handle redirect');
        }
        return Promise.reject(this.formatError(error));
      }
    );
  }

  // Token management methods for compatibility
  setToken(token: string): void {
    // For cookie-based auth, we don't need to set tokens in headers
    // The token is managed automatically by Better Auth via cookies
  }

  loadToken(): void {
    // For cookie-based auth, we don't need to load tokens from storage
    // The token is managed automatically by Better Auth via cookies
  }

  clearToken(): void {
    // For cookie-based auth, we don't need to clear tokens from headers
    // The token is managed automatically by Better Auth via cookies
  }

  private formatError(error: AxiosError): ApiError {
    // Handle different possible error response formats
    let message = 'An unexpected error occurred';

    if (error.response?.data) {
      const responseData = error.response.data;

      // Check for FastAPI validation error format
      if (Array.isArray(responseData) && responseData.length > 0) {
        // Pydantic validation errors are returned as an array
        const validationErrors = responseData as Array<{loc: string[], msg: string, type: string}>;
        message = validationErrors.map(err =>
          `${err.loc.join('.')}: ${err.msg}`
        ).join('; ');
      } else if (typeof responseData === 'object' && responseData !== null) {
        // Check for standard detail field
        if ('detail' in responseData && typeof responseData.detail === 'string') {
          message = responseData.detail;
        } else if ('message' in responseData && typeof responseData.message === 'string') {
          message = responseData.message;
        } else if (Object.keys(responseData).length === 0) {
          // If response is an empty object, provide a more descriptive message
          message = `Request failed with status ${error.response.status}. Empty response received.`;
        } else {
          // Try to convert the object to a string representation
          message = JSON.stringify(responseData);
        }
      } else if (typeof responseData === 'string') {
        message = responseData;
      }
    } else if (error.message) {
      message = error.message;
    } else if (error.code) {
      message = `Network error: ${error.code}`;
    }

    return {
      message,
      status: error.response?.status || 500,
    };
  }

  // Task API methods
  async getTasks(filters?: TaskFilters): Promise<Task[]> {
    const params = new URLSearchParams();
    if (filters?.status && filters.status !== 'all') {
      params.append('status', filters.status);
    }
    if (filters?.sortBy) {
      params.append('sort', filters.sortBy);
    }
    if (filters?.order) {
      params.append('order', filters.order);
    }

    const response = await this.client.get<{ tasks: Task[]; total: number }>(
      `/api/tasks${params.toString() ? '?' + params.toString() : ''}`
    );
    return response.data.tasks;
  }

  async getTask(taskId: number): Promise<Task> {
    const response = await this.client.get<Task>(`/api/tasks/${taskId}`);
    return response.data;
  }

  async createTask(input: CreateTaskInput): Promise<Task> {
    const response = await this.client.post<Task>(`/api/tasks`, input);
    return response.data;
  }

  async updateTask(taskId: number, input: UpdateTaskInput): Promise<Task> {
    const response = await this.client.put<Task>(`/api/tasks/${taskId}`, input);
    return response.data;
  }

  async deleteTask(taskId: number): Promise<void> {
    await this.client.delete(`/api/tasks/${taskId}`);
  }

  async toggleTaskComplete(taskId: number): Promise<Task> {
    const response = await this.client.patch<Task>(`/api/tasks/${taskId}/complete`);
    return response.data;
  }

  // Reminder API methods
  async getReminders(status?: string): Promise<Reminder[]> {
    const params = new URLSearchParams();
    if (status) {
      params.append('status', status);
    }

    const response = await this.client.get<{ reminders: Reminder[]; total: number }>(
      `/api/reminders${params.toString() ? '?' + params.toString() : ''}`
    );
    return response.data.reminders;
  }

  async getReminder(reminderId: string): Promise<Reminder> {
    const response = await this.client.get<Reminder>(`/api/reminders/${reminderId}`);
    return response.data;
  }

  async createReminder(input: { task_id: number; reminder_time: string; reminder_type?: ReminderType; message?: string }): Promise<Reminder> {
    const response = await this.client.post<Reminder>(`/api/reminders`, input);
    return response.data;
  }

  async updateReminder(reminderId: string, input: { reminder_time?: string; reminder_type?: ReminderType; status?: ReminderStatus; message?: string }): Promise<Reminder> {
    const response = await this.client.put<Reminder>(`/api/reminders/${reminderId}`, input);
    return response.data;
  }

  async deleteReminder(reminderId: string): Promise<void> {
    await this.client.delete(`/api/reminders/${reminderId}`);
  }

  async cancelReminder(reminderId: string): Promise<Reminder> {
    const response = await this.client.patch<Reminder>(`/api/reminders/${reminderId}/cancel`);
    return response.data;
  }

  // User Preference API methods
  async getUserPreferences(): Promise<UserPreference> {
    const response = await this.client.get<UserPreference>(`/api/preferences`);
    return response.data;
  }

  async createUserPreferences(input: Partial<UserPreference>): Promise<UserPreference> {
    const response = await this.client.post<UserPreference>(`/api/preferences`, input);
    return response.data;
  }

  async updateUserPreferences(input: Partial<UserPreference>): Promise<UserPreference> {
    const response = await this.client.put<UserPreference>(`/api/preferences`, input);
    return response.data;
  }

  async patchUserPreferences(input: Partial<UserPreference>): Promise<UserPreference> {
    const response = await this.client.patch<UserPreference>(`/api/preferences`, input);
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
