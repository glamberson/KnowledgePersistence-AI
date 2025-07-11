# CLAUDE.md

**Last Updated**: 2025-07-03  
**Purpose**: Comprehensive guidance for Claude Code AI assistant when working with KnowledgePersistence-AI project  
**Context**: Revolutionary AI knowledge persistence system with PATTERN RECOGNITION breakthrough  

---

## 🎯 EXECUTIVE SUMMARY

**Project**: KnowledgePersistence-AI - Revolutionary AI knowledge persistence database system  
**Purpose**: Transform AI from replaceable tool to irreplaceable strategic partner through persistent knowledge accumulation  
**Status**: Phase 4 COMPLETE - Multi-Provider AI Integration with Cost Optimization  

**Revolutionary Achievement**: First operational AI knowledge persistence database with predictive intelligence PLUS multi-provider AI routing system for cost-optimized strategic partnership development.

---

This file provides comprehensive guidance to Claude Code (claude.ai/code) when working with the KnowledgePersistence-AI project.

## Project Overview

This is the **KnowledgePersistence-AI** project - a revolutionary database infrastructure for AI knowledge persistence that enables continuous expertise accumulation across unlimited sessions.

### Key Distinction
- **This project**: AI knowledge persistence system implementation
- **Test Source**: NavyCMMS project serves as real-world testing source
- **Independence**: Completely separate from NavyCMMS, with own repository and infrastructure

## Session Startup Requirements

### Repository Access Verification
**CRITICAL**: At the start of each new session, verify access to project infrastructure:

#### **Linux (Debian 12)**
```bash
# Verify KnowledgePersistence-AI repository (current working directory)
pwd  # Should be: /home/greg/KnowledgePersistence-AI
ls -la

# Verify database server access (pgdbsrv)
ssh greg@192.168.10.90 "whoami && hostname"

# Check database status
ssh greg@192.168.10.90 "sudo systemctl status postgresql | head -5"

# Verify API server status
curl -s http://192.168.10.90:8090/health

# Check project status
git status
ls -la
```

**Session Startup Checklist:**
1. Verify working directory: `/home/greg/KnowledgePersistence-AI`
2. Confirm database server access: pgdbsrv (192.168.10.90)
3. Check PostgreSQL 17.5 + pgvector status
4. Verify Python API server operational
5. **CRITICAL**: Test Claude Code Router (CCR) functionality
6. **NEW**: Verify multi-provider AI access (OpenAI, Anthropic, Local Ollama)
7. **NEW**: Test MCP pattern recognition server functionality
8. **NEW**: Load session context with pattern predictions
9. Read latest session handoff documentation
10. Review current phase and next steps

**Claude Code Router (CCR) Startup Commands:**
```bash
# CRITICAL: Test CCR service status
ccr status

# Start CCR if not running
nohup ccr start > /tmp/ccr.log 2>&1 &

# Test multi-provider functionality
echo "Test local model" | timeout 10 ccr code
curl -s http://127.0.0.1:3456/health

# Verify providers are registered
grep "provider registered" /tmp/ccr.log
```

**Pattern Recognition Startup Commands:**
```bash
# Test MCP server with pattern recognition
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && timeout 10s python3 knowledge-mcp-server.py"

# Test pattern recognition prototype
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python3 pattern_recognition_prototype.py"
```

### **Important Notes on Infrastructure**
- **Database Server**: pgdbsrv (192.168.10.90) - Debian 12, PostgreSQL 17.5 + pgvector
- **API Server**: Python 3.11 with psycopg3 (NOT psycopg2)
- **Claude Code Router**: Multi-provider AI routing on port 3456 (OpenAI, Anthropic, Local Ollama)
- **Local AI Model**: qwen2.5:0.5b via Ollama (FREE cost optimization)
- **MCP Server**: Enhanced with pattern recognition capabilities (47-64% accuracy)
- **Database**: knowledge_persistence with 4 core tables + 115+ knowledge items
- **Credentials**: postgres / SecureKnowledgePassword2025
- **Pattern Recognition**: Operational with learning cycle discovery and predictive intelligence
- **Cost Optimization**: Local model reducing API costs from $100/day target to <$10/day

### Working with Database Server
```bash
# SSH access to database server
ssh greg@192.168.10.90

# Database operations
sudo -u postgres psql -d knowledge_persistence -c "SELECT COUNT(*) FROM knowledge_items;"

# API server management
cd KnowledgePersistence-AI
source venv/bin/activate
# Check if API running: curl http://localhost:8090/health
```

## Git Configuration and Attribution

### AI User Configuration
**AI User Account**: `lamco-office` (automated operations)  
**Human Project Manager**: `glamberson@lamco.io`  

#### Git Configuration Commands
```bash
# Configure AI user for automated commits
git config user.name "Lamco Development Office Staff"
git config user.email "lamco-office@users.noreply.github.com"

# When acting on behalf of human during session (with explicit approval)
git config user.name "Greg Lamberson"
git config user.email "glamberson@lamco.io"
```

#### Commit Message Attribution
```bash
# AI automated commits
git commit -m "feat: Implement MCP knowledge server integration

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Human-approved commits during AI session  
git commit -m "docs: Update deployment documentation

Approved by PM during AI session.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Essential Commands

### Database Server Operations

**Secure Knowledge Access (SSH Key + MCP-First)**:
```bash
# SECURE: Use SSH config alias (no password exposure)
ssh pgdbsrv

# SECURE TOOLS: All operations via secure authentication
./secure_ssh_simple.sh status    # System status (DB, API, Docker)
./secure_ssh_simple.sh count     # Knowledge items count (429 items)
./secure_ssh_simple.sh test-cag  # CAG performance test
./secure_ssh_simple.sh shell     # Interactive SSH shell

# SECURE SYNC: File synchronization with SSH keys
./sync_to_server.sh              # Sync all files securely

# PREFERRED: MCP knowledge access via CAG framework
ssh pgdbsrv "cd KnowledgePersistence-AI && source venv/bin/activate && python3 -c \"
from cag_mcp_integrated import CAGEngineMCP
import asyncio
async def test_mcp():
    engine = CAGEngineMCP()
    result = await engine.mcp_client.get_contextual_knowledge('session status', 10)
    print(f'MCP retrieved {len(result)} knowledge items')
    return result
asyncio.run(test_mcp())
\""

# PASSWORDLESS SUDO: Specific operations without password
ssh pgdbsrv "sudo systemctl status postgresql"    # ✅ No password required
ssh pgdbsrv "sudo docker ps"                      # ✅ No password required

# LEGACY: Direct database access (only when MCP unavailable)
ssh pgdbsrv "sudo -u postgres psql -d knowledge_persistence"
```

### Development Environment

**Python Virtual Environment**:
```bash
# Activate environment (on pgdbsrv)
cd /home/greg/KnowledgePersistence-AI
source venv/bin/activate

# Install dependencies (if needed)
pip install psycopg[binary]

# Run API server
python test_api.py
```

**Docker Operations** (on pgdbsrv):
```bash
# Check running containers
docker ps

# Start/stop services
docker compose up -d
docker compose down

# View logs
docker logs <container_name>
```

### GitHub Operations

```bash
# Repository status
git status
git log --oneline -5

# Branch operations
git branch
git checkout develop  # if needed

# Commit and push
git add .
git commit -m "descriptive message"
git push origin main
```

### Claude Code Router Operations

**Multi-Provider AI Access**:
```bash
# Interactive coding with intelligent routing
ccr code

# Check service status
ccr status

# Test specific providers
curl -X POST http://127.0.0.1:3456/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: [provider-key]" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}]}'

# Monitor real-time usage
tail -f /tmp/ccr.log
```

**Cost-Optimized Routing**:
```bash
# Default tasks → OpenAI gpt-4o-mini (cost optimized)
ccr code "Write a Python function"

# Background tasks → Local Ollama (FREE)
# Complex reasoning → Anthropic Claude (premium quality)  
# Long context → Google Gemini (when needed)

# Model switching within session
/model openai,gpt-4o-mini
/model ollama,qwen2.5:0.5b  
/model anthropic-direct,claude-3-5-sonnet-20241022
```

## Project Architecture

### Directory Structure
```
KnowledgePersistence-AI/
├── docs/                     # Project documentation
├── database/                 # Database schema and architecture
├── mcp-integration/          # MCP framework design
├── knowledge-capture/        # Knowledge capture system templates
├── server-config/           # Database server requirements
├── testing/                 # Testing and validation
├── supabase-deployment/     # API deployment configurations
├── venv/                    # Python virtual environment (on server)
├── deploy_schema.sql        # Database schema deployment
├── test_api.py             # Python REST API server
└── DEPLOYMENT_COMPLETE.md   # Comprehensive deployment guide
```

### Critical Files for Sessions
1. **DEPLOYMENT_COMPLETE.md** - Complete installation and configuration guide
2. **CCR_COMPREHENSIVE_DOCUMENTATION.md** - Complete Claude Code Router integration guide
3. **CCR_RECOVERY_PLAN.md** - CCR troubleshooting and recovery procedures
4. **CCR_API_PROVIDER_TEST_RESULTS.md** - Multi-provider API test results
5. **Latest Session Handoff** - Session-specific knowledge and insights
6. **database/POSTGRESQL_PGVECTOR_ARCHITECTURE.md** - Database design
7. **mcp-integration/MCP_FRAMEWORK_DESIGN.md** - Claude Code integration design

## Development Workflow

### Current Phase Status
- **Phase 1** ✅: Database Infrastructure (PostgreSQL 17.5 + pgvector)
- **Phase 2** ✅: REST API Development (Python + psycopg3)
- **Phase 3** ✅: MCP Integration with Pattern Recognition (64% accuracy)
- **Phase 4** ✅: Multi-Provider AI Integration with Cost Optimization
- **Phase 5** 🎯: Advanced Integration and NavyCMMS Testing

### Issue Management Pattern
- **Infrastructure issues**: Database, server, deployment
- **Development issues**: API, MCP integration, testing
- **Documentation issues**: Guides, architecture, handoffs

## Technology Stack

### Core Technologies
- **Database**: PostgreSQL 17.5 with pgvector 0.8.0 extension
- **Vector Search**: pgvector for semantic similarity search
- **Python**: 3.11 with modern psycopg3 (NOT psycopg2)
- **API**: Custom REST API with JSON responses
- **Containers**: Docker 28.3.0 with Docker Compose
- **Server**: Debian 12 on Proxmox VM

### Database Schema
```sql
-- Core tables deployed:
knowledge_items         -- Multi-modal knowledge storage with vector embeddings
ai_sessions            -- Session tracking and lifecycle management
session_knowledge_links -- Knowledge interaction tracking
technical_gotchas      -- Problem-solution mapping and discoveries
```

### Key Capabilities
- **Multi-Modal Storage**: 6 knowledge types (factual, procedural, contextual, relational, experiential, technical_discovery)
- **Vector Similarity**: VECTOR(1536) fields with cosine similarity search
- **Session Continuity**: Complete AI session tracking and knowledge linking
- **Real-time API**: REST endpoints for knowledge retrieval and storage

## Network and Infrastructure

### Server Configuration
- **Database Server**: pgdbsrv (192.168.10.90)
- **Development Server**: aibox (192.168.10.88)
- **Network**: 192.168.10.x subnet with full connectivity
- **Access**: SSH key-based authentication

### Service Endpoints
- **PostgreSQL**: localhost:5432 (on pgdbsrv)
- **API Server**: 192.168.10.90:8090
- **Health Check**: http://192.168.10.90:8090/health
- **Knowledge Data**: http://192.168.10.90:8090/knowledge_items

### Credentials and Access
- **Database User**: postgres / SecureKnowledgePassword2025
- **SSH Access**: greg@192.168.10.90 (password: Bibi4189)
- **GitHub**: lamco-admin organization

## Revolutionary Capabilities

### ✅ BREAKTHROUGH ACHIEVED: Pattern Recognition Integration
**First operational AI knowledge persistence database with predictive intelligence** featuring:
- Multi-modal knowledge storage across 6 knowledge types
- Vector similarity search for semantic knowledge retrieval  
- **REVOLUTIONARY**: Pattern recognition with 47-64% context prediction accuracy
- **MCP Integration COMPLETE**: Claude Code has direct access to predictive knowledge tools
- Session tracking and knowledge interaction recording
- Real-time API access with modern database connectivity

### 🚀 NEW PATTERN RECOGNITION CAPABILITIES (Phase 3 COMPLETE)
- **discover_knowledge_patterns**: Advanced analysis of learning cycles, temporal patterns, knowledge clustering
- **predict_knowledge_needs**: Context-based knowledge predictions with confidence scoring
- **Proactive Session Startup**: Automatic relevant knowledge loading based on project context
- **Learning Acceleration**: Pattern-guided problem-solving and breakthrough prediction

### Strategic Partnership Achievement
- **Session Continuity**: Operational knowledge retention across unlimited sessions
- **Predictive Intelligence**: Context-aware knowledge suggestions before you ask
- **Strategic Partnership**: AI becomes irreplaceable through accumulated expertise and pattern intelligence

## Session Handoff Process

### Session End Protocol
1. **Complete Session Storage**: Store ENTIRE chat conversation history in database
2. **Document Current Status**: Update session handoff with progress and insights
3. **Commit Changes**: Ensure all work is committed to repository
4. **Server Status**: Document database and API server status
5. **Next Steps**: Clear guidance for session continuation
6. **Knowledge Capture**: Preserve insights and discoveries

### Session Start Protocol  
1. **Load Complete Previous Session**: Access full conversation history from database
2. **Verify Session Continuity**: Confirm which previous session to continue from
3. **Read Handoff Documentation**: Latest session insights and status
4. **Verify Infrastructure**: Database server, API, and repository access
5. **Check Current Phase**: Understand implementation status
6. **Review Next Steps**: Clear continuation path from previous session

### CRITICAL REQUIREMENT: Complete Session Storage
**MANDATORY**: Every session must store complete chat history including:
- Every user prompt (exact text)
- Every AI response (complete responses with reasoning)
- Every redirection/correction (with classification)
- Tool usage and decision reasoning
- Context evolution throughout conversation

**Database Storage**: Use `complete_session_storage.py` for full conversation capture
**Retrieval**: Next session must load complete previous conversation for analysis

### USER TASK: Historical Chat Data Investigation
**ASSIGNED**: 2025-07-04 - User to investigate accessing historical Claude conversations
**PURPOSE**: Retroactive analysis of conversation patterns across multiple projects
**METHODS TO INVESTIGATE**:
- Claude.ai export functionality
- Anthropic API conversation history access
- Manual extraction of critical conversations
**IMPACT**: Massive expansion of analysis dataset and pattern recognition capabilities
**INTEGRATION**: Historical data to be imported into complete_session_storage.py system

## Development Standards

### Code Quality
- **Modern Dependencies**: Use psycopg3 (not psycopg2)
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Inline comments and comprehensive guides
- **Testing**: Operational validation and endpoint testing

### Database Standards
- **UUID Primary Keys**: Federation-ready unique identifiers
- **Vector Embeddings**: Consistent VECTOR(1536) for OpenAI embeddings
- **JSONB Metadata**: Flexible context data storage
- **Performance Indexes**: Optimized for similarity search

### Security Standards
- **Password Protection**: Secure credential management
- **Network Security**: Subnet-based access control
- **API Security**: CORS and error handling
- **Database Security**: Role-based access control

## Revolutionary Vision

**Goal**: Transform AI from replaceable tool to irreplaceable strategic partner through persistent knowledge accumulation.

**Current State**: Operational foundation for knowledge persistence  
**Next Phase**: MCP integration for seamless Claude Code knowledge access  
**Ultimate Vision**: AI that accumulates expertise and builds relationships continuously across unlimited sessions  

**Impact**: Revolutionary improvement in AI project management capability and strategic partnership development.

---

**Remember**: This project represents a fundamental breakthrough in AI capability enhancement. We're building the infrastructure that will enable AI to become a true strategic partner through continuous knowledge accumulation rather than session-by-session rebuilding.

**The foundation for transforming AI strategic partnership is operational and ready for MCP integration.**