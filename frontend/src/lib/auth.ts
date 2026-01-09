import { betterAuth } from 'better-auth';
import { nextCookies } from 'better-auth/next-js';
import { jwt } from 'better-auth/plugins';
import { Pool } from 'pg';

// Create PostgreSQL connection pool for Neon
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL?.includes('neon.tech') ? { rejectUnauthorized: false } : undefined,
});

// Better Auth configuration with Neon PostgreSQL
export const auth = betterAuth({
  baseURL: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
  secret: process.env.BETTER_AUTH_SECRET,

  // Database connection - use Neon PostgreSQL
  database: pool,

  // Configure user table to match backend's schema
  user: {
    modelName: 'users',  // Use 'users' table (backend's table) instead of 'user'
    fields: {
      // Map Better Auth's camelCase to backend's snake_case
      emailVerified: 'email_verified',
      createdAt: 'created_at',
      updatedAt: 'updated_at',
    },
  },

  // Configure session table
  session: {
    modelName: 'session',  // Keep default 'session' table
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,     // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60,            // 5 minutes
    },
  },

  emailAndPassword: {
    enabled: true,
    autoSignIn: true,
  },

  trustedOrigins: [
    'http://localhost:3000',
    'http://localhost:8000',
    process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000',
  ],

  advanced: {
    // Explicitly disable secure cookies for HTTP (local development)
    useSecureCookies: process.env.BETTER_AUTH_SECURE_COOKIES === 'true',
    // Cross-subdomain cookies disabled for localhost
    crossSubDomainCookies: {
      enabled: false,
    },
  },

  plugins: [
    nextCookies(),
    jwt(),  // Uses EdDSA by default, backend fetches JWKS to verify
  ],
});

export type Session = typeof auth.$Infer.Session;