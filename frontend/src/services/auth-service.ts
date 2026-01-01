/** Authentication service for the Todo Web Application */

import axios, { AxiosResponse } from 'axios';
import {
  User,
  UserRegistrationRequest,
  UserRegistrationResponse,
  UserLoginRequest,
  UserLoginResponse,
  TokenRefreshRequest,
  TokenRefreshResponse,
  PasswordResetRequest,
  PasswordResetResponse,
  PasswordResetConfirmRequest,
  UserProfileUpdateRequest,
  UserProfileResponse,
  AuthErrorResponse,
  LogoutResponse
} from '@/types/auth';

// Base API URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance for auth requests
const authApi = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
authApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
// NOTE: We intentionally do NOT redirect on 401 here.
// The auth layer (DashboardLayout) handles showing login prompt.
// Redirecting here causes race conditions during initial page load.
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If token is expired and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          // No refresh token - just clear and let auth layer handle it
          localStorage.removeItem('access_token');
          console.warn('[authApi] No refresh token, auth layer will handle redirect');
          return Promise.reject(error);
        }

        // Attempt to refresh the token
        const response = await refreshTokenApi({
          refreshToken
        });

        if (response.accessToken) {
          localStorage.setItem('access_token', response.accessToken);
          localStorage.setItem('refresh_token', response.refreshToken);

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${response.accessToken}`;
          return authApi(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens - auth layer will handle redirect
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        console.warn('[authApi] Token refresh failed, auth layer will handle redirect');
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Register a new user
 */
export const registerUser = async (
  userData: UserRegistrationRequest
): Promise<UserRegistrationResponse> => {
  try {
    const response: AxiosResponse<UserRegistrationResponse> = await authApi.post(
      '/auth/register',
      userData
    );

    // Store tokens if registration is successful and returns them
    if (response.data.success && response.data.user) {
      if (response.data.accessToken) {
        localStorage.setItem('access_token', response.data.accessToken);
      }
      if (response.data.refreshToken) {
        localStorage.setItem('refresh_token', response.data.refreshToken);
      }
    }

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const authError: AuthErrorResponse = {
        success: false,
        error: {
          message: error.response.data.message || error.response.data.detail || 'Registration failed',
          code: error.response.data.code || 'REGISTRATION_ERROR',
        }
      };
      throw authError;
    }
    throw error;
  }
};

/**
 * Login user
 */
export const loginUser = async (
  loginData: UserLoginRequest
): Promise<UserLoginResponse> => {
  try {
    const response: AxiosResponse<UserLoginResponse> = await authApi.post(
      '/auth/login',
      loginData
    );

    // Store tokens on successful login
    if (response.data.success) {
      localStorage.setItem('access_token', response.data.accessToken);
      localStorage.setItem('refresh_token', response.data.refreshToken);
    }

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const authError: AuthErrorResponse = {
        success: false,
        error: {
          message: error.response.data.message || error.response.data.detail || 'Login failed',
          code: error.response.data.code || 'LOGIN_ERROR',
        }
      };
      throw authError;
    }
    throw error;
  }
};

/**
 * Logout user
 */
export const logoutUser = async (): Promise<LogoutResponse> => {
  try {
    const response: AxiosResponse<LogoutResponse> = await authApi.post('/auth/logout');

    // Clear tokens on logout
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    return response.data;
  } catch (error) {
    // Even if backend logout fails, clear local tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    const logoutResponse: LogoutResponse = {
      success: true,
      message: 'Logged out successfully'
    };

    return logoutResponse;
  }
};

/**
 * Get current user profile
 */
export const getCurrentUser = async (): Promise<User> => {
  try {
    const response: AxiosResponse<{ user: User }> = await authApi.get('/auth/me');
    return response.data.user;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      // Token expired, clear local tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    throw error;
  }
};

/**
 * Refresh access token
 */
export const refreshTokenApi = async (
  refreshData: TokenRefreshRequest
): Promise<TokenRefreshResponse> => {
  try {
    const response: AxiosResponse<TokenRefreshResponse> = await authApi.post(
      '/auth/refresh',
      refreshData
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const authError: AuthErrorResponse = {
        success: false,
        error: {
          message: error.response.data.message || error.response.data.detail || 'Token refresh failed',
          code: error.response.data.code || 'TOKEN_REFRESH_ERROR',
        }
      };
      throw authError;
    }
    throw error;
  }
};

/**
 * Request password reset
 */
export const requestPasswordReset = async (
  resetData: PasswordResetRequest
): Promise<PasswordResetResponse> => {
  try {
    const response: AxiosResponse<PasswordResetResponse> = await authApi.post(
      '/auth/forgot-password',
      resetData
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const authError: AuthErrorResponse = {
        success: false,
        error: {
          message: error.response.data.message || error.response.data.detail || 'Password reset request failed',
          code: error.response.data.code || 'PASSWORD_RESET_ERROR',
        }
      };
      throw authError;
    }
    throw error;
  }
};

/**
 * Confirm password reset
 */
export const confirmPasswordReset = async (
  resetData: PasswordResetConfirmRequest
): Promise<PasswordResetResponse> => {
  try {
    const response: AxiosResponse<PasswordResetResponse> = await authApi.post(
      '/auth/reset-password',
      resetData
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const authError: AuthErrorResponse = {
        success: false,
        error: {
          message: error.response.data.message || error.response.data.detail || 'Password reset failed',
          code: error.response.data.code || 'PASSWORD_RESET_ERROR',
        }
      };
      throw authError;
    }
    throw error;
  }
};

/**
 * Update user profile
 */
export const updateUserProfile = async (
  profileData: UserProfileUpdateRequest
): Promise<UserProfileResponse> => {
  try {
    const response: AxiosResponse<{ user: UserProfileResponse }> = await authApi.put(
      '/users/profile',
      profileData
    );
    return response.data.user;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const authError: AuthErrorResponse = {
        success: false,
        error: {
          message: error.response.data.message || error.response.data.detail || 'Profile update failed',
          code: error.response.data.code || 'PROFILE_UPDATE_ERROR',
        }
      };
      throw authError;
    }
    throw error;
  }
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('access_token');
  return !!token;
};

/**
 * Get access token
 */
export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

/**
 * Clear all auth tokens
 */
export const clearAuthTokens = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export default authApi;