# MCP Server Setup & Configuration Guide
**Date**: 2025-07-03  
**Version**: 1.0  
**Purpose**: Complete setup and configuration guide for KnowledgePersistence-AI MCP server with pattern recognition  

---

## 🎯 **OVERVIEW**

This guide provides step-by-step instructions for setting up and configuring the enhanced MCP (Model Context Protocol) server with pattern recognition capabilities. The setup involves a distributed architecture with Claude Code connecting to a remote database server via SSH.

### **Architecture Summary**
```
[Claude Code Client] ◄─SSH─► [Database Server] ◄─TCP─► [PostgreSQL + pgvector]
     (aibox)                   (pgdbsrv)                 (localhost:5432)
  192.168.10.88              192.168.10.90
```

---

## 📋 **PREREQUISITES**

### **Infrastructure Requirements**
- **Database Server**: Debian 12 with PostgreSQL 17.5 + pgvector
- **Client Machine**: Linux system with Claude Code installed
- **Network**: SSH connectivity between client and database server
- **Credentials**: Database user with full access to knowledge_persistence database

### **Software Dependencies**
- Python 3.11+
- PostgreSQL 17.5 with pgvector extension
- SSH key-based authentication
- Virtual environment with MCP and psycopg3

---

## 🏗️ **INFRASTRUCTURE SETUP**

### **1. Database Server Configuration**

#### **PostgreSQL Installation & Setup**
```bash
# On pgdbsrv (192.168.10.90)
# Install PostgreSQL 17.5 with pgvector
sudo apt update
sudo apt install postgresql-17 postgresql-contrib-17

# Install pgvector extension
sudo apt install postgresql-17-pgvector

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### **Database Initialization**
```bash
# Create knowledge persistence database
sudo -u postgres createdb knowledge_persistence

# Set up database user and permissions
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'SecureKnowledgePassword2025';"

# Enable pgvector extension
sudo -u postgres psql -d knowledge_persistence -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

#### **Deploy Database Schema**
```bash
# Copy and execute schema deployment
scp deploy_schema.sql greg@192.168.10.90:~/
ssh greg@192.168.10.90 "sudo -u postgres psql -d knowledge_persistence -f deploy_schema.sql"
```

### **2. Python Environment Setup**

#### **Virtual Environment Creation**
```bash
# On database server (pgdbsrv)
ssh greg@192.168.10.90
cd /home/greg
git clone <repository> KnowledgePersistence-AI
cd KnowledgePersistence-AI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install --upgrade pip
pip install psycopg[binary] numpy python-dotenv
```

#### **MCP Dependencies Installation**
```bash
# Install MCP framework and dependencies
pip install mcp
pip install anyio httpx-sse httpx jsonschema pydantic-settings pydantic
pip install python-multipart sse-starlette starlette uvicorn

# Verify installation
python3 -c "import mcp; print('MCP installation successful')"
```

### **3. SSH Configuration**

#### **SSH Key Setup**
```bash
# On client machine (aibox)
# Generate SSH key if not exists
ssh-keygen -t rsa -b 4096 -C "claude-code-mcp"

# Copy public key to database server
ssh-copy-id greg@192.168.10.90

# Test SSH connectivity
ssh greg@192.168.10.90 "whoami && hostname"
```

#### **SSH Configuration Optimization**
```bash
# Add to ~/.ssh/config on client
Host pgdbsrv
    HostName 192.168.10.90
    User greg
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

---

## ⚙️ **MCP SERVER CONFIGURATION**

### **1. Server File Deployment**
```bash
# Copy enhanced MCP server to database host
scp mcp-integration/knowledge-mcp-server.py greg@192.168.10.90:KnowledgePersistence-AI/

# Set executable permissions
ssh greg@192.168.10.90 "chmod +x KnowledgePersistence-AI/knowledge-mcp-server.py"
```

### **2. Database Connection Configuration**
```python
# In knowledge-mcp-server.py - Database Configuration
DB_CONFIG = {
    "host": "192.168.10.90",      # Database server IP
    "port": 5432,                 # PostgreSQL port
    "database": "knowledge_persistence",  # Database name
    "user": "postgres",           # Database user
    "password": "SecureKnowledgePassword2025"  # Database password
}
```

### **3. Pattern Recognition Settings**
```python
# Default configuration parameters
DEFAULT_MIN_IMPORTANCE = 40       # Minimum importance for pattern analysis
DEFAULT_CONFIDENCE_THRESHOLD = 0.3  # 30% minimum confidence for predictions
DEFAULT_MAX_PREDICTIONS = 10      # Maximum predictions per request
DEFAULT_ANALYSIS_TYPES = ["cluster", "temporal", "progression", "all"]
```

### **4. Logging Configuration**
```python
# Logging setup in MCP server
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/greg/KnowledgePersistence-AI/mcp-server.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🔧 **CLAUDE CODE INTEGRATION**

### **1. MCP Configuration File**
Create or update `.mcp.json` in your project directory:

```json
{
  "mcpServers": {
    "knowledge-persistence": {
      "command": "ssh",
      "args": [
        "greg@192.168.10.90", 
        "cd KnowledgePersistence-AI && source venv/bin/activate && python3 knowledge-mcp-server.py"
      ],
      "env": {
        "DATABASE_URL": "postgresql://postgres:SecureKnowledgePassword2025@192.168.10.90:5432/knowledge_persistence"
      }
    }
  }
}
```

### **2. Global Claude Code Configuration**
For system-wide availability, update `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "knowledge-persistence": {
      "command": "ssh",
      "args": [
        "greg@192.168.10.90", 
        "cd KnowledgePersistence-AI && source venv/bin/activate && python3 knowledge-mcp-server.py"
      ],
      "env": {
        "DATABASE_URL": "postgresql://postgres:SecureKnowledgePassword2025@192.168.10.90:5432/knowledge_persistence"
      }
    }
  },
  "features": {
    "mcp": true,
    "knowledgePersistence": true
  }
}
```

### **3. Environment Variables**
Optional environment-based configuration:

```bash
# Export on client machine for additional configuration
export MCP_KNOWLEDGE_HOST="192.168.10.90"
export MCP_KNOWLEDGE_USER="greg"
export MCP_KNOWLEDGE_DB="knowledge_persistence"
export MCP_DEBUG_MODE="true"  # Enable verbose logging
```

---

## 🧪 **TESTING & VALIDATION**

### **1. Database Connectivity Test**
```bash
# Test PostgreSQL connection
ssh greg@192.168.10.90 "sudo -u postgres psql -d knowledge_persistence -c 'SELECT COUNT(*) FROM knowledge_items;'"

# Test API server functionality
ssh greg@192.168.10.90 "curl -s http://localhost:8090/health"
```

### **2. MCP Server Startup Test**
```bash
# Test MCP server initialization
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && timeout 10s python3 knowledge-mcp-server.py"

# Expected output:
# INFO:knowledge-mcp-server:Successfully connected to knowledge database
# INFO:knowledge-mcp-server:Starting Knowledge Persistence MCP Server...
```

### **3. Pattern Recognition Test**
```bash
# Test pattern recognition functionality
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python3 pattern_recognition_prototype.py"

# Verify pattern analysis output with 115+ knowledge items
```

### **4. Claude Code Integration Test**
Within a Claude Code session:
```python
# Test basic connectivity
get_session_context(project="KnowledgePersistence-AI")

# Test pattern recognition
discover_knowledge_patterns(analysis_type="all")

# Test predictive capabilities
predict_knowledge_needs(current_context="testing MCP integration")
```

---

## 📊 **PERFORMANCE CONFIGURATION**

### **1. Database Optimization**
```sql
-- Execute on PostgreSQL server for optimal performance
-- Index optimization for pattern queries
CREATE INDEX IF NOT EXISTS idx_knowledge_importance ON knowledge_items(importance_score);
CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge_items(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_items(knowledge_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_items(category);

-- Vector similarity optimization
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_items USING ivfflat (embedding vector_cosine_ops);

-- JSONB optimization for context queries
CREATE INDEX IF NOT EXISTS idx_knowledge_context ON knowledge_items USING gin(context_data);
```

### **2. Connection Pool Configuration**
```python
# In knowledge-mcp-server.py - Add connection pooling
import psycopg_pool

# Connection pool for better performance
pool = psycopg_pool.ConnectionPool(
    conninfo=conn_string,
    min_size=2,
    max_size=10,
    timeout=30.0
)
```

### **3. SSH Connection Optimization**
```bash
# Client-side SSH optimization in ~/.ssh/config
Host pgdbsrv
    HostName 192.168.10.90
    User greg
    ControlMaster auto
    ControlPath ~/.ssh/cm_socket_%r@%h:%p
    ControlPersist 10m
    Compression yes
    ServerAliveInterval 60
```

---

## 🔐 **SECURITY CONFIGURATION**

### **1. Database Security**
```sql
-- Restrict database access
-- Create dedicated MCP user (optional)
CREATE USER mcp_user WITH PASSWORD 'SecureMCPPassword2025';
GRANT CONNECT ON DATABASE knowledge_persistence TO mcp_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO mcp_user;
```

### **2. SSH Security**
```bash
# Secure SSH configuration on database server
sudo nano /etc/ssh/sshd_config

# Add security settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers greg
ClientAliveInterval 300
ClientAliveCountMax 2
```

### **3. Network Security**
```bash
# Firewall configuration on database server
sudo ufw allow from 192.168.10.88 to any port 22
sudo ufw allow from 192.168.10.88 to any port 5432
sudo ufw enable
```

---

## 📝 **LOGGING & MONITORING**

### **1. MCP Server Logging**
```python
# Enhanced logging configuration
import logging
from logging.handlers import RotatingFileHandler

# Configure rotating log files
log_handler = RotatingFileHandler(
    '/home/greg/KnowledgePersistence-AI/mcp-server.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

logger = logging.getLogger("knowledge-mcp-server")
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)
```

### **2. Database Activity Monitoring**
```sql
-- Enable PostgreSQL logging
-- In postgresql.conf:
log_statement = 'mod'
log_min_duration_statement = 1000  -- Log queries > 1 second
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### **3. System Resource Monitoring**
```bash
# Monitor system resources
# Add to crontab for regular monitoring
*/5 * * * * /usr/bin/free -h >> /var/log/memory-usage.log
*/5 * * * * /usr/bin/df -h >> /var/log/disk-usage.log
```

---

## 🔄 **BACKUP & RECOVERY**

### **1. Database Backup**
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backup/knowledge-persistence"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
sudo -u postgres pg_dump knowledge_persistence > "$BACKUP_DIR/knowledge_persistence_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/knowledge_persistence_$DATE.sql"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
```

### **2. Configuration Backup**
```bash
# Backup critical configuration files
tar -czf /backup/mcp-config-$(date +%Y%m%d).tar.gz \
    /home/greg/KnowledgePersistence-AI/knowledge-mcp-server.py \
    /home/greg/KnowledgePersistence-AI/.mcp.json \
    /etc/postgresql/17/main/postgresql.conf
```

### **3. Recovery Procedures**
```bash
# Database recovery from backup
sudo -u postgres createdb knowledge_persistence_recovery
sudo -u postgres psql knowledge_persistence_recovery < backup_file.sql

# MCP server recovery
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && git pull origin main"
scp mcp-integration/knowledge-mcp-server.py greg@192.168.10.90:KnowledgePersistence-AI/
```

---

## 🎛️ **ADVANCED CONFIGURATION**

### **1. Multi-Environment Setup**
```json
# Development environment configuration
{
  "mcpServers": {
    "knowledge-persistence-dev": {
      "command": "ssh",
      "args": ["greg@192.168.10.91", "cd KnowledgePersistence-AI && source venv/bin/activate && python3 knowledge-mcp-server.py"],
      "env": {
        "DATABASE_URL": "postgresql://postgres:DevPassword@192.168.10.91:5432/knowledge_persistence_dev",
        "MCP_ENV": "development"
      }
    }
  }
}
```

### **2. Load Balancing Configuration**
```bash
# HAProxy configuration for multiple MCP servers
# /etc/haproxy/haproxy.cfg
backend mcp_servers
    balance roundrobin
    server mcp1 192.168.10.90:8090 check
    server mcp2 192.168.10.91:8090 check backup
```

### **3. Container Deployment**
```dockerfile
# Dockerfile for containerized MCP server
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY knowledge-mcp-server.py .
EXPOSE 8090

CMD ["python", "knowledge-mcp-server.py"]
```

---

## 📋 **MAINTENANCE CHECKLIST**

### **Daily**
- [ ] Check MCP server logs for errors
- [ ] Verify database connectivity
- [ ] Monitor system resource usage

### **Weekly**
- [ ] Review pattern recognition accuracy
- [ ] Analyze knowledge base growth
- [ ] Check backup integrity
- [ ] Update dependency packages

### **Monthly**
- [ ] Optimize database indexes
- [ ] Review security configurations
- [ ] Update documentation
- [ ] Performance benchmarking

---

**Status**: Production-ready configuration with pattern recognition capabilities  
**Last Updated**: 2025-07-03  
**Next Review**: Weekly optimization and security assessment