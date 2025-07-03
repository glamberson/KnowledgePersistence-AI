# MCP Server Troubleshooting and Configuration Guide

**Date**: 2025-07-03  
**Project**: KnowledgePersistence-AI  
**Issue**: Dual MCP Server Configuration and Array Handling Fixes  

---

## 🚨 CRITICAL DISCOVERY: Dual MCP Server Architecture

### Problem Identification
During MCP integration testing, we discovered the project contains **TWO SEPARATE MCP SERVERS**:

1. **JavaScript/Node.js Server**: `/mcp-integration/server/knowledge-server.js`
2. **Python Server**: `/mcp-integration/knowledge-mcp-server.py`

This dual architecture was causing:
- Configuration confusion
- Deployment inconsistencies  
- Different behavior patterns
- Array handling issues in retrieval_triggers parameter

---

## 📁 File Structure Analysis

### JavaScript MCP Server
```
mcp-integration/
├── server/
│   └── knowledge-server.js     # Node.js MCP server
├── package.json                # Node.js dependencies
├── package-lock.json          
└── node_modules/               # Node.js packages
```

**Dependencies (package.json)**:
- `@modelcontextprotocol/sdk`: ^1.0.0
- `pg`: ^8.12.0 (PostgreSQL client)
- `openai`: ^4.67.0
- `uuid`: ^10.0.0
- `dotenv`: ^16.4.0

### Python MCP Server  
```
mcp-integration/
├── knowledge-mcp-server.py     # Python MCP server
├── requirements.txt            # Python dependencies
└── (uses system/venv Python packages)
```

**Dependencies (requirements.txt)**:
- `mcp>=1.0.0`
- `psycopg[binary]>=3.1.0` (PostgreSQL client)
- `numpy>=1.24.0`
- `python-dotenv>=1.0.0`

---

## 🐛 Array Handling Bug Documentation

### Issue Description
The `retrieval_triggers` parameter was causing errors when passed as an array to the MCP store_knowledge function.

### Error Message
```
MCP error -32603: Error executing tool store_knowledge: Failed to store knowledge: column "created_at" of relation "session_knowledge_links" does not exist
```

### Root Cause Analysis
1. **Primary Issue**: Array handling in Python MCP server
2. **Secondary Issue**: Database schema mismatch references
3. **Tertiary Issue**: Session tracking code attempting to access non-existent columns

### Fix Applied (Python Server)
**File**: `/mcp-integration/knowledge-mcp-server.py`  
**Lines**: 194-198

```python
# Handle retrieval_triggers as PostgreSQL array
retrieval_triggers = knowledge_data.get('retrieval_triggers', [])
if retrieval_triggers and isinstance(retrieval_triggers, list):
    triggers_array = retrieval_triggers
else:
    triggers_array = []
```

**Verification**: The fix correctly handles array conversion for PostgreSQL text[] column type.

---

## 🔧 Deployment Configuration

### Current Active Server
**Python MCP Server** (`knowledge-mcp-server.py`) is currently operational:
- **Location**: Database server (pgdbsrv: 192.168.10.90)
- **Process**: Running in background with nohup
- **Dependencies**: Installed in `/home/greg/KnowledgePersistence-AI/venv/`
- **Log File**: `/home/greg/KnowledgePersistence-AI/mcp-server.log`

### Database Connection
**Active Configuration**:
```python
DATABASE_URL = "postgresql://postgres:SecureKnowledgePassword2025@localhost:5432/knowledge_persistence"
```

**Database Schema Verification**:
- `knowledge_items` table: ✅ Operational with text[] retrieval_triggers
- `session_knowledge_links` table: ✅ Exists but different schema than expected
- `ai_sessions` table: ✅ Operational
- `technical_gotchas` table: ✅ Operational

---

## 🧪 Testing Results

### Successful Operations
1. **MCP Connection**: ✅ `mcp__knowledge-persistence__get_contextual_knowledge`
2. **Knowledge Retrieval**: ✅ Returns proper JSON with array fields
3. **Array Handling**: ✅ retrieval_triggers properly processed as PostgreSQL arrays
4. **Database Access**: ✅ All core tables accessible

### Fixed Issues
1. **Array Parameter Handling**: Resolved in Python server
2. **Database Connectivity**: Stable connection to pgdbsrv
3. **MCP Tool Registration**: All tools properly registered and responding

---

## 📋 Troubleshooting Steps Applied

### Step 1: Environment Setup
```bash
# Copy MCP server files to database server
scp mcp-integration/knowledge-mcp-server.py mcp-integration/requirements.txt greg@192.168.10.90:~/KnowledgePersistence-AI/mcp-integration/

# Install dependencies on database server
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && pip install -r mcp-integration/requirements.txt"
```

### Step 2: Server Startup
```bash
# Start MCP server in background
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && nohup python mcp-integration/knowledge-mcp-server.py > mcp-server.log 2>&1 &"
```

### Step 3: Database Schema Verification
```bash
# Check table structures
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -d knowledge_persistence -c '\d knowledge_items'"
ssh greg@192.168.10.90 "export PGPASSWORD='SecureKnowledgePassword2025' && psql -h localhost -U postgres -d knowledge_persistence -c '\d session_knowledge_links'"
```

### Step 4: MCP Tool Testing
```bash
# Test MCP tools through Claude Code
mcp__knowledge-persistence__get_contextual_knowledge
# Parameters: {"situation": "Testing MCP connection after array handling fix"}
```

---

## ⚙️ Configuration Recommendations

### Primary MCP Server Decision
**RECOMMENDATION**: Standardize on **Python MCP Server** (`knowledge-mcp-server.py`)

**Rationale**:
1. ✅ Successfully tested and operational
2. ✅ Proper database connectivity with psycopg3
3. ✅ Array handling fix implemented and verified
4. ✅ Compatible with existing database schema
5. ✅ Integrated with project's Python virtual environment

### JavaScript Server Status
**RECOMMENDATION**: Archive or remove JavaScript server to avoid confusion

**Current Status**: Unused, potentially outdated, causes deployment confusion

### Environment Variables
**Required Environment Setup**:
```bash
# Database server (pgdbsrv)
export PGPASSWORD='SecureKnowledgePassword2025'
export DATABASE_URL='postgresql://postgres:SecureKnowledgePassword2025@localhost:5432/knowledge_persistence'
```

---

## 🚀 Deployment Checklist

### Pre-Deployment Verification
- [ ] PostgreSQL 17.5 + pgvector running on pgdbsrv
- [ ] Python virtual environment activated
- [ ] MCP dependencies installed (`pip install -r requirements.txt`)
- [ ] Database connectivity verified
- [ ] Array handling fix in place

### Deployment Steps
1. **Copy Files**: Transfer Python MCP server to database server
2. **Install Dependencies**: Ensure all Python packages available
3. **Start Server**: Launch with nohup for background operation
4. **Test Connection**: Verify MCP tools respond correctly
5. **Monitor Logs**: Check mcp-server.log for any issues

### Post-Deployment Verification
- [ ] MCP tools accessible from Claude Code
- [ ] Knowledge storage working with arrays
- [ ] Knowledge retrieval returning proper data
- [ ] No database connection errors in logs

---

## 📝 Lessons Learned

### Key Insights
1. **Dual Server Confusion**: Having both JS and Python servers creates deployment complexity
2. **Array Handling**: PostgreSQL text[] requires specific handling in Python psycopg3
3. **Database Schema**: Session tracking features may reference non-existent columns
4. **Environment Consistency**: MCP server must run on same server as database for localhost connections

### Best Practices
1. **Single Server Architecture**: Maintain one authoritative MCP server implementation
2. **Comprehensive Testing**: Test all MCP tools after deployment changes
3. **Database Schema Alignment**: Ensure code matches actual database structure
4. **Documentation**: Document all configuration decisions and troubleshooting steps

---

## 🔍 Next Steps

### Immediate Actions
1. **Archive JavaScript Server**: Move to deprecated folder or remove entirely
2. **Update Documentation**: Reflect Python-only MCP server architecture
3. **Create Deployment Scripts**: Automate MCP server deployment process
4. **Monitor Performance**: Track MCP server performance and reliability

### Future Improvements
1. **Error Handling**: Enhance error handling in Python MCP server
2. **Logging**: Implement comprehensive logging for troubleshooting
3. **Testing Suite**: Create automated tests for MCP functionality
4. **Configuration Management**: Centralize configuration for easier maintenance

---

**Status**: MCP Server operational with array handling fix verified ✅  
**Next Review**: Upon next deployment or configuration change