#!/usr/bin/env node

/**
 * Test script for KnowledgePersistence-AI MCP Server
 * Tests database connectivity and basic tool functionality
 */

import { spawn } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class MCPServerTester {
  constructor() {
    this.serverPath = join(__dirname, '../server/knowledge-server.js');
    this.testsPassed = 0;
    this.testsFailed = 0;
  }

  async runTest(testName, testFn) {
    console.log(`\n🧪 Running test: ${testName}`);
    try {
      await testFn();
      console.log(`✅ PASS: ${testName}`);
      this.testsPassed++;
    } catch (error) {
      console.log(`❌ FAIL: ${testName}`);
      console.log(`   Error: ${error.message}`);
      this.testsFailed++;
    }
  }

  async sendMCPRequest(request) {
    return new Promise((resolve, reject) => {
      const server = spawn('node', [this.serverPath]);
      let stdout = '';
      let stderr = '';

      // Set timeout
      const timeout = setTimeout(() => {
        server.kill();
        reject(new Error('Test timeout after 10 seconds'));
      }, 10000);

      server.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      server.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      server.on('close', (code) => {
        clearTimeout(timeout);
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          reject(new Error(`Server exited with code ${code}: ${stderr}`));
        }
      });

      // Send request
      server.stdin.write(JSON.stringify(request) + '\n');
      server.stdin.end();
    });
  }

  async testListTools() {
    const request = {
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/list'
    };

    const response = await this.sendMCPRequest(request);
    
    if (!response.stdout.includes('start_session')) {
      throw new Error('start_session tool not found in response');
    }
    
    if (!response.stdout.includes('store_knowledge')) {
      throw new Error('store_knowledge tool not found in response');
    }
    
    if (!response.stdout.includes('get_contextual_knowledge')) {
      throw new Error('get_contextual_knowledge tool not found in response');
    }
  }

  async testStartSession() {
    const request = {
      jsonrpc: '2.0',
      id: 2,
      method: 'tools/call',
      params: {
        name: 'start_session',
        arguments: {
          project_context: 'KnowledgePersistence-AI Test Session'
        }
      }
    };

    const response = await this.sendMCPRequest(request);
    
    if (!response.stdout.includes('session_id')) {
      throw new Error('Session ID not found in response');
    }
    
    if (!response.stdout.includes('Session started successfully')) {
      throw new Error('Success message not found in response');
    }
  }

  async testStoreKnowledge() {
    const request = {
      jsonrpc: '2.0',
      id: 3,
      method: 'tools/call',
      params: {
        name: 'store_knowledge',
        arguments: {
          knowledge_type: 'technical_discovery',
          category: 'mcp_testing',
          title: 'MCP Server Test Knowledge',
          content: 'This is a test knowledge item created during MCP server testing.',
          context_data: {
            test_run: true,
            timestamp: new Date().toISOString()
          },
          retrieval_triggers: ['mcp', 'test', 'server', 'validation']
        }
      }
    };

    const response = await this.sendMCPRequest(request);
    
    if (!response.stdout.includes('Knowledge stored successfully')) {
      throw new Error('Knowledge storage success message not found');
    }
    
    if (!response.stdout.includes('knowledge_id')) {
      throw new Error('Knowledge ID not found in response');
    }
  }

  async testSearchKnowledge() {
    const request = {
      jsonrpc: '2.0',
      id: 4,
      method: 'tools/call',
      params: {
        name: 'search_similar_knowledge',
        arguments: {
          query: 'mcp test',
          max_results: 5
        }
      }
    };

    const response = await this.sendMCPRequest(request);
    
    // Should return some results (could be empty array if no matching knowledge)
    if (!response.stdout.includes('[]') && !response.stdout.includes('knowledge_id')) {
      throw new Error('Invalid search response format');
    }
  }

  async testGetContextualKnowledge() {
    const request = {
      jsonrpc: '2.0',
      id: 5,
      method: 'tools/call',
      params: {
        name: 'get_contextual_knowledge',
        arguments: {
          situation: 'testing MCP server functionality',
          max_results: 3
        }
      }
    };

    const response = await this.sendMCPRequest(request);
    
    // Should return array format (could be empty)
    if (!response.stdout.includes('[')) {
      throw new Error('Invalid contextual knowledge response format');
    }
  }

  async testStoreTechnicalDiscovery() {
    const request = {
      jsonrpc: '2.0',
      id: 6,
      method: 'tools/call',
      params: {
        name: 'store_technical_discovery',
        arguments: {
          problem: 'MCP server database connection issues',
          solution: 'Ensure DATABASE_URL environment variable is properly configured',
          context: {
            test_discovery: true,
            solution_category: 'configuration'
          }
        }
      }
    };

    const response = await this.sendMCPRequest(request);
    
    if (!response.stdout.includes('Technical discovery stored successfully')) {
      throw new Error('Technical discovery storage success message not found');
    }
  }

  async runAllTests() {
    console.log('🚀 Starting KnowledgePersistence-AI MCP Server Tests\n');
    console.log('━'.repeat(60));

    await this.runTest('List Available Tools', () => this.testListTools());
    await this.runTest('Start Session', () => this.testStartSession());
    await this.runTest('Store Knowledge', () => this.testStoreKnowledge());
    await this.runTest('Search Similar Knowledge', () => this.testSearchKnowledge());
    await this.runTest('Get Contextual Knowledge', () => this.testGetContextualKnowledge());
    await this.runTest('Store Technical Discovery', () => this.testStoreTechnicalDiscovery());

    console.log('\n' + '━'.repeat(60));
    console.log('📊 Test Results Summary:');
    console.log(`✅ Passed: ${this.testsPassed}`);
    console.log(`❌ Failed: ${this.testsFailed}`);
    console.log(`📈 Success Rate: ${Math.round((this.testsPassed / (this.testsPassed + this.testsFailed)) * 100)}%`);

    if (this.testsFailed === 0) {
      console.log('\n🎉 All tests passed! MCP server is ready for integration.');
      process.exit(0);
    } else {
      console.log('\n⚠️  Some tests failed. Check the error messages above.');
      process.exit(1);
    }
  }
}

// Run tests
const tester = new MCPServerTester();
tester.runAllTests().catch(error => {
  console.error('Test runner error:', error.message);
  process.exit(1);
});