# KnowledgePersistence-AI MCP Integration

**Model Context Protocol server for AI knowledge persistence**

This directory contains the MCP server implementation that enables seamless AI knowledge storage and retrieval through Claude Code.

## 🚀 Quick Start

### 1. Installation
```bash
cd /home/greg/KnowledgePersistence-AI/mcp-integration
npm install
```

### 2. Configuration
Copy the environment template:
```bash
cp .env.example .env
# Edit .env to add your OpenAI API key if you want semantic search
```

### 3. Test the Server
```bash
npm test
# Or for database connectivity test only:
node test/simple-test.js
```

### 4. Claude Code Integration
Add to your Claude Code MCP configuration (`~/.claude/mcp_servers.json`):
```json
{
  "mcpServers": {
    "knowledge-persistence": {
      "command": "node",
      "args": ["/home/greg/KnowledgePersistence-AI/mcp-integration/server/knowledge-server.js"],
      "env": {
        "DATABASE_URL": "postgresql://postgres:SecureKnowledgePassword2025@192.168.10.90:5432/knowledge_persistence"
      }
    }
  }
}
```

## 🧰 Available Tools

### Session Management
- **`start_session`** - Initialize new AI session with project context
- **`end_session`** - Close session and capture insights

### Knowledge Operations
- **`get_contextual_knowledge`** - Retrieve relevant knowledge for current situation
- **`search_similar_knowledge`** - Semantic search across knowledge base
- **`store_knowledge`** - Store new knowledge items
- **`store_technical_discovery`** - Save technical gotchas and solutions

### Technical Support
- **`get_technical_gotchas`** - Find solutions for similar technical problems

## 📊 Current Status

### ✅ Completed Features
- **MCP Server Implementation** - Full Node.js MCP server with database connectivity
- **Core Knowledge Tools** - All 6 primary knowledge operations implemented
- **Database Integration** - PostgreSQL + pgvector connection tested and working
- **Session Management** - Basic session lifecycle tracking
- **Technical Discoveries** - Storage and retrieval of problem-solution patterns

### 🔄 In Progress
- **Semantic Search** - OpenAI embeddings integration (requires API key)
- **Advanced Session Features** - Automatic knowledge injection
- **Real-time Updates** - Supabase subscriptions for live knowledge updates

### 🎯 Next Steps
- Add OpenAI API key for semantic search capabilities
- Test full integration with Claude Code
- Implement automatic knowledge capture during sessions
- Add NavyCMMS bridge server for project-specific integration

## 🏗️ Architecture

```
mcp-integration/
├── server/
│   └── knowledge-server.js       # Main MCP server
├── test/
│   ├── simple-test.js            # Database connectivity test
│   └── test-server.js            # Full MCP server test
├── package.json                  # Node.js dependencies
├── .env                          # Environment configuration
└── claude-mcp-config.json        # Claude Code MCP configuration
```

## 💾 Database Schema

The server connects to the KnowledgePersistence-AI database with these tables:
- **`knowledge_items`** - Multi-modal knowledge storage with vector embeddings
- **`ai_sessions`** - Session tracking and lifecycle management
- **`session_knowledge_links`** - Knowledge interaction tracking
- **`technical_gotchas`** - Problem-solution mapping

## 🔧 Development

### Running in Development Mode
```bash
npm run dev  # Uses --watch flag for auto-restart
```

### Manual Testing
```bash
# Start server
node server/knowledge-server.js

# Send MCP request (in another terminal)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node server/knowledge-server.js
```

## 🔐 Security Notes

- Database credentials are configured for local development
- OpenAI API key should be added to `.env` for production use
- MCP server runs with local file system access

## 🌟 Revolutionary Impact

This MCP server enables:
- **Knowledge Accumulation** - AI builds expertise across unlimited sessions
- **Contextual Intelligence** - Automatic retrieval of relevant past knowledge
- **Technical Memory** - Permanent storage of hard-learned lessons
- **Strategic Partnership** - AI transforms from tool to irreplaceable partner

**Status**: Phase 3 MCP Integration Complete - Ready for Claude Code integration and knowledge persistence testing.