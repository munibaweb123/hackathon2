'use client';

import { useCallback, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession, signIn, signUp, signOut, getSession, clearStoredToken } from '@/lib/auth-client';
import { clearCachedToken } from '@/services/auth/api-client';
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
      console.log('[useAuth] Starting login...');
      const result = await signIn.email({
        email: input.email,
        password: input.password,
      }, {
        // Capture bearer token from response headers
        onSuccess: (ctx) => {
          const authToken = ctx.response.headers.get('set-auth-token');
          if (authToken) {
            console.log('[useAuth] Storing bearer token from login response');
            localStorage.setItem('bearer_token', authToken);
          }
        }
      });

      console.log('[useAuth] signIn.email result:', {
        hasData: !!result.data,
        hasError: !!result.error,
        error: result.error?.message
      });

      if (result.error) {
        throw new Error(result.error.message || 'Login failed');
      }

      console.log('[useAuth] Login successful, fetching JWT token...');

      // Fetch and store JWT token for API calls
      try {
        const { getJwtToken } = await import('@/lib/auth-client');
        const token = await getJwtToken();
        if (token) {
          localStorage.setItem('bearer_token', token);
          console.log('[useAuth] JWT token stored successfully');
        } else {
          console.warn('[useAuth] No JWT token returned, will use cookie auth');
        }
      } catch (tokenError) {
        console.warn('[useAuth] Failed to get JWT token:', tokenError);
      }

      // Wait for session to be fully established
      await new Promise(resolve => setTimeout(resolve, 300));

      // Refetch session to ensure it's available
      await refetch();

      console.log('[useAuth] Session confirmed, redirecting to /tasks...');

      // Use window.location for reliable redirect
      window.location.href = '/tasks';

      return result;
    } catch (err) {
      console.error('[useAuth] Login error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [refetch]);

  const register = useCallback(async (input: RegisterInput) => {
    setIsLoading(true);
    try {
      console.log('[useAuth] Starting registration...');
      const result = await signUp.email({
        email: input.email,
        password: input.password,
        name: input.name || '',
      }, {
        // Capture bearer token from response headers
        onSuccess: (ctx) => {
          const authToken = ctx.response.headers.get('set-auth-token');
          if (authToken) {
            console.log('[useAuth] Storing bearer token from register response');
            localStorage.setItem('bearer_token', authToken);
          }
        }
      });

      console.log('[useAuth] signUp.email result:', {
        hasData: !!result.data,
        hasError: !!result.error,
        error: result.error?.message
      });

      if (result.error) {
        throw new Error(result.error.message || 'Registration failed');
      }

      console.log('[useAuth] Registration successful, fetching JWT token...');

      // Fetch and store JWT token for API calls
      try {
        const { getJwtToken } = await import('@/lib/auth-client');
        const token = await getJwtToken();
        if (token) {
          localStorage.setItem('bearer_token', token);
          console.log('[useAuth] JWT token stored successfully');
        } else {
          console.warn('[useAuth] No JWT token returned, will use cookie auth');
        }
      } catch (tokenError) {
        console.warn('[useAuth] Failed to get JWT token:', tokenError);
      }

      // Wait for session to be fully established
      await new Promise(resolve => setTimeout(resolve, 300));

      // Refetch session to ensure it's available
      await refetch();

      console.log('[useAuth] Session confirmed, redirecting to /tasks...');

      // Use window.location for reliable redirect
      window.location.href = '/tasks';

      return result;
    } catch (err) {
      console.error('[useAuth] Registration error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [refetch]);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      // Clear cached JWT token and bearer token
      clearCachedToken();
      clearStoredToken();
      await signOut();
      router.push('/login');
      router.refresh();
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  const user: User | null = session?.user ? {
    id: session.user.id,
    email: session.user.email,
    name: session.user.name || undefined,
    image: session.user.image || undefined,
    created_at: session.user.createdAt?.toString() || new Date().toISOString(),
  } : null;

  return {
    user,
    isAuthenticated: !!session?.user,
    isLoading: isPending || isLoading,
    error,
    login,
    register,
    logout,
    refetch,
  };
}