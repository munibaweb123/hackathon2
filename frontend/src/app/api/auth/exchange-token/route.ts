import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { NextResponse } from 'next/server';

/**
 * Exchange Better Auth session for a backend JWT token.
 * This route runs server-side and has access to the session cookies.
 */
export async function GET() {
  try {
    // Get the session from Better Auth (server-side has access to cookies)
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.user) {
      return NextResponse.json(
        { error: 'No active session' },
        { status: 401 }
      );
    }

    const { user } = session;
    console.log('[exchange-token] User from Better Auth session:', user.email);

    // Call backend to get a JWT token for this user
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Use the backend's sign-in endpoint to get a token
    // Since we already verified the user via Better Auth, we can create a token
    const response = await fetch(`${backendUrl}/api/auth/sign-in/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: user.email,
        password: 'better-auth-verified', // Backend will accept this for verified sessions
      }),
    });

    if (!response.ok) {
      // If sign-in fails, try to create the user first (they might not exist in backend)
      console.log('[exchange-token] Sign-in failed, trying to sync user...');

      const syncResponse = await fetch(`${backendUrl}/api/auth/sign-up/email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: user.email,
          password: 'better-auth-verified',
          name: user.name || '',
        }),
      });

      if (syncResponse.ok) {
        const syncData = await syncResponse.json();
        console.log('[exchange-token] User synced to backend');
        return NextResponse.json({
          token: syncData.access_token,
          tokenType: 'bearer',
          user: {
            id: syncData.user?.id || user.id,
            email: user.email,
            name: user.name,
          },
        });
      }

      // If that also fails, check if user exists (409 conflict means they exist)
      if (syncResponse.status === 409) {
        // User exists, try login again with correct endpoint
        const loginResponse = await fetch(`${backendUrl}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: user.email,
            password: 'better-auth-verified',
          }),
        });

        if (loginResponse.ok) {
          const loginData = await loginResponse.json();
          console.log('[exchange-token] Login successful via /api/auth/login');
          return NextResponse.json({
            token: loginData.accessToken,
            tokenType: 'bearer',
            user: {
              id: loginData.user?.id || user.id,
              email: user.email,
              name: user.name,
            },
          });
        }
      }

      console.error('[exchange-token] Failed to get token from backend');
      return NextResponse.json(
        { error: 'Failed to exchange token' },
        { status: 500 }
      );
    }

    const data = await response.json();
    console.log('[exchange-token] Token exchange successful');

    return NextResponse.json({
      token: data.access_token,
      tokenType: 'bearer',
      user: {
        id: data.user?.id || user.id,
        email: user.email,
        name: user.name,
      },
    });
  } catch (error) {
    console.error('[exchange-token] Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
