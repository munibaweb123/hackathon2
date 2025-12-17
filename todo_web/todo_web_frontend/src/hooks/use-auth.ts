'use client';

import { useCallback, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession, signIn, signUp, signOut, getSession } from '@/lib/auth-client';
import { clearCachedToken } from '@/services/auth/api-client';
import type { User, LoginInput, RegisterInput } from '@/types';

export function useAuth() {
  const router = useRouter();
  const { data: session, isPending, error, refetch } = useSession();
  const [isLoading, setIsLoading] = useState(false);

  // Debug logging for session state
  useEffect(() => {
    console.log('[useAuth] Session state:', {
      session: session ? { user: session.user?.email, hasSession: !!session.session } : null,
      isPending,
      error: error?.message || null,
    });
  }, [session, isPending, error]);

  const login = useCallback(async (input: LoginInput) => {
    setIsLoading(true);
    try {
      console.log('[useAuth] Starting login...');
      const result = await signIn.email({
        email: input.email,
        password: input.password,
      });

      console.log('[useAuth] signIn.email result:', {
        hasData: !!result.data,
        hasError: !!result.error,
        error: result.error?.message
      });

      if (result.error) {
        throw new Error(result.error.message || 'Login failed');
      }

      console.log('[useAuth] Login successful, waiting for session...');

      // Wait for session to be established
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Refetch session
      await refetch();

      console.log('[useAuth] Redirecting to /tasks...');

      // Use window.location for more reliable redirect
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
      });

      console.log('[useAuth] signUp.email result:', {
        hasData: !!result.data,
        hasError: !!result.error,
        error: result.error?.message
      });

      if (result.error) {
        throw new Error(result.error.message || 'Registration failed');
      }

      console.log('[useAuth] Registration successful, waiting for session...');

      // Wait for session to be established
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Refetch session
      await refetch();

      console.log('[useAuth] Redirecting to /tasks...');

      // Use window.location for more reliable redirect
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
      // Clear cached JWT token
      clearCachedToken();
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