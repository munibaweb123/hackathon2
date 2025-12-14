// Enhanced test to check if the database connection works with better settings
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

async function testConnection() {
  try {
    console.log('Attempting to connect to database...');
    console.log('Using connection string:', process.env.DATABASE_URL ? 'from env' : 'default');

    const client = await pool.connect();
    console.log('Connected successfully!');

    // Test query
    const result = await client.query('SELECT NOW()');
    console.log('Query result:', result.rows[0]);

    // Check if Better Auth tables exist
    const tablesResult = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND (table_name LIKE 'better%' OR table_name LIKE '%auth%')
    `);
    console.log('Better Auth related tables found:', tablesResult.rows);

    client.release();
    console.log('Connection test completed successfully');
  } catch (err) {
    console.error('Database connection error:', err.message);
    console.error('Full error:', err);
  } finally {
    await pool.end();
  }
}

testConnection();