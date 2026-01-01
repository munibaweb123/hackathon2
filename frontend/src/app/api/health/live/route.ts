/**
 * Liveness probe endpoint for Kubernetes
 *
 * Checks if the application process is running.
 * Should NEVER check external dependencies.
 */

export async function GET() {
  return Response.json(
    { status: 'alive' },
    { status: 200 }
  );
}
