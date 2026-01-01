/**
 * Readiness probe endpoint for Kubernetes
 *
 * Checks if the app can serve traffic by validating backend connectivity.
 */

export async function GET() {
  try {
    // Check backend connectivity
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000';

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

    const response = await fetch(`${backendUrl}/health`, {
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      return Response.json(
        {
          status: 'not_ready',
          reason: 'backend_unavailable',
          checks: {
            backend: 'unhealthy'
          }
        },
        { status: 503 }
      );
    }

    return Response.json(
      {
        status: 'ready',
        checks: {
          backend: 'healthy'
        }
      },
      { status: 200 }
    );
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'unknown error';

    return Response.json(
      {
        status: 'not_ready',
        reason: errorMessage,
        checks: {
          backend: 'unhealthy'
        }
      },
      { status: 503 }
    );
  }
}
