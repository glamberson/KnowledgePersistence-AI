#!/usr/bin/env node

/**
 * Simple test for MCP server database connectivity
 */

import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

async function testDatabaseConnection() {
  console.log('🔌 Testing database connection...');
  
  const db = new Pool({
    connectionString: process.env.DATABASE_URL || 'postgresql://postgres:SecureKnowledgePassword2025@192.168.10.90:5432/knowledge_persistence',
    ssl: false,
  });

  try {
    // Test basic connection
    await db.query('SELECT 1');
    console.log('✅ Database connection successful');

    // Test knowledge_items table
    const result = await db.query('SELECT COUNT(*) FROM knowledge_items');
    console.log(`✅ Knowledge items table accessible: ${result.rows[0].count} items`);

    // Test ai_sessions table
    const sessionsResult = await db.query('SELECT COUNT(*) FROM ai_sessions');
    console.log(`✅ AI sessions table accessible: ${sessionsResult.rows[0].count} sessions`);

    // Test technical_gotchas table
    const gotchasResult = await db.query('SELECT COUNT(*) FROM technical_gotchas');
    console.log(`✅ Technical gotchas table accessible: ${gotchasResult.rows[0].count} gotchas`);

    console.log('\n🎉 All database tests passed! MCP server should work correctly.');
    
  } catch (error) {
    console.error('❌ Database test failed:', error.message);
    process.exit(1);
  } finally {
    await db.end();
  }
}

testDatabaseConnection();