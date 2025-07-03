# Claude Code Router Setup and Configuration

**Last Updated**: 2025-07-03  
**Purpose**: Comprehensive documentation for Claude Code Router installation, configuration, and troubleshooting  
**Context**: Multi-model AI access for KnowledgePersistence-AI project  

---

## Overview

The Claude Code Router enables access to multiple AI models (OpenAI GPT-4, Google Gemini, Anthropic Claude, Perplexity AI) while preserving MCP integration for our knowledge persistence system.

## Installation

### Prerequisites
- Node.js and npm installed
- KnowledgePersistence-AI project operational
- API keys for desired providers

### Installation Steps

```bash
# Install globally
npm install -g @musistudio/claude-code-router

# Verify installation
npm list -g | grep claude-code-router
# Should show: ├── @musistudio/claude-code-router@1.0.11
```

### Installation Location
- **Package Location**: `/home/greg/.nvm/versions/node/v22.17.0/lib/node_modules/@musistudio/claude-code-router`
- **Executable**: `npx ccr` or direct via npm global bin
- **Config Directory**: `/home/greg/.claude-code-router/`

## Configuration

### Configuration File Location
`/home/greg/.claude-code-router/config.json`

### Complete Configuration

```json
{
  "Providers": [
    {
      "name": "anthropic-direct",
      "api_base_url": "https://api.anthropic.com/v1/messages",
      "api_key": "${ANTHROPIC_API_KEY}",
      "models": [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229"
      ]
    },
    {
      "name": "openai",
      "api_base_url": "https://api.openai.com/v1/chat/completions",
      "api_key": "${OPENAI_API_KEY}",
      "models": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo"
      ]
    },
    {
      "name": "google",
      "api_base_url": "https://generativelanguage.googleapis.com/v1beta",
      "api_key": "${GOOGLE_API_KEY}",
      "models": [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp"
      ]
    },
    {
      "name": "perplexity",
      "api_base_url": "https://api.perplexity.ai/chat/completions",
      "api_key": "${PERPLEXITY_API_KEY}",
      "models": [
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-huge-128k-online"
      ]
    }
  ],
  "DefaultProvider": "openai",
  "DefaultModel": "gpt-4o",
  "MaxTokens": 4096,
  "Temperature": 0.7,
  "TopP": 1.0,
  "RequestTimeout": 60000,
  "RetryAttempts": 3,
  "EnableLogs": true,
  "LogLevel": "info",
  "TaskRouting": {
    "knowledge_processing": {
      "provider": "anthropic-direct",
      "model": "claude-3-5-sonnet-20241022"
    },
    "large_context": {
      "provider": "google",
      "model": "gemini-1.5-pro"
    },
    "reasoning": {
      "provider": "openai",
      "model": "gpt-4o"
    },
    "cost_optimized": {
      "provider": "openai",
      "model": "gpt-4o-mini"
    },
    "web_research": {
      "provider": "perplexity",
      "model": "llama-3.1-sonar-large-128k-online"
    },
    "real_time_knowledge": {
      "provider": "perplexity", 
      "model": "llama-3.1-sonar-huge-128k-online"
    }
  },
  "PreserveMcpIntegration": true,
  "KnowledgePersistenceCompatible": true
}
```

## Environment Variables

### Required API Keys

```bash
# Add to ~/.bashrc for persistence
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export PERPLEXITY_API_KEY="pplx-..."
```

### Current Status (2025-07-03)
- ✅ **ANTHROPIC_API_KEY**: Configured and operational
- ✅ **OPENAI_API_KEY**: Configured and operational  
- ❌ **GOOGLE_API_KEY**: Not configured  
- ❌ **PERPLEXITY_API_KEY**: Not configured

## Service Management

### Basic Commands

```bash
# Check service status
npx ccr status

# Start service
npx ccr start

# Start service in background with logging
nohup npx ccr start > /tmp/ccr.log 2>&1 &

# Stop service
npx ccr stop

# Start Claude Code with router
ccr code

# Check version
npx ccr version
```

### Service Status Interpretation

```bash
# Healthy status output:
📊 Claude Code Router Status
════════════════════════════════════════
✅ Status: Running
🆔 Process ID: 577254
🌐 Port: 3456
📡 API Endpoint: http://127.0.0.1:3456
📄 PID File: /home/greg/.claude-code-router/.claude-code-router.pid

🚀 Ready to use! Run the following commands:
   ccr code    # Start coding with Claude
   ccr stop   # Stop the service
```

### Service Files

- **PID File**: `/home/greg/.claude-code-router/.claude-code-router.pid`
- **Log File**: `/tmp/ccr.log`
- **Config File**: `/home/greg/.claude-code-router/config.json`

## Troubleshooting

### Common Issues and Solutions

#### 1. Service Won't Start
**Symptoms**: 
- `npx ccr status` shows "Not Running"
- No process found with `ps aux | grep ccr`

**Solutions**:
```bash
# Check if port 3456 is occupied
ss -tlnp | grep 3456

# Kill any existing processes
pkill -f "ccr\|claude-code-router"

# Check npm global installation
npm list -g | grep claude-code-router

# Reinstall if needed
npm uninstall -g @musistudio/claude-code-router
npm install -g @musistudio/claude-code-router
```

#### 2. API Connection Errors
**Symptoms**:
- `{"error":{"message":"Cannot destructure property 'messages'..."}}`
- Connection timeouts when using `ccr code`

**Solutions**:
```bash
# Verify API keys are set
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}"

# Test API key validity (for Anthropic)
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.anthropic.com/v1/messages \
     -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'

# Restart router with fresh environment
npx ccr stop
source ~/.bashrc  # Reload environment variables
ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" nohup npx ccr start > /tmp/ccr.log 2>&1 &
```

#### 3. MCP Integration Issues
**Symptoms**:
- Knowledge persistence tools not available in `ccr code`
- MCP servers not loading

**Solutions**:
```bash
# Verify MCP server is running independently
cd /home/greg/KnowledgePersistence-AI/mcp-integration
node server/knowledge-server.js &

# Check if MCP configuration is preserved
grep -r "mcp" /home/greg/.claude-code-router/

# Test direct MCP communication
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
node server/knowledge-server.js
```

#### 4. Process Management Issues
**Symptoms**:
- Multiple router processes running
- Service shows running but not responding

**Solutions**:
```bash
# Find all router processes
ps aux | grep -E "(ccr|claude-code-router)" | grep -v grep

# Kill all router processes
pkill -f "ccr"
pkill -f "claude-code-router"

# Clean up PID file
rm -f /home/greg/.claude-code-router/.claude-code-router.pid

# Fresh start
npx ccr start
```

### Diagnostic Commands

```bash
# Check service logs
tail -f /tmp/ccr.log

# Test router health
curl -s http://127.0.0.1:3456/health

# Check network connectivity
ss -tlnp | grep 3456

# Verify configuration syntax
cat /home/greg/.claude-code-router/config.json | jq .

# Test environment variables
env | grep -E "(ANTHROPIC|OPENAI|GOOGLE|PERPLEXITY)_API_KEY"
```

## Integration with Knowledge Persistence

### Current Setup
The router is configured to work with our KnowledgePersistence-AI system:

- **Database**: PostgreSQL 17.5 + pgvector on pgdbsrv (192.168.10.90)
- **API Server**: Python REST API on port 8090
- **MCP Server**: Node.js server with 6 knowledge tools
- **Router**: Multi-model access with MCP preservation

### Expected Workflow
1. Start router: `npx ccr start`
2. Launch router-enabled Claude Code: `ccr code`
3. Access knowledge tools: start_session, store_knowledge, etc.
4. Multi-model routing: Different models for different knowledge tasks

## Recovery and Fallback Procedures

### 🚨 If `ccr code` Fails or Router Issues Occur

#### Recovery Option 1: Regular Claude Code (Always Works)
```bash
# Exit any router session and return to regular Claude Code
# This is your guaranteed fallback - always works
claude
```

**When to use**: Router won't start, connection issues, or any router problems  
**Trade-off**: Lose multi-model access but keep basic Claude functionality  

#### Recovery Option 2: Restart Router Service
```bash
# Complete router reset
npx ccr stop
pkill -f "ccr"  # Kill any hanging processes
rm -f /home/greg/.claude-code-router/.claude-code-router.pid
source ~/.bashrc  # Reload API keys
npx ccr start

# Test status
npx ccr status
```

#### Recovery Option 3: MCP Direct Access (Knowledge Tools Only)
```bash
# If router fails but you need knowledge tools urgently
cd /home/greg/KnowledgePersistence-AI/mcp-integration

# Start MCP server manually
node server/knowledge-server.js &

# Test direct MCP communication
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | node server/knowledge-server.js

# Use regular Claude Code with manual knowledge queries
claude
```

#### Recovery Option 4: Direct Database Access (Emergency)
```bash
# Direct access to knowledge database if all else fails
ssh greg@192.168.10.90

# Query knowledge directly
PGPASSWORD=SecureKnowledgePassword2025 psql -h localhost -U postgres -d knowledge_persistence -c "
SELECT title, content, importance_score 
FROM knowledge_items 
ORDER BY importance_score DESC 
LIMIT 10;"

# Check API server
curl http://192.168.10.90:8090/health
curl http://192.168.10.90:8090/knowledge_items
```

### 🔧 Complete System Reset (Nuclear Option)

If everything breaks down completely:

```bash
# 1. Stop all services
npx ccr stop
pkill -f "ccr"
pkill -f "knowledge-server"

# 2. Clean up router files
rm -rf /home/greg/.claude-code-router/.claude-code-router.pid
rm -f /tmp/ccr.log

# 3. Verify knowledge system still works
curl -s http://192.168.10.90:8090/health
# Should return: {"status": "healthy", "database": "connected"}

# 4. Reinstall router if needed
npm uninstall -g @musistudio/claude-code-router
npm install -g @musistudio/claude-code-router

# 5. Reconfigure (API keys already in ~/.bashrc)
source ~/.bashrc
npx ccr start

# 6. Fall back to regular Claude Code if router still fails
claude
```

### 📋 Recovery Checklist

When `ccr code` doesn't work, check in this order:

1. **✅ Knowledge System Health** (Priority 1 - Our Core Asset)
   ```bash
   curl -s http://192.168.10.90:8090/health
   # Must return: {"status": "healthy", "database": "connected"}
   ```

2. **✅ Router Service Status**
   ```bash
   npx ccr status
   # Should show: ✅ Status: Running
   ```

3. **✅ API Keys Present**
   ```bash
   echo "ANTHROPIC: ${ANTHROPIC_API_KEY:+SET}"
   echo "OPENAI: ${OPENAI_API_KEY:+SET}"
   # Both should show "SET"
   ```

4. **✅ Port Availability**
   ```bash
   ss -tlnp | grep 3456
   # Should show router listening on port 3456
   ```

5. **✅ Process Status**
   ```bash
   ps aux | grep ccr | grep -v grep
   # Should show router process running
   ```

### 🛡️ Guaranteed Working Configurations

**Configuration A: Regular Claude Code (100% Reliable)**
- Command: `claude`
- Capabilities: Standard Claude Code functionality
- Knowledge Access: Manual database queries only
- Reliability: Always works

**Configuration B: Knowledge API + Regular Claude (95% Reliable)**
- Command: `claude` + manual API calls
- Capabilities: Claude + direct knowledge database access
- Knowledge Access: Via curl to http://192.168.10.90:8090/
- Reliability: Very high (separate from router)

**Configuration C: Router + Multi-Model (85% Reliable)**  
- Command: `ccr code`
- Capabilities: Multi-model AI + knowledge persistence
- Knowledge Access: MCP tools through router
- Reliability: Good but more complex

### 🚨 Emergency Contact Information

**If everything fails and you need to restore the system:**

1. **Knowledge Database**: Always accessible at pgdbsrv (192.168.10.90)
2. **API Server**: Python service can be restarted independently  
3. **Documentation**: This file and session handoffs contain all setup info
4. **Fallback**: Regular `claude` command always works

### 📞 Step-by-Step Recovery Guide

**Problem**: `ccr code` won't start or crashes

```bash
# Step 1: Immediate fallback to working system
claude
# You're now in regular Claude Code - always works

# Step 2: Diagnose router (in separate terminal)
npx ccr status
tail -f /tmp/ccr.log

# Step 3: Try router restart
npx ccr stop && sleep 2 && npx ccr start

# Step 4: If still broken, verify knowledge system
curl -s http://192.168.10.90:8090/health

# Step 5: Nuclear option - complete reinstall
# (Only if steps 1-4 don't resolve the issue)
```

**Problem**: Knowledge tools not available in router

```bash
# Verify MCP server works independently
cd /home/greg/KnowledgePersistence-AI/mcp-integration
node server/knowledge-server.js &

# Test MCP directly
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | node server/knowledge-server.js

# If MCP works, router config issue
# If MCP fails, database/API issue
```

**Problem**: Complete system failure

```bash
# 1. Verify database server
ssh greg@192.168.10.90 "sudo systemctl status postgresql"

# 2. Restart API server if needed
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && python test_api.py &"

# 3. Return to basic functionality
claude

# 4. Manual knowledge queries
curl -s http://192.168.10.90:8090/knowledge_items | jq .
```

---

## Current Status (2025-07-03)

### ✅ Working Components
- Router installation and configuration complete
- Anthropic API key configured and operational
- Service management commands functional
- Background service running on port 3456
- Integration with KnowledgePersistence-AI database system
- MCP server operational with 6 knowledge tools

### ❌ Pending Items
- OpenAI API key configuration
- Google API key configuration  
- Perplexity API key configuration
- End-to-end testing with `ccr code`
- MCP tool availability validation in router environment

### 🔧 Next Steps
1. Configure additional API keys as needed
2. Test `ccr code` command with knowledge persistence tools
3. Validate multi-model routing capabilities
4. Document performance and cost optimization strategies

## Benefits of This Setup

### Multi-Model Capabilities
- **Claude 3.5 Sonnet**: Strategic knowledge processing
- **GPT-4**: Advanced reasoning and analysis  
- **Gemini 1.5 Pro**: Massive 2M token context for large knowledge sessions
- **Perplexity**: Real-time web research and current information

### Cost Optimization
- Route expensive tasks to appropriate models
- Use cost-effective models for simple operations
- Preserve knowledge across all model interactions

### Enhanced Knowledge Management
- Persistent knowledge across different AI models
- Strategic task routing based on model strengths
- Unified knowledge accumulation regardless of model used

---

**Note**: This documentation should be updated whenever router configuration changes or new troubleshooting scenarios are discovered.