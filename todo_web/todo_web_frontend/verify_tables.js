// Enhanced test to check if the Better Auth tables were created
const { Pool } = require('pg');

// Test the database connection with more generous settings
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_58GBtdLMTCJD@ep-gentle-tooth-adhd8nnt-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require',
  max: 5,
  min: 0,
  idleTimeoutMillis: 60000, // 1 minute
  connectionTimeoutMillis: 20000, // 20 seconds
  ssl: {
    rejectUnauthorized: false // Allow Neon's SSL certificates
  }
});

async function verifyTables() {
  try {
    console.log('Connecting to database...');
    const client = await pool.connect();
    console.log('Connected successfully!');

    // Check all tables in the public schema
    const tablesResult = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY table_name;
    `);
    console.log('All tables in public schema:', tablesResult.rows);

    // Check specifically for Better Auth tables (they might have different names)
    const betterAuthTables = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND (table_name LIKE '%user%' OR table_name LIKE '%session%' OR table_name LIKE '%account%' OR table_name LIKE '%verification%')
      ORDER BY table_name;
    `);
    console.log('Potential Better Auth tables:', betterAuthTables.rows);

    client.release();
    console.log('Verification completed successfully');
  } catch (err) {
    console.error('Database verification error:', err.message);
    console.error('Full error:', err);
  } finally {
    await pool.end();
  }
}

verifyTables();