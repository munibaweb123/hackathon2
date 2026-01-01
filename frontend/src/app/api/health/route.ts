/**
 * General health endpoint for monitoring/observability
 *
 * Returns application status, version, and service information.
 */

export async function GET() {
  return Response.json({
    status: 'healthy',
    version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
    service: 'todo-frontend',
    timestamp: new Date().toISOString(),
  }, {
    status: 200
  });
}
