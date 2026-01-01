import { createAuthClient } from 'better-auth/react';
import { jwtClient } from 'better-auth/client/plugins';

// Helper to safely access localStorage (only in browser)
export const getStoredToken = (): string => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('bearer_token') || '';
  }
  return '';
};

export const setStoredToken = (token: string): void => {
  if (typeof window !== 'undefined' && token) {
    localStorage.setItem('bearer_token', token);
    console.log('[auth-client] Token stored in localStorage');
  }
};

export const clearStoredToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('bearer_token');
    localStorage.removeItem('auth_token');
    console.log('[auth-client] Tokens cleared from localStorage');
  }
};

// Create auth client with bearer token support (per Better Auth docs)
// This configures the client to automatically include Bearer token in all requests
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
  plugins: [
    jwtClient(),
  ],
  fetchOptions: {
    credentials: 'include',
    // Configure bearer token auth - automatically include token from localStorage
    auth: {
      type: 'Bearer',
      token: () => getStoredToken(),
    },
    // Auto-store bearer token from responses
    onSuccess: (ctx) => {
      const authToken = ctx.response.headers.get('set-auth-token');
      if (authToken) {
        console.log('[auth-client] Storing bearer token from response header');
        setStoredToken(authToken);
      }
    },
  },
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;

// Use a single key for JWT token storage
const JWT_TOKEN_KEY = 'bearer_token';

/**
 * Get the current JWT token using Better Auth's JWT plugin.
 * This token can be used for authenticating with the FastAPI backend.
 */
export async function getJwtToken(): Promise<string | null> {
  try {
    // Check localStorage first for cached token (using same key as setStoredToken)
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem(JWT_TOKEN_KEY);
      if (storedToken) {
        // Verify token is not expired (only if it's a JWT)
        try {
          const parts = storedToken.split('.');
          if (parts.length === 3) {
            const payload = JSON.parse(atob(parts[1]));
            // Check if token expires in more than 5 minutes
            if (payload.exp && (payload.exp * 1000) > (Date.now() + 5 * 60 * 1000)) {
              console.log('[getJwtToken] Using cached token from localStorage');
              return storedToken;
            } else {
              console.log('[getJwtToken] Cached token expired or expiring soon, refreshing...');
              localStorage.removeItem(JWT_TOKEN_KEY);
            }
          } else {
            // Not a JWT, might be session token - still use it
            console.log('[getJwtToken] Using stored token (non-JWT format)');
            return storedToken;
          }
        } catch {
          // If we can't parse, still return the token
          console.log('[getJwtToken] Using stored token (parse failed but returning anyway)');
          return storedToken;
        }
      }
    }

    // Use Better Auth's jwtClient plugin to get token
    // According to docs: authClient.token() returns { data: { token }, error }
    try {
      const result = await (authClient as any).token();
      console.log('[getJwtToken] authClient.token() result:', {
        hasData: !!result?.data,
        hasToken: !!result?.data?.token,
        error: result?.error?.message || null
      });

      if (result?.error) {
        console.log('[getJwtToken] Token fetch error:', result.error.message);
      }

      if (result?.data?.token) {
        console.log('[getJwtToken] Got token via authClient.token()');
        if (typeof window !== 'undefined') {
          localStorage.setItem(JWT_TOKEN_KEY, result.data.token);
        }
        return result.data.token;
      }
    } catch (e) {
      console.log('[getJwtToken] authClient.token() threw:', e);
    }

    // Fallback: Direct fetch from /api/auth/token endpoint
    try {
      const baseUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000';
      console.log('[getJwtToken] Fetching from:', `${baseUrl}/api/auth/token`);
      const response = await fetch(`${baseUrl}/api/auth/token`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'accept': 'application/json',
        }
      });

      console.log('[getJwtToken] /api/auth/token response status:', response.status);

      if (response.ok) {
        const tokenData = await response.json();
        console.log('[getJwtToken] /api/auth/token response:', { hasToken: !!tokenData?.token });

        if (tokenData?.token) {
          console.log('[getJwtToken] Got token from /api/auth/token endpoint');
          if (typeof window !== 'undefined') {
            localStorage.setItem(JWT_TOKEN_KEY, tokenData.token);
          }
          return tokenData.token;
        }
      } else {
        const errorText = await response.text();
        console.log('[getJwtToken] /api/auth/token failed:', response.status, errorText);
      }
    } catch (e) {
      console.log('[getJwtToken] /api/auth/token fetch failed:', e);
    }

    console.log('[getJwtToken] No JWT token available');
    return null;
  } catch (error) {
    console.error('[getJwtToken] Error:', error);
    return null;
  }
}
