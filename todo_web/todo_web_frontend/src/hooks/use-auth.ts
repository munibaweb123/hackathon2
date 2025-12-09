'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSession, signIn, signUp, signOut } from '@/lib/auth-client';
import { apiClient } from '@/lib/api-client';
import type { User, LoginInput, RegisterInput } from '@/types';

export function useAuth() {
  const router = useRouter();
  const { data: session, isPending, error } = useSession();
  const [isLoading, setIsLoading] = useState(false);

  // Sync token with API client when session changes
  useEffect(() => {
    if (session?.session?.token) {
      apiClient.setToken(session.session.token);
    } else {
      apiClient.loadToken();
    }
  }, [session]);

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

      router.push('/tasks');
      router.refresh();
      return result;
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

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

      router.push('/tasks');
      router.refresh();
      return result;
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await signOut();
      apiClient.clearToken();
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
  };
}
