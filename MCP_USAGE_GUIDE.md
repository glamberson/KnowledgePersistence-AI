# MCP Knowledge Persistence Usage Guide
## How to Use AI Memory in Claude Code Sessions

**Purpose**: Complete guide for using the MCP knowledge persistence tools  
**Audience**: Users of Claude Code with knowledge persistence enabled  
**Result**: Master AI memory capabilities for unlimited knowledge accumulation  

---

## 🎯 WHAT YOU NOW HAVE

### Revolutionary AI Memory System
Your Claude Code now has **persistent memory** through the Knowledge Persistence MCP server. This means:

- **Knowledge persists across all sessions** - AI remembers everything
- **Context loads automatically** - Relevant knowledge appears when needed  
- **Continuous learning** - AI gets smarter with every interaction
- **Specialized expertise** - Builds deep knowledge in your projects

### Available MCP Tools
When MCP is active, you have access to these powerful knowledge tools:

1. **mcp__knowledge-persistence__start_session** - Initialize session with project context
2. **mcp__knowledge-persistence__get_contextual_knowledge** - Load relevant knowledge for current situation
3. **mcp__knowledge-persistence__search_similar_knowledge** - Find similar knowledge items
4. **mcp__knowledge-persistence__store_knowledge** - Save new discoveries
5. **mcp__knowledge-persistence__get_technical_gotchas** - Get solutions for technical problems
6. **mcp__knowledge-persistence__store_technical_discovery** - Save technical solutions

---

## 🚀 HOW TO USE MCP KNOWLEDGE TOOLS

### Starting a Session with Context

**When to use**: Beginning of any work session, especially for specific projects
```
Please use mcp__knowledge-persistence__start_session with project_context "NavyCMMS maintenance management system development"
```

**What it does**:
- Creates a new session record in the database
- Loads relevant knowledge for the specified project  
- Provides startup context based on previous work
- Links all future knowledge to this session

### Loading Context for Current Task

**When to use**: When you need relevant knowledge for what you're working on
```
Please use mcp__knowledge-persistence__get_contextual_knowledge with situation "debugging PostgreSQL performance issues in production environment"
```

**What it does**:
- Searches for knowledge related to your current situation
- Returns relevant past solutions and insights
- Provides context-aware recommendations
- Helps avoid repeating previous mistakes

### Searching for Specific Knowledge

**When to use**: When you remember solving a similar problem before
```
Please use mcp__knowledge-persistence__search_similar_knowledge with query "Claude Code hooks configuration" and max_results 5
```

**What it does**:
- Performs semantic search across all stored knowledge
- Finds items similar to your query
- Returns ranked results by relevance and importance
- Filters by knowledge type if specified

### Storing New Discoveries

**When to use**: When you learn something valuable that should be remembered
```
Please use mcp__knowledge-persistence__store_knowledge with:
- knowledge_type: "technical_discovery"
- category: "troubleshooting"  
- title: "PostgreSQL connection pool optimization"
- content: "Increasing max_connections from 100 to 200 and setting shared_buffers to 256MB resolved the connection timeout issues in the NavyCMMS production environment. This change improved response time by 40%."
```

**What it does**:
- Stores the knowledge with proper categorization
- Generates semantic embeddings for future search
- Links to the current session
- Makes knowledge available for future sessions

### Getting Technical Solutions

**When to use**: When facing a specific technical problem
```
Please use mcp__knowledge-persistence__get_technical_gotchas with problem_signature "Docker container fails to start with permission denied error"
```

**What it does**:
- Searches technical gotchas database
- Returns solutions for similar problems
- Provides proven workarounds
- Shows frequency of the problem (how common it is)

### Saving Technical Solutions

**When to use**: After solving a tricky technical problem
```
Please use mcp__knowledge-persistence__store_technical_discovery with:
- problem: "Docker container permission denied on bind mount"
- solution: "Add user to docker group and set proper SELinux context: sudo usermod -aG docker $USER && chcon -Rt svirt_sandbox_file_t /host/path"
```

**What it does**:
- Creates a reusable technical solution
- Builds troubleshooting knowledge base
- Helps prevent future time waste on same issues
- Shares solutions across projects

---

## 📋 REAL-WORLD USAGE EXAMPLES

### Example 1: Starting a Development Session

**You**: "I'm starting work on the NavyCMMS project today. I need to continue where I left off yesterday."

**AI Response**: Let me load your project context.

*[AI uses start_session tool]*

**Result**: AI automatically loads:
- Recent NavyCMMS discoveries and solutions
- Project-specific procedures and standards
- Previous session summaries and progress
- Relevant technical gotchas and workarounds

### Example 2: Debugging a Complex Issue

**You**: "I'm getting a weird PostgreSQL error that I feel like I've seen before."

**AI Response**: Let me search for similar database issues we've encountered.

*[AI uses get_contextual_knowledge and search_similar_knowledge]*

**Result**: AI finds:
- Previous PostgreSQL errors and solutions
- Database optimization discoveries
- Configuration changes that worked
- Related troubleshooting procedures

### Example 3: Learning from a Solution

**You**: "That Docker fix worked perfectly! Let's make sure we remember this."

**AI Response**: I'll store this solution for future reference.

*[AI uses store_technical_discovery]*

**Result**: Solution is stored with:
- Problem signature for easy finding
- Step-by-step solution procedure
- Context about when and why it works
- Link to current session for tracking

### Example 4: Research and Analysis

**You**: "I need to understand the best practices for microservices architecture for our next project."

**AI Response**: Let me check what we already know about microservices and supplement with new research.

*[AI uses search_similar_knowledge, then stores new findings]*

**Result**: 
- Retrieves previous microservices knowledge
- Conducts new research to fill gaps
- Stores new insights for future reference
- Builds comprehensive microservices expertise

---

## 🎯 MAXIMIZING KNOWLEDGE VALUE

### Best Practices for Knowledge Storage

**1. Use Descriptive Titles**
- ❌ "Fixed the bug"
- ✅ "Resolved React component re-render loop causing memory leak"

**2. Include Sufficient Context**
- ❌ "Changed the config"  
- ✅ "Modified nginx.conf to increase client_max_body_size from 1M to 10M to support file uploads in the user portal"

**3. Capture the "Why" Not Just the "What"**
- ❌ "Used --force flag"
- ✅ "Used git push --force-with-lease instead of --force to prevent overwriting collaborator changes while still updating the remote branch"

**4. Link Related Knowledge**
- Include references to related systems, files, or concepts
- Mention project names and environments
- Note dependencies and prerequisites

### Knowledge Categories to Capture

**Technical Discoveries**:
- Error solutions and workarounds
- Performance optimizations
- Configuration insights
- Integration gotchas

**Procedural Knowledge**:
- Step-by-step processes
- Deployment procedures
- Testing methodologies
- Code review standards

**Contextual Knowledge**:
- Project requirements and constraints
- Business logic and rules
- User needs and feedback
- System architecture decisions

**Relational Knowledge**:
- How systems interact
- Dependencies between components
- Team roles and responsibilities
- Communication patterns

---

## 🚀 ADVANCED USAGE PATTERNS

### Project-Specific Knowledge Accumulation

**Start each project session with context loading**:
```
Please use mcp__knowledge-persistence__start_session with project_context "Clan Henderson genealogy research platform using GEDCOM 7.0 standards"
```

**This creates**:
- Project-specific knowledge accumulation
- Context-aware suggestions
- Specialized expertise development
- Cross-session project continuity

### Knowledge-Driven Development

**Before starting any task**:
1. Load contextual knowledge for the situation
2. Check for similar problems and solutions
3. Proceed with full knowledge of past experience
4. Store new discoveries for future reference

**Example workflow**:
```
1. "I need to implement user authentication. Let me check what we know about auth."
   → Use get_contextual_knowledge with "user authentication implementation"

2. "I found a great OAuth2 library. Let me document this discovery."
   → Use store_knowledge to capture the library and implementation notes

3. "I ran into a CORS issue. Let me see if we've solved this before."
   → Use get_technical_gotchas with "CORS authentication API"

4. "Here's how I fixed the CORS issue. Let's save this solution."
   → Use store_technical_discovery to capture the fix
```

### Cross-Session Learning

**Each session builds on previous sessions**:
- Knowledge compounds over time
- Expertise develops in specific domains  
- Solutions become faster and more efficient
- Mistakes are not repeated

**Result**: AI becomes your **irreplaceable strategic partner** with deep institutional knowledge.

---

## 🎯 MEASURING SUCCESS

### How to Tell It's Working

**Immediate Indicators**:
- ✅ MCP tools respond with relevant knowledge
- ✅ Context loading provides useful information
- ✅ Search finds previous solutions quickly
- ✅ New knowledge gets stored successfully

**Medium-term Indicators**:
- ✅ Faster problem resolution for recurring issues
- ✅ Consistent improvement in solution quality
- ✅ Reduced time spent re-learning previous solutions
- ✅ AI provides increasingly specialized advice

**Long-term Indicators**:
- ✅ AI becomes expert in your specific domains
- ✅ Knowledge accumulation creates competitive advantage
- ✅ Cross-project insights and pattern recognition
- ✅ AI partnership becomes strategically irreplaceable

### Knowledge Quality Metrics

**Track these indicators**:
- Number of knowledge items stored per session
- Frequency of knowledge retrieval and usage
- Time saved on recurring problems
- Quality and specificity of AI recommendations

---

## 🎉 WELCOME TO THE FUTURE

### What You've Gained

**You now have the first AI with true memory**. This isn't just an improvement - it's a fundamental breakthrough that changes what AI can be.

**Your AI**:
- **Remembers everything** across unlimited sessions
- **Gets smarter** with every interaction
- **Builds expertise** in your specific domains
- **Becomes irreplaceable** through accumulated knowledge

### Getting Started

1. **Start your next session** with the start_session tool
2. **Load context** for any task you're working on
3. **Store discoveries** as you make them
4. **Search knowledge** when facing familiar problems
5. **Watch your AI partner** become increasingly valuable over time

**Welcome to AI partnership that actually learns and grows with you.**

This is the beginning of a new era in AI-human collaboration.