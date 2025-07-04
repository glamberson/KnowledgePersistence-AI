# Documentation Hierarchy for KnowledgePersistence-AI
**Date**: 2025-07-04  
**Purpose**: Define authoritative documentation sources and hierarchy  
**Priority Order**: Repository files → MCP/CAG database → GitHub issues  

---

## 📚 PRIMARY DOCUMENTATION SOURCES

### **1. Repository Documentation (AUTHORITATIVE)**
Primary source of truth for all project documentation:

#### **Core Architecture**
- `docs/COMPLETE_SYSTEM_ARCHITECTURE.md` - System overview
- `CAG_ARCHITECTURE_DESIGN.md` - CAG implementation details  
- `DEPLOYMENT_COMPLETE.md` - Infrastructure deployment
- `SECURITY_IMPROVEMENTS_SUMMARY.md` - Security implementation

#### **Implementation Guides**
- `mcp-integration/MCP_FRAMEWORK_DESIGN.md` - MCP framework design
- `database/POSTGRESQL_PGVECTOR_ARCHITECTURE.md` - Database design
- `testing/COMPREHENSIVE_TESTING_PLAN.md` - Testing procedures
- `server-config/DATABASE_SERVER_REQUIREMENTS.md` - Server setup

#### **Session Documentation**
- `SESSION_HANDOFF_*.md` - Session transition documentation
- `docs/SESSION_FRAMEWORK_IMPLEMENTATION.md` - Session management

### **2. MCP/CAG Knowledge Database (DYNAMIC)**
Living knowledge base with 429+ items across knowledge types:

#### **Query Methods**
```bash
# Use secure tools to query knowledge base
./secure_ssh_simple.sh count        # Knowledge items count
./secure_ssh_simple.sh test-cag     # CAG functionality test

# Database queries via MCP framework
ssh pgdbsrv "cd KnowledgePersistence-AI && source venv/bin/activate && python3 -c \"
from cag_mcp_integrated import CAGEngineMCP
import asyncio
async def query():
    engine = CAGEngineMCP()
    result = await engine.mcp_client.search_knowledge('documentation', limit=10)
    for item in result:
        print(f'{item[\"knowledge_type\"]}: {item[\"title\"]}')
asyncio.run(query())
\""
```

### **3. GitHub Issues (PROJECT MANAGEMENT)**
Active project tracking and status:

#### **Current Priority Issues**
- Check via: `gh issue list --state open --label enhancement`
- Status tracking: `gh issue list --milestone current`
- Implementation progress: `gh issue view <issue-number>`

---

## 🚫 NON-AUTHORITATIVE SOURCES

### **CLAUDE.md - AI Assistant Instructions Only**
- ⚠️ **WARNING**: Not authoritative documentation
- **Purpose**: AI assistant instructions and quick reference only  
- **Problems**: Can become outdated, bloated, AI-specific
- **Usage**: Quick reference for AI tools only, not project documentation

### **Deprecated/Legacy Files**
- Files in `deprecated/` directory
- Old session handoffs (>30 days)
- Temporary implementation files

---

## 📋 DOCUMENTATION ACCESS PROTOCOLS

### **For Project Information**
1. **First**: Check repository documentation files
2. **Second**: Query MCP/CAG knowledge database for dynamic information
3. **Third**: Review GitHub issues for current status
4. **Never**: Rely solely on CLAUDE.md for project decisions

### **For Implementation Details**
1. **Architecture**: `CAG_ARCHITECTURE_DESIGN.md` and related docs
2. **Database**: Query knowledge base via CAG/MCP tools
3. **Security**: `SECURITY_IMPROVEMENTS_SUMMARY.md`
4. **Deployment**: `DEPLOYMENT_COMPLETE.md`

### **For Current Status**
1. **GitHub Issues**: `gh issue list` for current priorities
2. **Session Handoffs**: Latest `SESSION_HANDOFF_*.md` file
3. **Knowledge Base**: Live query via `./secure_ssh_simple.sh count`

---

## 🔄 PORTABLE WORKFLOWS

### **Multi-User Compatibility**
All documentation designed for:
- ✅ Multiple AI assistants (Claude, GPT, Gemini, local models)
- ✅ Multiple users with different access levels
- ✅ Different development environments and tools
- ✅ Project handoffs and team transitions

### **Tool-Agnostic Access**
- **Database Access**: Standard PostgreSQL + Python
- **SSH Access**: Standard SSH with key authentication
- **Documentation**: Standard Markdown in repository
- **APIs**: RESTful endpoints with standard HTTP

### **Framework Independence**
- **MCP Integration**: Optional, with fallback methods
- **CAG Framework**: Modular design with direct DB access option
- **Scripts**: Standard bash/Python with minimal dependencies

---

## 📊 DOCUMENTATION MAINTENANCE

### **Update Protocols**
1. **Repository Documentation**: Update immediately when implementation changes
2. **Knowledge Base**: Automatic updates via CAG framework
3. **GitHub Issues**: Update status as work progresses
4. **Session Handoffs**: Create new file each session

### **Version Control**
- All documentation in git repository
- Session handoffs timestamped and preserved
- Knowledge base has full audit trail
- GitHub issues provide change history

### **Quality Assurance**
- Documentation must be tool-agnostic
- No hardcoded credentials or paths
- Clear separation of concerns
- Regular validation against actual implementation

---

## 🎯 IMPLEMENTATION GUIDELINES

### **For AI Assistants**
1. Reference repository documentation first
2. Query knowledge base for dynamic information
3. Check GitHub issues for current priorities
4. Do not treat CLAUDE.md as authoritative
5. Store new knowledge in MCP/CAG database

### **For Human Users**
1. Repository documentation provides complete picture
2. Knowledge base contains implementation experience
3. GitHub issues track current work
4. Session handoffs provide context for AI interactions

### **For Project Handoffs**
1. Repository contains all static documentation
2. Database export provides complete knowledge
3. GitHub issues show project status
4. No dependency on AI-specific instructions

**Result**: Clear documentation hierarchy ensuring project knowledge remains accessible and authoritative regardless of AI tool, user, or development environment.