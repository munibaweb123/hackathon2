// Database initialization script for Better Auth
import { getMigrations } from 'better-auth/db';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 5,
  min: 0,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
});

async function initializeDatabase() {
  try {
    // Create a temporary config with essential auth settings
    const authConfig = {
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
      ],
    };

    console.log('Checking for required database migrations...');
    const migrations = await getMigrations(authConfig);

    console.log('Tables to be created:', migrations.toBeCreated);
    console.log('Fields to be added:', migrations.toBeAdded);

    if (migrations.toBeCreated.length > 0 || migrations.toBeAdded.length > 0) {
      console.log('Applying migrations...');
      await migrations.runMigrations();
      console.log('Database schema initialized successfully');
    } else {
      console.log('Database schema is already up to date');
    }
  } catch (error) {
    console.error('Error initializing database:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

initializeDatabase();