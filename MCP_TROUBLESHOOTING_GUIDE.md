# MCP Pattern Recognition Troubleshooting Guide
**Date**: 2025-07-03  
**Version**: 1.0  
**Purpose**: Comprehensive troubleshooting guide for KnowledgePersistence-AI MCP server with pattern recognition  

---

## 🎯 **QUICK REFERENCE**

### **Emergency Commands**
```bash
# Check MCP server status
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && timeout 5s python3 knowledge-mcp-server.py"

# Database connectivity test
ssh greg@192.168.10.90 "sudo -u postgres psql -d knowledge_persistence -c 'SELECT COUNT(*) FROM knowledge_items;'"

# Check system resources
ssh greg@192.168.10.90 "free -h && df -h"

# View recent logs
ssh greg@192.168.10.90 "tail -50 KnowledgePersistence-AI/mcp-server.log"
```

### **Common Issues Quick Fix**
1. **SSH Connection Failed** → Check network, verify SSH keys
2. **Database Connection Error** → Verify PostgreSQL service, credentials
3. **No Pattern Predictions** → Lower confidence threshold, check knowledge base
4. **MCP Import Error** → Reinstall dependencies in virtual environment
5. **Low Accuracy Results** → Increase knowledge base size, refine context descriptions

---

## 🚨 **CONNECTION ISSUES**

### **SSH Connection Problems**

#### **Problem: "Connection refused" or SSH timeouts**
**Solutions**:
```bash
# Restart SSH service on database server
ssh greg@192.168.10.90 "sudo systemctl restart ssh"

# Check SSH configuration
ssh greg@192.168.10.90 "sudo sshd -t"

# Regenerate SSH keys if needed
ssh-keygen -f ~/.ssh/id_rsa -N ''
ssh-copy-id greg@192.168.10.90
```

### **Database Connection Issues**

#### **Problem: "Failed to connect to database" errors**
**Solutions**:
```bash
# Restart PostgreSQL service
ssh greg@192.168.10.90 "sudo systemctl restart postgresql"

# Reset database password
ssh greg@192.168.10.90 "sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'SecureKnowledgePassword2025';\""
```

---

## 🛠️ **COMPREHENSIVE DIAGNOSTIC SCRIPT**
```bash
#!/bin/bash
# MCP Health Check Script
echo "=== MCP Knowledge Persistence Health Check ==="

echo "1. Testing SSH connectivity..."
if ssh greg@192.168.10.90 "echo 'SSH OK'"; then
    echo "✓ SSH connection successful"
else
    echo "✗ SSH connection failed"
fi

echo "2. Testing database connectivity..."
if ssh greg@192.168.10.90 "sudo -u postgres psql -d knowledge_persistence -c 'SELECT 1;' >/dev/null 2>&1"; then
    echo "✓ Database connection successful"
else
    echo "✗ Database connection failed"
fi

echo "3. Testing MCP server startup..."
if ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && timeout 5s python3 knowledge-mcp-server.py >/dev/null 2>&1"; then
    echo "✓ MCP server starts successfully"
else
    echo "✗ MCP server startup failed"
fi

echo "=== Health Check Complete ==="
```

---

**Status**: Comprehensive troubleshooting coverage for all MCP pattern recognition components  
**Last Updated**: 2025-07-03