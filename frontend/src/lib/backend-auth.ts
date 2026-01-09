/**
 * Alternative authentication using backend endpoints directly.
 * This allows using existing backend users with their original credentials.
 */

import axios from 'axios';
import { clearCachedToken } from '@/services/auth/api-client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterCredentials {
  email: string;
  password: string;
  name?: string;
}

interface AuthResponse {
  success: boolean;
  user: {
    id: string;
    email: string;
    name?: string;
  };
  accessToken: string;
  refreshToken: string;
  tokenType: string;
}

/**
 * Login using backend authentication
 */
export async function backendLogin(credentials: LoginCredentials): Promise<AuthResponse> {
  try {
    const response = await axios.post<AuthResponse>(
      `${API_BASE_URL}/api/auth/login`,
      credentials,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    // Store tokens in localStorage for API client
    if (response.data.accessToken) {
      localStorage.setItem('access_token', response.data.accessToken);
    }
    if (response.data.refreshToken) {
      localStorage.setItem('refresh_token', response.data.refreshToken);
    }

    return response.data;
  } catch (error) {
    console.error('Backend login failed:', error);

    // Clear any existing tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.response?.data?.message || 'Login failed');
    }
    throw new Error('Login failed');
  }
}

/**
 * Register using backend authentication
 */
export async function backendRegister(credentials: RegisterCredentials): Promise<AuthResponse> {
  try {
    const response = await axios.post<AuthResponse>(
      `${API_BASE_URL}/api/auth/register`,
      credentials,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    // Store tokens in localStorage for API client
    if (response.data.accessToken) {
      localStorage.setItem('access_token', response.data.accessToken);
    }
    if (response.data.refreshToken) {
      localStorage.setItem('refresh_token', response.data.refreshToken);
    }

    return response.data;
  } catch (error) {
    console.error('Backend registration failed:', error);

    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.response?.data?.message || 'Registration failed');
    }
    throw new Error('Registration failed');
  }
}

/**
 * Logout from backend
 */
export async function backendLogout(): Promise<void> {
  try {
    await axios.post(
      `${API_BASE_URL}/api/auth/logout`,
      {},
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      }
    );
  } catch (error) {
    console.warn('Backend logout failed:', error);
  } finally {
    // Always clear local tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    clearCachedToken();
  }
}

/**
 * Get current user info from backend
 */
export async function getCurrentUser(): Promise<AuthResponse['user']> {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No access token available');
  }

  try {
    const response = await axios.get<{ user: AuthResponse['user'] }>(
      `${API_BASE_URL}/api/auth/me`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    return response.data.user;
  } catch (error) {
    console.error('Get user failed:', error);
    throw new Error('Failed to get user information');
  }
}