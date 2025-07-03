# Administration Guide
## KnowledgePersistence-AI System

**Purpose**: Complete administrative procedures for managing the AI knowledge persistence system  
**Audience**: System administrators and project managers  
**Scope**: Day-to-day operations, per-project configuration, maintenance, and optimization  

---

## 🎯 SYSTEM ADMINISTRATION OVERVIEW

This guide covers the operational aspects of managing a production AI knowledge persistence system, including per-project configuration, monitoring, maintenance, and scaling considerations.

**Administrative Responsibilities**:
- Per-project hook configuration and knowledge patterns
- Database maintenance and optimization
- Performance monitoring and scaling
- Knowledge quality management and cleanup
- Security and access control

---

## 📋 PER-PROJECT CONFIGURATION

### Project-Specific Hook Configuration

Each project can have customized knowledge capture patterns. Create project-specific configurations:

**Project Structure**:
```
/projects/
├── navycmms/
│   ├── .claude/
│   │   └── settings.json
│   └── knowledge-hooks/
│       └── navycmms-hook.py
├── genealogy-research/
│   ├── .claude/
│   │   └── settings.json
│   └── knowledge-hooks/
│       └── genealogy-hook.py
└── clan-henderson/
    ├── .claude/
    │   └── settings.json
    └── knowledge-hooks/
        └── clan-henderson-hook.py
```

### NavyCMMS Project Configuration

**Project-Specific Settings** (`/projects/navycmms/.claude/settings.json`):
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
            "command": "python3 /projects/navycmms/knowledge-hooks/navycmms-hook.py"
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
            "command": "python3 /projects/navycmms/knowledge-hooks/navycmms-hook.py --session-end --project navycmms"
          }
        ]
      }
    ]
  }
}
```

**NavyCMMS-Specific Knowledge Patterns**:
```python
# /projects/navycmms/knowledge-hooks/navycmms-hook.py
def extract_navycmms_knowledge(self, tool_data):
    """Extract maintenance management specific knowledge"""
    knowledge_items = []
    
    # Maintenance procedure discoveries
    if "maintenance" in tool_input.get("file_path", "").lower():
        knowledge_items.append({
            "knowledge_type": "procedural",
            "category": "maintenance_procedures",
            "project": "navycmms",
            "title": f"Maintenance Procedure: {operation_type}",
            "content": f"Discovered maintenance procedure pattern in {file_path}",
            "importance": 80
        })
    
    # Equipment troubleshooting patterns
    if tool_name == "Bash" and "systemctl" in command:
        knowledge_items.append({
            "knowledge_type": "technical_discovery",
            "category": "system_operations",
            "project": "navycmms",
            "title": f"System Operation: {command}",
            "content": f"System management command executed: {command}",
            "importance": 70
        })
    
    return knowledge_items
```

### Genealogy Research Project Configuration

**Genealogy-Specific Settings** (`/projects/genealogy-research/.claude/settings.json`):
```json
{
  "model": "sonnet", 
  "permissions": {
    "allow": ["mcp_*", "WebFetch", "WebSearch"]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /projects/genealogy-research/knowledge-hooks/genealogy-hook.py"
          }
        ]
      }
    ]
  }
}
```

**Genealogy-Specific Knowledge Patterns**:
```python
# /projects/genealogy-research/knowledge-hooks/genealogy-hook.py
def extract_genealogy_knowledge(self, tool_data):
    """Extract genealogical research specific knowledge"""
    knowledge_items = []
    
    # Research source discoveries
    if tool_name in ["WebFetch", "WebSearch"]:
        query = tool_input.get("query", "")
        if any(term in query.lower() for term in ["genealogy", "ancestry", "birth", "death", "marriage"]):
            knowledge_items.append({
                "knowledge_type": "factual",
                "category": "genealogy_sources",
                "project": "genealogy_research",
                "title": f"Research Source: {query[:50]}...",
                "content": f"Genealogical research conducted: {query}",
                "importance": 75
            })
    
    # GEDCOM file processing
    if ".ged" in tool_input.get("file_path", ""):
        knowledge_items.append({
            "knowledge_type": "procedural",
            "category": "data_processing",
            "project": "genealogy_research", 
            "title": f"GEDCOM Processing: {os.path.basename(file_path)}",
            "content": f"GEDCOM file processed: {file_path}",
            "importance": 85
        })
    
    return knowledge_items
```

---

## 📋 DATABASE ADMINISTRATION

### Database Maintenance Tasks

**Daily Operations**:
```bash
# Check database health
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables 
ORDER BY n_tup_ins DESC;"

# Monitor database size
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "
SELECT 
    pg_size_pretty(pg_total_relation_size('knowledge_items')) as knowledge_items_size,
    pg_size_pretty(pg_database_size('knowledge_persistence')) as total_db_size;"

# Check vector index performance
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%vector%';"
```

**Weekly Maintenance**:
```bash
# Vacuum and analyze tables
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "
VACUUM ANALYZE knowledge_items;
VACUUM ANALYZE ai_sessions;
VACUUM ANALYZE session_knowledge_links;
VACUUM ANALYZE technical_gotchas;"

# Update table statistics
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "
ANALYZE knowledge_items;
REINDEX INDEX CONCURRENTLY idx_knowledge_items_embedding;"
```

### Knowledge Quality Management

**Identify Low-Quality Knowledge**:
```sql
-- Find knowledge items with low importance scores
SELECT id, title, importance_score, created_at 
FROM knowledge_items 
WHERE importance_score < 30 
ORDER BY created_at DESC;

-- Find duplicate or near-duplicate titles
SELECT title, COUNT(*) as count 
FROM knowledge_items 
GROUP BY title 
HAVING COUNT(*) > 1;

-- Find orphaned knowledge (not linked to sessions)
SELECT ki.id, ki.title 
FROM knowledge_items ki 
LEFT JOIN session_knowledge_links skl ON ki.id = skl.knowledge_item_id 
WHERE skl.knowledge_item_id IS NULL;
```

**Knowledge Cleanup Procedures**:
```sql
-- Archive old low-importance knowledge (older than 90 days, importance < 40)
BEGIN;

-- Create archive table if not exists
CREATE TABLE IF NOT EXISTS knowledge_items_archive (LIKE knowledge_items INCLUDING ALL);

-- Move low-importance old items to archive
INSERT INTO knowledge_items_archive 
SELECT * FROM knowledge_items 
WHERE importance_score < 40 
  AND created_at < NOW() - INTERVAL '90 days';

-- Delete from main table
DELETE FROM knowledge_items 
WHERE importance_score < 40 
  AND created_at < NOW() - INTERVAL '90 days';

COMMIT;
```

---

## 📋 PERFORMANCE MONITORING

### System Performance Metrics

**API Server Monitoring**:
```bash
# Create monitoring script
cat > /home/greg/monitor-knowledge-system.sh << 'EOF'
#!/bin/bash

echo "=== Knowledge Persistence System Health Check ==="
echo "Timestamp: $(date)"
echo

# API Health Check
echo "API Server Status:"
curl -s -w "Response Time: %{time_total}s\n" http://192.168.10.90:8090/health || echo "API Server DOWN"
echo

# Database Connection Test
echo "Database Status:"
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "SELECT 'Database OK' as status;" 2>/dev/null || echo "Database DOWN"
echo

# Knowledge Items Count
echo "Knowledge Items:"
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -t -c "SELECT COUNT(*) FROM knowledge_items;" 2>/dev/null | xargs echo "Total Items:"

# Recent Activity (last 24 hours)
echo "Recent Activity (24h):"
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -t -c "SELECT COUNT(*) FROM knowledge_items WHERE created_at > NOW() - INTERVAL '24 hours';" 2>/dev/null | xargs echo "New Items:"

# Disk Usage
echo "Disk Usage:"
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -t -c "SELECT pg_size_pretty(pg_database_size('knowledge_persistence'));" 2>/dev/null | xargs echo "Database Size:"

echo "=== End Health Check ==="
EOF

chmod +x /home/greg/monitor-knowledge-system.sh

# Run monitoring
./monitor-knowledge-system.sh
```

**Performance Optimization Queries**:
```sql
-- Identify slow queries
SELECT query, mean_time, calls, rows 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Monitor vector search performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT id, title, embedding <-> '[0.1,0.2,...]'::vector as distance 
FROM knowledge_items 
ORDER BY embedding <-> '[0.1,0.2,...]'::vector 
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE tablename = 'knowledge_items';
```

---

## 📋 SCALING CONSIDERATIONS

### Database Scaling Recommendations

**Current Capacity** (Single PostgreSQL instance):
- Expected knowledge items: ~100,000 items/year
- Storage requirement: ~100MB/year
- Vector searches: <100ms response time
- Concurrent sessions: 10-20 users

**Scaling Triggers**:
- Database size > 10GB
- Query response time > 500ms
- Concurrent users > 50
- Knowledge items > 1M

**Scaling Options**:

1. **Vertical Scaling**:
```bash
# Monitor current resource usage
htop
iostat -x 1
free -h

# Database tuning recommendations
sudo nano /etc/postgresql/17/main/postgresql.conf

# Increase memory settings for larger datasets
shared_buffers = 256MB          # 25% of RAM
effective_cache_size = 1GB      # 75% of RAM  
work_mem = 64MB                 # For vector operations
maintenance_work_mem = 256MB    # For index maintenance
```

2. **Storage Optimization**:
```bash
# Create dedicated volume for database
sudo lvcreate -L 50G -n knowledge_data vg_data
sudo mkfs.ext4 /dev/vg_data/knowledge_data
sudo mount /dev/vg_data/knowledge_data /var/lib/postgresql/17/main

# Configure tablespace for knowledge data
sudo -u postgres psql -d knowledge_persistence -c "
CREATE TABLESPACE knowledge_data LOCATION '/var/lib/postgresql/17/knowledge_data';
ALTER TABLE knowledge_items SET TABLESPACE knowledge_data;
"
```

3. **Read Replica Setup** (for high-query workloads):
```bash
# Configure streaming replication
# Master server configuration
echo "wal_level = replica" >> /etc/postgresql/17/main/postgresql.conf
echo "max_wal_senders = 3" >> /etc/postgresql/17/main/postgresql.conf

# Create replication user
sudo -u postgres psql -c "CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'replica_password';"
```

---

## 📋 SECURITY ADMINISTRATION

### Access Control

**User Management**:
```sql
-- Create project-specific database users
CREATE USER navycmms_user WITH PASSWORD 'navycmms_secure_password';
CREATE USER genealogy_user WITH PASSWORD 'genealogy_secure_password';

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE ON knowledge_items TO navycmms_user;
GRANT SELECT, INSERT, UPDATE ON ai_sessions TO navycmms_user;

-- Row-level security for project isolation
ALTER TABLE knowledge_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY project_isolation ON knowledge_items
FOR ALL TO navycmms_user
USING (context_data->>'project' = 'navycmms');
```

**Audit Logging**:
```bash
# Enable PostgreSQL audit logging
sudo nano /etc/postgresql/17/main/postgresql.conf

# Add audit settings
log_statement = 'mod'           # Log all modifications
log_min_duration_statement = 1000  # Log slow queries
log_connections = on
log_disconnections = on

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Backup and Recovery

**Automated Backup Script**:
```bash
cat > /home/greg/backup-knowledge-db.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backup/knowledge"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="knowledge_persistence_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
PGPASSWORD=SecureKnowledgePassword2025 pg_dump \
  -h 192.168.10.90 \
  -U postgres \
  -d knowledge_persistence \
  --verbose \
  --clean \
  --create \
  > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/$BACKUP_FILE.gz"
EOF

chmod +x /home/greg/backup-knowledge-db.sh

# Schedule daily backups
echo "0 2 * * * /home/greg/backup-knowledge-db.sh" | crontab -
```

---

## 📋 TROUBLESHOOTING PROCEDURES

### Common Administrative Issues

1. **Database Performance Degradation**:
```bash
# Check for long-running queries
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "
SELECT pid, usename, application_name, state, query_start, query 
FROM pg_stat_activity 
WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';"

# Kill problematic queries if necessary
# SELECT pg_terminate_backend(PID);
```

2. **Hook Configuration Issues**:
```bash
# Verify hook script functionality
python3 /projects/navycmms/knowledge-hooks/navycmms-hook.py --test

# Check Claude Code settings syntax
python3 -m json.tool ~/.claude/settings.json

# Monitor hook execution
tail -f /tmp/claude-hook-debug.log
```

3. **Storage Space Issues**:
```bash
# Check database size by table
PGPASSWORD=SecureKnowledgePassword2025 psql -h 192.168.10.90 -U postgres -d knowledge_persistence -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Implement emergency cleanup if needed
# Run knowledge cleanup procedures (see above)
```

---

## 📋 PROJECT ONBOARDING CHECKLIST

**New Project Setup**:
- [ ] Create project directory structure
- [ ] Configure project-specific Claude Code settings
- [ ] Develop project-specific knowledge patterns
- [ ] Set up project database user and permissions
- [ ] Test hook functionality with project workflows
- [ ] Configure project-specific monitoring
- [ ] Document project-specific procedures

**Ongoing Project Management**:
- [ ] Weekly knowledge quality review
- [ ] Monthly performance assessment  
- [ ] Quarterly knowledge cleanup
- [ ] Annual backup and archival procedures

---

## 🎯 ADMINISTRATIVE SUCCESS METRICS

**System Health Indicators**:
- API response time < 500ms
- Database query time < 100ms
- Hook execution success rate > 99%
- Knowledge storage success rate > 99%

**Knowledge Quality Metrics**:
- Average knowledge importance score > 60
- Knowledge retrieval accuracy > 85%
- Cross-session knowledge utilization > 70%
- Duplicate knowledge rate < 5%

**Project Efficiency Indicators**:
- Time to deploy new project < 2 hours
- Knowledge onboarding completion < 1 week
- Project-specific pattern effectiveness > 80%
- Inter-project knowledge sharing value score > 70%

This administration guide ensures your AI knowledge persistence system remains performant, secure, and valuable across multiple projects and use cases.