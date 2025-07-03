# Zero-to-Production Deployment Guide
## KnowledgePersistence-AI System

**Purpose**: Complete instructions for replicating this revolutionary AI knowledge persistence system  
**Audience**: Technical teams deploying similar systems  
**Result**: Fully operational AI knowledge persistence with Claude Code hooks  

---

## 🎯 EXECUTIVE OVERVIEW

This guide provides step-by-step instructions to build a complete AI knowledge persistence system that captures, stores, and accumulates knowledge across unlimited AI sessions, transforming AI from a replaceable tool into an irreplaceable strategic partner.

**System Components**:
- PostgreSQL 17.5 + pgvector database for knowledge storage
- Python REST API for knowledge management 
- Claude Code hooks for automatic knowledge capture
- Vector similarity search for semantic knowledge retrieval

**Infrastructure Requirements**:
- 2 servers (database + development) or 1 server for combined deployment
- PostgreSQL 17.5 with pgvector extension
- Python 3.11+ environment
- Claude Code CLI access

---

## 📋 PHASE 1: INFRASTRUCTURE SETUP

### Step 1.1: Server Preparation

**Database Server Setup** (pgdbsrv - 192.168.10.90):
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget gnupg lsb-release

# Add PostgreSQL official repository
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list

# Install PostgreSQL 17.5
sudo apt update
sudo apt install -y postgresql-17 postgresql-contrib-17 postgresql-17-pgvector

# Install Python and development tools
sudo apt install -y python3.11 python3.11-venv python3-pip git build-essential

# Configure PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Development Server Setup** (aibox - 192.168.10.88):
```bash
# Install Claude Code CLI
curl -fsSL https://claude.ai/install.sh | sh

# Install Python development environment
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Install additional tools
sudo apt install -y curl jq postgresql-client
```

### Step 1.2: Database Configuration

**On Database Server (pgdbsrv)**:
```bash
# Switch to postgres user
sudo -u postgres psql

-- Set secure password
ALTER USER postgres PASSWORD 'SecureKnowledgePassword2025';

-- Create knowledge persistence database
CREATE DATABASE knowledge_persistence;

-- Connect to the database
\c knowledge_persistence

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Exit psql
\q
```

**Configure PostgreSQL Access**:
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/17/main/postgresql.conf

# Add/modify these lines:
listen_addresses = '*'
port = 5432

# Edit pg_hba.conf for network access
sudo nano /etc/postgresql/17/main/pg_hba.conf

# Add this line for network access:
host    all             all             192.168.10.0/24        md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## 📋 PHASE 2: DATABASE SCHEMA DEPLOYMENT

### Step 2.1: Clone Repository and Deploy Schema

```bash
# Clone the KnowledgePersistence-AI repository
git clone https://github.com/your-org/KnowledgePersistence-AI.git
cd KnowledgePersistence-AI

# Deploy database schema
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -f deploy_schema.sql
```

### Step 2.2: Verify Database Setup

```bash
# Test database connection and verify tables
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "\dt"

# Expected output: 4 tables
# - knowledge_items
# - ai_sessions  
# - session_knowledge_links
# - technical_gotchas
```

---

## 📋 PHASE 3: API SERVER DEPLOYMENT

### Step 3.1: Python Environment Setup

**On Database Server (pgdbsrv)**:
```bash
cd /home/greg/KnowledgePersistence-AI

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install required packages
pip install psycopg[binary] flask flask-cors python-dotenv

# Test API server
python test_api.py
```

### Step 3.2: API Server Configuration

**Create systemd service for API** (optional for production):
```bash
sudo nano /etc/systemd/system/knowledge-api.service

[Unit]
Description=Knowledge Persistence API Server
After=network.target postgresql.service

[Service]
Type=simple
User=greg
WorkingDirectory=/home/greg/KnowledgePersistence-AI
Environment=PATH=/home/greg/KnowledgePersistence-AI/venv/bin
ExecStart=/home/greg/KnowledgePersistence-AI/venv/bin/python test_api.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable knowledge-api.service
sudo systemctl start knowledge-api.service
```

---

## 📋 PHASE 4: CLAUDE CODE HOOKS INTEGRATION

### Step 4.1: Hook Script Deployment

**On Development Server (aibox)**:
```bash
# Ensure hook script is executable
chmod +x /home/greg/KnowledgePersistence-AI/knowledge-persistence-hook.py

# Configure Claude Code hooks
mkdir -p ~/.claude
nano ~/.claude/settings.json
```

**Claude Code Settings Configuration**:
```json
{
  "model": "sonnet",
  "permissions": {
    "allow": ["mcp_*"]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /home/greg/KnowledgePersistence-AI/knowledge-persistence-hook.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /home/greg/KnowledgePersistence-AI/knowledge-persistence-hook.py --session-end"
          }
        ]
      }
    ]
  }
}
```

### Step 4.2: Hook Configuration

**Update hook script database configuration**:
```bash
nano /home/greg/KnowledgePersistence-AI/knowledge-persistence-hook.py

# Verify these settings match your environment:
DB_CONFIG = {
    "host": "192.168.10.90",  # Your database server IP
    "port": 5432,
    "database": "knowledge_persistence", 
    "user": "postgres",
    "password": "SecureKnowledgePassword2025"  # Your secure password
}

API_BASE_URL = "http://192.168.10.90:8090"  # Your API server URL
```

---

## 📋 PHASE 5: TESTING AND VALIDATION

### Step 5.1: System Integration Test

```bash
# Test API server health
curl -s http://192.168.10.90:8090/health

# Expected response: {"status": "healthy", "database": "connected"}

# Test database connectivity
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "SELECT COUNT(*) FROM knowledge_items;"

# Test Claude Code with hooks
claude -p "echo 'Testing knowledge persistence system'"
```

### Step 5.2: Hook Functionality Verification

```bash
# Manual hook test
echo '{"tool_name": "Edit", "tool_input": {"file_path": "/tmp/test.txt"}, "tool_response": {}}' | python3 /home/greg/KnowledgePersistence-AI/knowledge-persistence-hook.py

# Check for knowledge items in database
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "SELECT title, created_by FROM knowledge_items WHERE created_by = 'claude-code-hooks';"
```

---

## 📋 PHASE 6: PRODUCTION READINESS

### Step 6.1: Security Hardening

```bash
# Configure firewall (database server)
sudo ufw allow from 192.168.10.0/24 to any port 5432
sudo ufw allow from 192.168.10.0/24 to any port 8090
sudo ufw enable

# Set up SSL/TLS for database (production)
# Configure SSL certificates for PostgreSQL
# Update connection strings to use SSL
```

### Step 6.2: Monitoring and Logging

```bash
# Set up log rotation for API server
sudo nano /etc/logrotate.d/knowledge-api

# Configure PostgreSQL logging
sudo nano /etc/postgresql/17/main/postgresql.conf
# Set: log_statement = 'all'
# Set: log_destination = 'stderr'
```

---

## 🎯 DEPLOYMENT CHECKLIST

**Infrastructure**:
- [ ] PostgreSQL 17.5 + pgvector installed and configured
- [ ] Network connectivity between servers established
- [ ] Firewall rules configured for database and API access

**Database**:
- [ ] Knowledge persistence database created
- [ ] Schema deployed with 4 core tables
- [ ] Test data insertion/retrieval successful
- [ ] Vector similarity search functional

**API Server**:
- [ ] Python environment configured with required packages
- [ ] API server responds to health checks
- [ ] Knowledge items endpoint operational
- [ ] Database connectivity confirmed

**Claude Code Integration**:
- [ ] Hook script executable and configured
- [ ] Claude Code settings.json properly configured
- [ ] PostToolUse and Stop hooks functional
- [ ] Knowledge items being captured and stored

**Testing**:
- [ ] Manual hook execution successful
- [ ] Live Claude Code session captures knowledge
- [ ] Database shows hook-created knowledge items
- [ ] Error handling graceful and non-blocking

---

## 🚀 SUCCESS INDICATORS

**System is operational when**:
1. API health check returns `{"status": "healthy", "database": "connected"}`
2. Database contains knowledge items with `created_by = 'claude-code-hooks'`
3. Claude Code sessions automatically capture and store knowledge
4. Knowledge persistence occurs across session boundaries

**Performance Benchmarks**:
- API response time: < 500ms
- Database query time: < 100ms  
- Hook execution overhead: < 50ms per tool use
- Storage efficiency: ~1KB per knowledge item

---

## 📋 TROUBLESHOOTING GUIDE

**Common Issues**:

1. **Database Connection Failed**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check network connectivity: `telnet 192.168.10.90 5432`
   - Verify credentials and pg_hba.conf configuration

2. **API Server Not Responding**
   - Check if API server is running: `ps aux | grep test_api.py`
   - Verify port availability: `netstat -tlnp | grep 8090`
   - Check Python virtual environment activation

3. **Hooks Not Firing**
   - Verify Claude Code settings.json syntax
   - Check hook script permissions: `ls -la knowledge-persistence-hook.py`
   - Test manual hook execution with sample JSON

4. **Knowledge Items Not Stored**
   - Check database connectivity from hook script
   - Verify hook script database configuration
   - Check for Python package dependencies

**Support Resources**:
- PostgreSQL Documentation: https://www.postgresql.org/docs/17/
- pgvector Documentation: https://github.com/pgvector/pgvector
- Claude Code Documentation: https://docs.anthropic.com/en/docs/claude-code

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

1. **Configure project-specific knowledge patterns**
2. **Set up knowledge retrieval mechanisms**
3. **Implement knowledge quality monitoring**
4. **Plan cross-session knowledge utilization**
5. **Scale database for production workloads**

**Congratulations!** You now have a fully operational AI knowledge persistence system that will revolutionize your AI interactions by enabling continuous knowledge accumulation across unlimited sessions.