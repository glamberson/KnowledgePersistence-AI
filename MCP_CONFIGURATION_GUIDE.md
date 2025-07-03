# MCP Server Configuration Guide

**Date**: 2025-07-03  
**Project**: KnowledgePersistence-AI  
**Version**: 1.0 (Python Implementation)  

---

## 🎯 Overview

This guide provides the definitive configuration for the KnowledgePersistence-AI MCP (Model Context Protocol) server. After troubleshooting dual server issues, we've standardized on the **Python implementation** as the single source of truth.

---

## 🏗️ Architecture Decision

### Selected Implementation: Python MCP Server
**File**: `/mcp-integration/knowledge-mcp-server.py`

**Decision Rationale**:
- ✅ Proven compatibility with existing PostgreSQL + pgvector infrastructure
- ✅ Uses psycopg3 (modern PostgreSQL adapter)
- ✅ Array handling fix implemented and tested
- ✅ Integrates with project's Python virtual environment
- ✅ Stable database connectivity on pgdbsrv

### Deprecated Implementation: JavaScript MCP Server
**File**: `/mcp-integration/server/knowledge-server.js`
**Status**: ⚠️ **DEPRECATED** - Do not use for production

---

## 📋 Prerequisites

### Infrastructure Requirements
- **Database Server**: pgdbsrv (192.168.10.90)
- **PostgreSQL**: Version 17.5
- **pgvector**: Version 0.8.0
- **Python**: 3.11+
- **Operating System**: Debian 12

### Network Requirements
- SSH access to pgdbsrv (greg@192.168.10.90)
- PostgreSQL port 5432 accessible on localhost (pgdbsrv)
- Database credentials: postgres / SecureKnowledgePassword2025

---

## 🔧 Installation & Configuration

### Step 1: Environment Setup
```bash
# Connect to database server
ssh greg@192.168.10.90

# Navigate to project directory
cd KnowledgePersistence-AI

# Activate Python virtual environment
source venv/bin/activate
```

### Step 2: Install MCP Dependencies
```bash
# Install Python MCP server dependencies
pip install -r mcp-integration/requirements.txt

# Verify installations
pip list | grep -E "(mcp|psycopg|numpy|python-dotenv)"
```

**Expected Output**:
```
mcp                    1.10.1
numpy                  2.3.1
psycopg                3.2.9
psycopg-binary         3.2.9
python-dotenv          1.1.1
```

### Step 3: Database Configuration
```bash
# Test database connectivity
export PGPASSWORD='SecureKnowledgePassword2025'
psql -h localhost -U postgres -d knowledge_persistence -c "SELECT COUNT(*) FROM knowledge_items;"
```

### Step 4: MCP Server Configuration
The Python MCP server uses the following configuration:

**Database Connection**:
```python
# In knowledge-mcp-server.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'knowledge_persistence', 
    'user': 'postgres',
    'password': 'SecureKnowledgePassword2025',
    'port': 5432
}
```

**Required Database Tables**:
- `knowledge_items` - Main knowledge storage with text[] retrieval_triggers
- `ai_sessions` - Session tracking
- `session_knowledge_links` - Knowledge interaction tracking  
- `technical_gotchas` - Problem-solution mapping

---

## 🚀 Deployment Process

### Manual Deployment
```bash
# 1. Copy MCP server files to database server (if needed)
scp mcp-integration/knowledge-mcp-server.py greg@192.168.10.90:~/KnowledgePersistence-AI/mcp-integration/
scp mcp-integration/requirements.txt greg@192.168.10.90:~/KnowledgePersistence-AI/mcp-integration/

# 2. SSH to database server and start MCP server
ssh greg@192.168.10.90

# 3. Navigate and activate environment
cd KnowledgePersistence-AI
source venv/bin/activate

# 4. Start MCP server in background
nohup python mcp-integration/knowledge-mcp-server.py > mcp-server.log 2>&1 &

# 5. Verify server started
ps aux | grep knowledge-mcp-server
tail -f mcp-server.log
```

### Automated Deployment Script
```bash
#!/bin/bash
# deploy-mcp.sh - Automated MCP server deployment

set -e

SERVER="greg@192.168.10.90"
PROJECT_DIR="KnowledgePersistence-AI"

echo "🚀 Deploying MCP Server..."

# Copy files
echo "📁 Copying MCP server files..."
scp mcp-integration/knowledge-mcp-server.py $SERVER:~/$PROJECT_DIR/mcp-integration/
scp mcp-integration/requirements.txt $SERVER:~/$PROJECT_DIR/mcp-integration/

# Deploy and start
echo "🔧 Installing dependencies and starting server..."
ssh $SERVER << EOF
cd $PROJECT_DIR
source venv/bin/activate
pip install -r mcp-integration/requirements.txt

# Stop existing server
pkill -f "python.*knowledge-mcp-server.py" || true
sleep 2

# Start new server
nohup python mcp-integration/knowledge-mcp-server.py > mcp-server.log 2>&1 &

# Verify
sleep 3
if ps aux | grep -q "[p]ython.*knowledge-mcp-server.py"; then
    echo "✅ MCP Server started successfully"
    tail -5 mcp-server.log
else
    echo "❌ MCP Server failed to start"
    cat mcp-server.log
    exit 1
fi
EOF

echo "🎉 MCP Server deployment complete!"
```

---

## 🔍 Verification & Testing

### Health Check Commands
```bash
# 1. Check if MCP server process is running
ssh greg@192.168.10.90 "ps aux | grep knowledge-mcp-server"

# 2. Check server logs
ssh greg@192.168.10.90 "tail -20 KnowledgePersistence-AI/mcp-server.log"

# 3. Test database connectivity
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python -c 'import psycopg; conn = psycopg.connect(\"postgresql://postgres:SecureKnowledgePassword2025@localhost:5432/knowledge_persistence\"); print(\"Database OK\")'"
```

### MCP Tool Testing
Test each MCP tool from Claude Code:

```bash
# 1. Test knowledge retrieval
mcp__knowledge-persistence__get_contextual_knowledge
# Parameters: {"situation": "Testing MCP server health"}

# 2. Test knowledge storage
mcp__knowledge-persistence__store_knowledge
# Parameters: {
#   "knowledge_type": "technical_discovery",
#   "category": "testing", 
#   "title": "MCP Configuration Test",
#   "content": "Testing MCP server configuration and array handling",
#   "retrieval_triggers": ["test", "config", "mcp"]
# }

# 3. Test similarity search
mcp__knowledge-persistence__search_similar_knowledge
# Parameters: {"query": "configuration", "knowledge_type": "technical_discovery"}
```

**Expected Results**: All tools should return JSON responses without errors.

---

## 🛠️ Troubleshooting

### Common Issues

#### Issue 1: MCP Server Won't Start
**Symptoms**: No process found, empty log file
**Solution**:
```bash
# Check Python environment
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python --version"

# Check dependencies
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && pip list | grep mcp"

# Manual start for debugging
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python mcp-integration/knowledge-mcp-server.py"
```

#### Issue 2: Database Connection Errors
**Symptoms**: Connection refused, authentication failed
**Solution**:
```bash
# Check PostgreSQL status
ssh greg@192.168.10.90 "sudo systemctl status postgresql"

# Test direct connection
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -d knowledge_persistence -c 'SELECT version();'"

# Check database exists
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -l | grep knowledge_persistence"
```

#### Issue 3: Array Handling Errors
**Symptoms**: MCP error -32603, retrieval_triggers issues
**Solution**: Verify the array handling fix is in place:
```python
# In knowledge-mcp-server.py around line 194
retrieval_triggers = knowledge_data.get('retrieval_triggers', [])
if retrieval_triggers and isinstance(retrieval_triggers, list):
    triggers_array = retrieval_triggers
else:
    triggers_array = []
```

#### Issue 4: MCP Tools Not Responding
**Symptoms**: Tools not available in Claude Code
**Solution**:
```bash
# Restart MCP server
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && pkill -f knowledge-mcp-server && sleep 2 && source venv/bin/activate && nohup python mcp-integration/knowledge-mcp-server.py > mcp-server.log 2>&1 &"

# Check Claude Code MCP configuration
# Ensure .mcp.json or claude-mcp-config.json points to correct server
```

---

## 📁 File Reference

### Core Configuration Files
- `mcp-integration/knowledge-mcp-server.py` - **Main MCP server** (Python)
- `mcp-integration/requirements.txt` - Python dependencies
- `mcp-integration/claude-mcp-config.json` - Claude Code MCP configuration
- `mcp-integration/.env` - Environment variables (if used)

### Deprecated Files (Do Not Use)
- `mcp-integration/server/knowledge-server.js` - JavaScript server (archived)
- `mcp-integration/package.json` - Node.js dependencies (unused)
- `mcp-integration/package-lock.json` - Node.js lockfile (unused)

### Log Files
- `mcp-server.log` - MCP server runtime logs
- `postgresql.log` - Database server logs (if needed)

---

## 🔒 Security Considerations

### Database Security
- Password authentication required
- Access restricted to localhost on pgdbsrv
- No external database connections allowed

### Network Security
- MCP server only accessible within subnet 192.168.10.x
- SSH key-based authentication to pgdbsrv
- No public internet exposure

### Credential Management
- Database password in configuration files (consider environment variables)
- SSH access via configured keys
- No credentials in version control

---

## 📈 Performance Monitoring

### Key Metrics
- MCP server response times
- Database query performance
- Memory usage on pgdbsrv
- Disk space for knowledge storage

### Monitoring Commands
```bash
# MCP server memory usage
ssh greg@192.168.10.90 "ps aux | grep knowledge-mcp-server"

# Database performance
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -d knowledge_persistence -c 'SELECT COUNT(*) FROM knowledge_items;'"

# Disk usage
ssh greg@192.168.10.90 "df -h | grep -E '(Filesystem|/$)'"
```

---

## 📝 Maintenance

### Regular Tasks
- **Weekly**: Check MCP server logs for errors
- **Monthly**: Verify database connectivity and performance  
- **Quarterly**: Review and update dependencies
- **As needed**: Apply security updates to pgdbsrv

### Backup Considerations
- Database backups handled by PostgreSQL backup strategy
- MCP server configuration files in version control
- Log rotation to prevent disk space issues

---

**Configuration Status**: Production Ready ✅  
**Last Verified**: 2025-07-03  
**Next Review**: Upon infrastructure changes or issues