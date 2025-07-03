# CLAUDE.md

**Last Updated**: 2025-07-02  
**Purpose**: Comprehensive guidance for Claude Code AI assistant when working with KnowledgePersistence-AI project  
**Context**: Revolutionary AI knowledge persistence system development and deployment  

---

## 🎯 EXECUTIVE SUMMARY

**Project**: KnowledgePersistence-AI - Revolutionary AI knowledge persistence database system  
**Purpose**: Transform AI from replaceable tool to irreplaceable strategic partner through persistent knowledge accumulation  
**Status**: Phase 1-2 Complete (Database + API), Phase 3 Ready (MCP Integration)  

**Key Achievement**: First operational AI knowledge persistence database capable of accumulating expertise across unlimited sessions.

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
5. Read latest session handoff documentation
6. Review current phase and next steps

### **Important Notes on Infrastructure**
- **Database Server**: pgdbsrv (192.168.10.90) - Debian 12, PostgreSQL 17.5 + pgvector
- **API Server**: Python 3.11 with psycopg3 (NOT psycopg2)
- **Database**: knowledge_persistence with 4 core tables
- **Credentials**: postgres / SecureKnowledgePassword2025

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

**SSH Access and Basic Operations**:
```bash
# Connect to database server
ssh greg@192.168.10.90

# Check PostgreSQL status
sudo systemctl status postgresql

# Access database
sudo -u postgres psql -d knowledge_persistence

# API server status
curl http://192.168.10.90:8090/health
curl http://192.168.10.90:8090/knowledge_items
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
2. **Latest Session Handoff** - Session-specific knowledge and insights
3. **database/POSTGRESQL_PGVECTOR_ARCHITECTURE.md** - Database design
4. **mcp-integration/MCP_FRAMEWORK_DESIGN.md** - Claude Code integration design

## Development Workflow

### Current Phase Status
- **Phase 1** ✅: Database Infrastructure (PostgreSQL 17.5 + pgvector)
- **Phase 2** ✅: REST API Development (Python + psycopg3)
- **Phase 3** 🔄: MCP Integration (Next phase)
- **Phase 4** 🎯: NavyCMMS Testing and Validation

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

### Current Achievement
**First operational AI knowledge persistence database** with:
- Multi-modal knowledge storage across 6 knowledge types
- Vector similarity search for semantic knowledge retrieval
- Session tracking and knowledge interaction recording
- Real-time API access with modern database connectivity

### Target Capabilities (Phase 3-4)
- **MCP Integration**: Seamless Claude Code knowledge access
- **Automatic Capture**: Background knowledge storage during sessions
- **Session Continuity**: 90%+ knowledge retention across sessions
- **Strategic Partnership**: AI becomes irreplaceable through accumulated expertise

## Session Handoff Process

### Session End Protocol
1. **Document Current Status**: Update session handoff with progress and insights
2. **Commit Changes**: Ensure all work is committed to repository
3. **Server Status**: Document database and API server status
4. **Next Steps**: Clear guidance for session continuation
5. **Knowledge Capture**: Preserve insights and discoveries

### Session Start Protocol  
1. **Read Handoff Documentation**: Latest session insights and status
2. **Verify Infrastructure**: Database server, API, and repository access
3. **Check Current Phase**: Understand implementation status
4. **Review Next Steps**: Clear continuation path from previous session

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