'use client';

import { useCallback, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession, signIn, signUp, signOut, clearStoredToken } from '@/lib/auth-client';
import { clearCachedToken } from '@/services/auth/api-client';
import { loginUser, registerUser } from '@/services/auth-service';
import type { User, LoginInput, RegisterInput } from '@/types';

export function useAuth() {
  const router = useRouter();
  const { data: session, isPending, error, refetch } = useSession();
  const [isLoading, setIsLoading] = useState(false);

  // Debug logging for session state
  useEffect(() => {
    console.log('[useAuth] Session state:', {
      sessionRaw: session,
      sessionUser: session?.user,
      sessionSession: session?.session,
      isPending,
      error: error?.message || null,
      isAuthenticated: !!session?.user,
    });
  }, [session, isPending, error]);

  const login = useCallback(async (input: LoginInput) => {
    setIsLoading(true);
    try {
      console.log('[useAuth] Starting backend login...');

      // Use the backend authentication service instead of Better Auth directly
      // This allows us to authenticate users that exist in the backend database
      const result = await loginUser({
        email: input.email,
        password: input.password,
      });

      console.log('[useAuth] Backend login result:', {
        success: result.success,
        user: result.user,
      });

      if (!result.success) {
        throw new Error('Login failed');
      }

      console.log('[useAuth] Login successful, redirecting to /tasks...');

      // Use window.location for reliable redirect
      window.location.href = '/tasks';

      return result;
    } catch (err) {
      console.error('[useAuth] Login error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (input: RegisterInput) => {
    setIsLoading(true);
    try {
      console.log('[useAuth] Starting backend registration...');

      // Use the backend authentication service instead of Better Auth directly
      const result = await registerUser({
        email: input.email,
        password: input.password,
        name: input.name || '',
      });

      console.log('[useAuth] Backend registration result:', {
        success: result.success,
        user: result.user,
      });

      if (!result.success) {
        throw new Error('Registration failed');
      }

      console.log('[useAuth] Registration successful, redirecting to /tasks...');

      // Use window.location for reliable redirect
      window.location.href = '/tasks';

      return result;
    } catch (err) {
      console.error('[useAuth] Registration error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      // Clear cached tokens
      clearCachedToken();
      clearStoredToken();

      // Use backend logout as well if needed
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        console.log('[useAuth] Backend logout response:', response.status);
      } catch (logoutErr) {
        console.warn('[useAuth] Backend logout failed:', logoutErr);
      }

      // Clear local tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');

      router.push('/login');
      router.refresh();
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  // Get user info from backend authentication
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    // Check if user is authenticated by trying to get user info
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setCurrentUser(null);
        setAuthChecked(true);
        return;
      }

      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setCurrentUser({
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
          });
        } else {
          console.log('[useAuth] User not authenticated via backend:', response.status);
          setCurrentUser(null);
          // Clear invalid token
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      } catch (err) {
        console.log('[useAuth] Error checking backend auth:', err);
        setCurrentUser(null);
      } finally {
        setAuthChecked(true);
      }
    };

    checkAuth();
  }, []);

  return {
    user: currentUser,
    isAuthenticated: !!currentUser && authChecked,
    isLoading: isLoading || (!authChecked && isPending),
    error,
    login,
    register,
    logout,
    refetch: () => {}, // Backend auth doesn't use session refetch
  };
}