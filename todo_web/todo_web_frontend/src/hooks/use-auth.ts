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
      const result = await signIn.email({
        email: input.email,
        password: input.password,
      });

      if (result.error) {
        throw new Error(result.error.message || 'Login failed');
      }

      // Wait for session to be available before redirecting
      // This ensures cookies are properly set
      await new Promise(resolve => setTimeout(resolve, 300));

      // Refetch session to ensure it's updated
      await refetch();

      // Wait a bit more to ensure session is fully established
      await new Promise(resolve => setTimeout(resolve, 200));

      router.push('/tasks');
      router.refresh();
      return result;
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router, refetch]);

  const register = useCallback(async (input: RegisterInput) => {
    setIsLoading(true);
    try {
      const result = await signUp.email({
        email: input.email,
        password: input.password,
        name: input.name || '',
      });

      if (result.error) {
        throw new Error(result.error.message || 'Registration failed');
      }

      // Wait for session to be available before redirecting
      await new Promise(resolve => setTimeout(resolve, 300));

      // Refetch session to ensure it's updated
      await refetch();

      // Wait a bit more to ensure session is fully established
      await new Promise(resolve => setTimeout(resolve, 200));

      router.push('/tasks');
      router.refresh();
      return result;
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router, refetch]);

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
