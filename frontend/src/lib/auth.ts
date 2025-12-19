import { betterAuth } from 'better-auth';
import { nextCookies } from 'better-auth/next-js';
import { jwt } from 'better-auth/plugins';
import { Pool } from 'pg';

// Create a singleton pattern for the database connection to avoid multiple instances in Next.js
let pool: Pool;

// Initialize the pool only once in development, or on each request in production serverless
if (process.env.NODE_ENV === 'production') {
  // In production, Better Auth will handle the connection lifecycle appropriately
  pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    // Neon-specific optimizations for serverless
    max: 3,                    // Lower max connections for serverless
    min: 0,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000,
  });
} else {
  // In development, reuse the same pool instance to avoid connection issues
  if (!global.pool) {
    global.pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      max: 3,
      min: 0,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 10000,
    });
  }
  pool = global.pool;
}

// Add type declaration for the global pool to avoid TypeScript errors
declare global {
  var pool: Pool | undefined;
}

export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
    autoSignIn: true,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,     // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60,            // 5 minutes
    },
  },
  trustedOrigins: [
    process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000', // Frontend origin
  ],
  plugins: [
    nextCookies(),
    jwt(),  // Uses EdDSA by default, backend fetches JWKS to verify
  ],
});

export type Session = typeof auth.$Infer.Session;
