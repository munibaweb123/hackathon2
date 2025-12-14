// Simple test to check if the database connection works
const { Pool } = require('pg');

// Test the database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_58GBtdLMTCJD@ep-gentle-tooth-adhd8nnt-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require',
  max: 5,
  min: 0,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

async function testConnection() {
  try {
    console.log('Attempting to connect to database...');
    const client = await pool.connect();
    console.log('Connected successfully!');

    // Test query
    const result = await client.query('SELECT NOW()');
    console.log('Query result:', result.rows[0]);

    client.release();
    console.log('Connection test completed successfully');
  } catch (err) {
    console.error('Database connection error:', err.message);
  } finally {
    await pool.end();
  }
}

testConnection();