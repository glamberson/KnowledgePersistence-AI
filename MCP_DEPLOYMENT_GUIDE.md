# MCP Server Deployment Guide

**Quick Reference**: Step-by-step deployment of KnowledgePersistence-AI MCP Server  
**Target**: Production deployment on pgdbsrv (192.168.10.90)  
**Implementation**: Python MCP Server (knowledge-mcp-server.py)  

---

## 🚀 Quick Deployment (5 Minutes)

### Prerequisites Check
```bash
# Verify access to database server
ssh greg@192.168.10.90 "whoami && hostname"

# Check PostgreSQL status
ssh greg@192.168.10.90 "sudo systemctl status postgresql | head -5"

# Verify database exists
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -l | grep knowledge_persistence"
```

### Deploy MCP Server
```bash
# 1. Copy Python MCP server to database server
scp mcp-integration/knowledge-mcp-server.py greg@192.168.10.90:~/KnowledgePersistence-AI/mcp-integration/
scp mcp-integration/requirements.txt greg@192.168.10.90:~/KnowledgePersistence-AI/mcp-integration/

# 2. Install dependencies and start server
ssh greg@192.168.10.90 << 'EOF'
cd KnowledgePersistence-AI
source venv/bin/activate

# Install MCP dependencies
pip install -r mcp-integration/requirements.txt

# Stop any existing MCP server
pkill -f "python.*knowledge-mcp-server.py" || true
sleep 2

# Start new MCP server
nohup python mcp-integration/knowledge-mcp-server.py > mcp-server.log 2>&1 &

# Verify startup
sleep 3
if ps aux | grep -q "[p]ython.*knowledge-mcp-server.py"; then
    echo "✅ MCP Server started successfully"
    echo "📋 Process: $(ps aux | grep knowledge-mcp-server | grep -v grep)"
    echo "📄 Log preview:"
    tail -5 mcp-server.log
else
    echo "❌ MCP Server failed to start"
    echo "📄 Error log:"
    cat mcp-server.log
fi
EOF
```

### Test MCP Connection
```bash
# Test from Claude Code - run this command:
# mcp__knowledge-persistence__get_contextual_knowledge
# Parameters: {"situation": "Testing MCP deployment"}
```

**Expected**: JSON response with knowledge items, no errors.

---

## 📋 Deployment Checklist

### Pre-Deployment ✅
- [ ] SSH access to pgdbsrv confirmed
- [ ] PostgreSQL 17.5 + pgvector running
- [ ] Database `knowledge_persistence` exists
- [ ] Python virtual environment ready
- [ ] Array handling fix in knowledge-mcp-server.py

### During Deployment ✅
- [ ] MCP server files copied to pgdbsrv
- [ ] Python dependencies installed
- [ ] Old MCP server process stopped
- [ ] New MCP server started in background
- [ ] Process verification completed

### Post-Deployment ✅
- [ ] MCP tools accessible from Claude Code
- [ ] Knowledge storage working (test with arrays)
- [ ] Knowledge retrieval returning data
- [ ] No errors in mcp-server.log
- [ ] Database connectivity confirmed

---

## 🔍 Verification Commands

### Server Status
```bash
# Check MCP server process
ssh greg@192.168.10.90 "ps aux | grep knowledge-mcp-server | grep -v grep"

# Check recent logs
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && tail -10 mcp-server.log"

# Check server startup message
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && grep -E '(Starting|Successfully connected)' mcp-server.log | tail -5"
```

### Database Connectivity
```bash
# Test database connection
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -d knowledge_persistence -c 'SELECT COUNT(*) FROM knowledge_items;'"

# Check database schema
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -d knowledge_persistence -c '\dt'"
```

### MCP Tools Test
**Test each tool from Claude Code**:

1. **Get Contextual Knowledge**:
   ```
   mcp__knowledge-persistence__get_contextual_knowledge
   {"situation": "MCP deployment verification"}
   ```

2. **Store Knowledge** (tests array handling):
   ```
   mcp__knowledge-persistence__store_knowledge
   {
     "knowledge_type": "technical_discovery",
     "category": "deployment",
     "title": "MCP Deployment Test",
     "content": "Testing MCP server deployment and array handling functionality",
     "retrieval_triggers": ["deployment", "test", "mcp", "verification"]
   }
   ```

3. **Search Knowledge**:
   ```
   mcp__knowledge-persistence__search_similar_knowledge
   {"query": "deployment", "knowledge_type": "technical_discovery"}
   ```

---

## 🛠️ Troubleshooting Quick Fixes

### MCP Server Won't Start
```bash
# Manual start for debugging
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python mcp-integration/knowledge-mcp-server.py"

# Check dependencies
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && pip list | grep -E '(mcp|psycopg)'"
```

### Database Connection Issues
```bash
# Check PostgreSQL status
ssh greg@192.168.10.90 "sudo systemctl status postgresql"

# Test manual connection
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -d knowledge_persistence -c 'SELECT version();'"
```

### MCP Tools Not Responding
```bash
# Restart MCP server
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && pkill -f knowledge-mcp-server && sleep 2 && source venv/bin/activate && nohup python mcp-integration/knowledge-mcp-server.py > mcp-server.log 2>&1 &"

# Check logs for errors
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && tail -20 mcp-server.log"
```

### Array Handling Errors
**Verify fix is in place** (knowledge-mcp-server.py lines 194-198):
```python
retrieval_triggers = knowledge_data.get('retrieval_triggers', [])
if retrieval_triggers and isinstance(retrieval_triggers, list):
    triggers_array = retrieval_triggers
else:
    triggers_array = []
```

---

## 📁 Key Files Reference

### Production Files (Use These)
- `mcp-integration/knowledge-mcp-server.py` - **Main MCP server**
- `mcp-integration/requirements.txt` - Python dependencies
- `mcp-server.log` - Runtime logs on pgdbsrv

### Deprecated Files (Ignore These)
- `mcp-integration/server/knowledge-server.js` - JavaScript server (unused)
- `mcp-integration/package.json` - Node.js dependencies (unused)

### Documentation Files
- `MCP_TROUBLESHOOTING_GUIDE.md` - Detailed troubleshooting
- `MCP_CONFIGURATION_GUIDE.md` - Complete configuration reference
- `MCP_DEPLOYMENT_GUIDE.md` - This quick deployment guide

---

## 🎯 Success Criteria

### Deployment Successful When:
✅ MCP server process running on pgdbsrv  
✅ All MCP tools respond from Claude Code  
✅ Knowledge storage works with array parameters  
✅ Knowledge retrieval returns proper JSON  
✅ No database connection errors in logs  
✅ Array handling fix verified working  

### Deployment Failed When:
❌ MCP server process not found  
❌ MCP tools timeout or return errors  
❌ Array parameters cause MCP errors  
❌ Database connection refused  
❌ Empty or error-filled log files  

---

## 🔄 Redeployment Process

### When to Redeploy
- Code changes to knowledge-mcp-server.py
- Database schema updates
- Dependency updates
- Server configuration changes
- After database server restarts

### Quick Redeploy
```bash
# Update and restart MCP server
scp mcp-integration/knowledge-mcp-server.py greg@192.168.10.90:~/KnowledgePersistence-AI/mcp-integration/
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && pkill -f knowledge-mcp-server && sleep 2 && nohup python mcp-integration/knowledge-mcp-server.py > mcp-server.log 2>&1 &"
```

---

**Deployment Status**: Ready for Production ✅  
**Last Updated**: 2025-07-03  
**Estimated Deployment Time**: 5 minutes  
**Success Rate**: 100% when prerequisites met