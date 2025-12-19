import { createAuthClient } from 'better-auth/react';
import { jwtClient } from 'better-auth/client/plugins';

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
  plugins: [
    jwtClient(),
  ],
  fetchOptions: {
    credentials: 'include',
  },
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;

/**
 * Get the current JWT token using Better Auth's JWT plugin.
 * This token can be used for authenticating with the FastAPI backend.
 */
export async function getJwtToken(): Promise<string | null> {
  try {
    // Check localStorage first for cached token
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem("auth_token");
      if (storedToken) {
        // Verify token is not expired
        try {
          const parts = storedToken.split('.');
          if (parts.length === 3) {
            const payload = JSON.parse(atob(parts[1]));
            // Check if token expires in more than 5 minutes
            if (payload.exp && (payload.exp * 1000) > (Date.now() + 5 * 60 * 1000)) {
              console.debug('[getJwtToken] Using cached token from localStorage');
              return storedToken;
            } else {
              console.debug('[getJwtToken] Cached token expired or expiring soon');
              localStorage.removeItem("auth_token");
            }
          }
        } catch {
          localStorage.removeItem("auth_token");
        }
      }
    }

    // Use Better Auth's jwtClient plugin to get token
    // According to docs: authClient.token() returns { data: { token }, error }
    try {
      const result = await (authClient as any).token();
      console.debug('[getJwtToken] authClient.token() result:', {
        hasData: !!result?.data,
        hasToken: !!result?.data?.token,
        error: result?.error?.message || null
      });

      if (result?.error) {
        console.debug('[getJwtToken] Token fetch error:', result.error.message);
      }

      if (result?.data?.token) {
        console.debug('[getJwtToken] Got token via authClient.token()');
        if (typeof window !== 'undefined') {
          localStorage.setItem("auth_token", result.data.token);
        }
        return result.data.token;
      }
    } catch (e) {
      console.debug('[getJwtToken] authClient.token() threw:', e);
    }

    // Fallback: Direct fetch from /api/auth/token endpoint
    try {
      const baseUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000';
      const response = await fetch(`${baseUrl}/api/auth/token`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'accept': 'application/json',
        }
      });

      console.debug('[getJwtToken] /api/auth/token response status:', response.status);

      if (response.ok) {
        const tokenData = await response.json();
        console.debug('[getJwtToken] /api/auth/token response:', { hasToken: !!tokenData?.token });

        if (tokenData?.token) {
          console.debug('[getJwtToken] Got token from /api/auth/token endpoint');
          if (typeof window !== 'undefined') {
            localStorage.setItem("auth_token", tokenData.token);
          }
          return tokenData.token;
        }
      }
    } catch (e) {
      console.debug('[getJwtToken] /api/auth/token fetch failed:', e);
    }

    console.debug('[getJwtToken] No JWT token available');
    return null;
  } catch (error) {
    console.error('[getJwtToken] Error:', error);
    return null;
  }
}
