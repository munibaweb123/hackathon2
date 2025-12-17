import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { Task, CreateTaskInput, UpdateTaskInput, TaskFilters, ApiError, Reminder, ReminderType, ReminderStatus, UserPreference } from '@/types';
import { getJwtToken } from '@/lib/auth-client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Cache the JWT token to avoid fetching it on every request
let cachedToken: string | null = null;
let tokenFetchPromise: Promise<string | null> | null = null;

async function getToken(): Promise<string | null> {
  // If we have a cached token, return it
  if (cachedToken) {
    return cachedToken;
  }

  // If a fetch is already in progress, wait for it
  if (tokenFetchPromise) {
    return tokenFetchPromise;
  }

  // Start a new fetch
  tokenFetchPromise = getJwtTokenWithRetry().then((token) => {
    cachedToken = token;
    tokenFetchPromise = null;
    return token;
  }).catch((error) => {
    console.error('Error fetching JWT token:', error);
    tokenFetchPromise = null;
    return null;
  });

  return tokenFetchPromise;
}

// Enhanced function to get JWT token with retry logic
async function getJwtTokenWithRetry(maxRetries: number = 3): Promise<string | null> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const token = await getJwtToken();
      if (token) {
        console.debug(`JWT token retrieved on attempt ${attempt + 1}`);
        return token;
      }

      if (attempt < maxRetries - 1) {
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, 300 * (attempt + 1))); // Increasing delay
      }
    } catch (error) {
      console.error(`Attempt ${attempt + 1} to get JWT token failed:`, error);
      if (attempt >= maxRetries - 1) {
        throw error;
      }
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, 300 * (attempt + 1)));
    }
  }
  return null;
}

// Function to clear cached token (call this on logout or auth errors)
export function clearCachedToken(): void {
  cachedToken = null;
  tokenFetchPromise = null;
}

class JwtApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      // Still enable credentials for cookie fallback if needed
      withCredentials: true,
    });

    // Request interceptor to add JWT token to requests
    this.client.interceptors.request.use(
      async (config: InternalAxiosRequestConfig) => {
        try {
          // Get the JWT token
          const token = await getToken();
          console.debug('JWT token retrieved:', token ? 'Yes' : 'No');

          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.debug('Authorization header set with JWT token');
          } else {
            // If no JWT token is available, the request will still include credentials
            // which should work with Better Auth's cookie-based authentication
            console.debug('No JWT token available, relying on cookie-based auth');
          }
        } catch (error) {
          console.warn('Could not retrieve JWT token for API request:', error);
          // Still make the request, relying on cookie-based authentication
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - token invalid or expired
          // Clear cached token and redirect to login
          clearCachedToken();
          if (typeof window !== 'undefined') {
            localStorage.removeItem('jwt_token');
            sessionStorage.removeItem('jwt_token');
            // Redirect to login page
            window.location.href = '/login';
          }
        } else if (error.response?.status === 403) {
          // Forbidden - user doesn't have access to this resource
          console.error('Access forbidden:', error.response.data);
        }
        return Promise.reject(this.formatError(error));
      }
    );
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

export const jwtApiClient = new JwtApiClient();
export default jwtApiClient;
