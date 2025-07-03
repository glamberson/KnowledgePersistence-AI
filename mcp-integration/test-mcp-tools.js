#!/usr/bin/env node

/**
 * Test script for MCP Knowledge Persistence Server
 * Tests all available tools and database connectivity
 */

import { spawn } from 'child_process';
import { writeFileSync, readFileSync } from 'fs';

class MCPTester {
  constructor() {
    this.serverProcess = null;
    this.testResults = [];
  }

  async startServer() {
    console.log('🚀 Starting MCP Knowledge Server...');
    
    this.serverProcess = spawn('node', [
      '/home/greg/KnowledgePersistence-AI/mcp-integration/server/knowledge-server.js'
    ], {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: {
        ...process.env,
        DATABASE_URL: 'postgresql://postgres:SecureKnowledgePassword2025@192.168.10.90:5432/knowledge_persistence'
      }
    });

    return new Promise((resolve, reject) => {
      this.serverProcess.stderr.on('data', (data) => {
        const output = data.toString();
        console.log('Server output:', output);
        if (output.includes('MCP Server running')) {
          resolve();
        }
      });

      this.serverProcess.on('error', reject);
      
      setTimeout(() => resolve(), 2000); // Give it 2 seconds to start
    });
  }

  async sendRequest(request) {
    return new Promise((resolve, reject) => {
      let responseData = '';
      
      const timeout = setTimeout(() => {
        reject(new Error('Request timeout'));
      }, 5000);

      this.serverProcess.stdout.once('data', (data) => {
        clearTimeout(timeout);
        try {
          responseData = data.toString();
          const response = JSON.parse(responseData);
          resolve(response);
        } catch (error) {
          reject(new Error(`Invalid JSON response: ${responseData}`));
        }
      });

      this.serverProcess.stdin.write(JSON.stringify(request) + '\n');
    });
  }

  async testListTools() {
    console.log('\n📋 Testing List Tools...');
    
    try {
      const request = {
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/list',
        params: {}
      };

      const response = await this.sendRequest(request);
      
      if (response.result && response.result.tools) {
        console.log(`✅ Found ${response.result.tools.length} tools:`);
        response.result.tools.forEach(tool => {
          console.log(`   - ${tool.name}: ${tool.description}`);
        });
        this.testResults.push({ test: 'list_tools', status: 'PASS', tools: response.result.tools.length });
      } else {
        throw new Error('No tools found in response');
      }
    } catch (error) {
      console.log(`❌ List Tools failed: ${error.message}`);
      this.testResults.push({ test: 'list_tools', status: 'FAIL', error: error.message });
    }
  }

  async testStoreKnowledge() {
    console.log('\n💾 Testing Store Knowledge...');
    
    try {
      const request = {
        jsonrpc: '2.0',
        id: 2,
        method: 'tools/call',
        params: {
          name: 'store_knowledge',
          arguments: {
            knowledge_type: 'technical_discovery',
            category: 'mcp_testing',
            title: 'MCP Integration Test Knowledge',
            content: 'This is a test knowledge item created during MCP integration testing. It validates that the knowledge storage system is working correctly.',
            context_data: {
              test_session: true,
              timestamp: new Date().toISOString(),
              test_type: 'mcp_integration'
            },
            retrieval_triggers: ['mcp', 'test', 'integration', 'knowledge_storage']
          }
        }
      };

      const response = await this.sendRequest(request);
      
      if (response.result && response.result.content) {
        const result = JSON.parse(response.result.content[0].text);
        console.log(`✅ Knowledge stored successfully: ${result.knowledge_id}`);
        this.testResults.push({ 
          test: 'store_knowledge', 
          status: 'PASS', 
          knowledge_id: result.knowledge_id 
        });
        return result.knowledge_id;
      } else {
        throw new Error('No content in response');
      }
    } catch (error) {
      console.log(`❌ Store Knowledge failed: ${error.message}`);
      this.testResults.push({ test: 'store_knowledge', status: 'FAIL', error: error.message });
      return null;
    }
  }

  async testSearchKnowledge() {
    console.log('\n🔍 Testing Search Knowledge...');
    
    try {
      const request = {
        jsonrpc: '2.0',
        id: 3,
        method: 'tools/call',
        params: {
          name: 'search_similar_knowledge',
          arguments: {
            query: 'MCP integration test',
            max_results: 5
          }
        }
      };

      const response = await this.sendRequest(request);
      
      if (response.result && response.result.content) {
        const results = JSON.parse(response.result.content[0].text);
        console.log(`✅ Found ${results.length} knowledge items`);
        if (results.length > 0) {
          console.log(`   - First result: ${results[0].title}`);
        }
        this.testResults.push({ 
          test: 'search_knowledge', 
          status: 'PASS', 
          results_count: results.length 
        });
      } else {
        throw new Error('No content in response');
      }
    } catch (error) {
      console.log(`❌ Search Knowledge failed: ${error.message}`);
      this.testResults.push({ test: 'search_knowledge', status: 'FAIL', error: error.message });
    }
  }

  async testGetContextualKnowledge() {
    console.log('\n🎯 Testing Get Contextual Knowledge...');
    
    try {
      const request = {
        jsonrpc: '2.0',
        id: 4,
        method: 'tools/call',
        params: {
          name: 'get_contextual_knowledge',
          arguments: {
            situation: 'Setting up MCP integration for knowledge persistence system',
            max_results: 10
          }
        }
      };

      const response = await this.sendRequest(request);
      
      if (response.result && response.result.content) {
        const results = JSON.parse(response.result.content[0].text);
        console.log(`✅ Found ${results.length} contextual knowledge items`);
        this.testResults.push({ 
          test: 'contextual_knowledge', 
          status: 'PASS', 
          results_count: results.length 
        });
      } else {
        throw new Error('No content in response');
      }
    } catch (error) {
      console.log(`❌ Get Contextual Knowledge failed: ${error.message}`);
      this.testResults.push({ test: 'contextual_knowledge', status: 'FAIL', error: error.message });
    }
  }

  async testStartSession() {
    console.log('\n🏁 Testing Start Session...');
    
    try {
      const request = {
        jsonrpc: '2.0',
        id: 5,
        method: 'tools/call',
        params: {
          name: 'start_session',
          arguments: {
            project_context: 'KnowledgePersistence-AI MCP Integration Testing'
          }
        }
      };

      const response = await this.sendRequest(request);
      
      if (response.result && response.result.content) {
        const result = JSON.parse(response.result.content[0].text);
        console.log(`✅ Session started: ${result.session_id}`);
        this.testResults.push({ 
          test: 'start_session', 
          status: 'PASS', 
          session_id: result.session_id 
        });
      } else {
        throw new Error('No content in response');
      }
    } catch (error) {
      console.log(`❌ Start Session failed: ${error.message}`);
      this.testResults.push({ test: 'start_session', status: 'FAIL', error: error.message });
    }
  }

  async runAllTests() {
    try {
      await this.startServer();
      
      await this.testListTools();
      await this.testStoreKnowledge();
      await this.testSearchKnowledge();
      await this.testGetContextualKnowledge();
      await this.testStartSession();
      
    } catch (error) {
      console.log(`❌ Test setup failed: ${error.message}`);
    } finally {
      if (this.serverProcess) {
        this.serverProcess.kill();
      }
    }
  }

  printResults() {
    console.log('\n📊 TEST RESULTS SUMMARY');
    console.log('========================');
    
    const passed = this.testResults.filter(r => r.status === 'PASS').length;
    const failed = this.testResults.filter(r => r.status === 'FAIL').length;
    
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📊 Total: ${this.testResults.length}`);
    
    if (failed === 0) {
      console.log('\n🎉 ALL TESTS PASSED - MCP Integration is working correctly!');
    } else {
      console.log('\n⚠️  Some tests failed - check the output above for details');
    }
    
    // Write detailed results to file
    writeFileSync('/tmp/mcp-test-results.json', JSON.stringify(this.testResults, null, 2));
    console.log('\n📝 Detailed results saved to /tmp/mcp-test-results.json');
  }
}

// Run the tests
const tester = new MCPTester();
tester.runAllTests().then(() => {
  tester.printResults();
}).catch(error => {
  console.error('Test runner failed:', error);
});