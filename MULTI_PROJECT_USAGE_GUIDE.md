# Multi-Project Usage Guide for KnowledgePersistence-AI

**Date**: 2025-07-03  
**Purpose**: Complete guide for using CCR, Claude, and MCP tools with multiple projects  
**Context**: Revolutionary multi-project strategic partnership system  

---

## 🎯 EXECUTIVE SUMMARY

This guide provides comprehensive instructions for using KnowledgePersistence-AI with multiple projects, including NavyCMMS, genealogy-ai, and future projects. The system maintains project-specific knowledge isolation while sharing strategic insights across all your work.

**Key Innovation**: Project-scoped AI strategic partnership with cross-project intelligence transfer.

---

## 🚀 QUICK START

### **1. List Available Projects**
```bash
cd /home/greg/KnowledgePersistence-AI
python3 project_manager.py list
```

### **2. Switch to a Project**
```bash
# Switch to genealogy-ai project
python3 project_manager.py switch genealogy-ai
source switch_to_genealogy-ai.sh

# Or manually
export CURRENT_PROJECT="genealogy-ai"
cd /home/greg/genealogy-ai
```

### **3. Start AI Session with Project Context**
```bash
# Using Claude Code with MCP
claude --mcp-config ./claude-mcp-config.json

# Using CCR (Claude Code Router)
ccr code

# Using direct MCP tools
python3 /home/greg/KnowledgePersistence-AI/mcp-integration/knowledge-mcp-server.py
```

---

## 🏗️ PROJECT MANAGEMENT

### **Creating New Projects**

#### **Basic Project Creation**
```bash
python3 project_manager.py create my-project --type software
```

#### **Advanced Project Creation**
```bash
python3 project_manager.py create my-research \
    --type research \
    --display-name "My Research Project" \
    --description "Advanced research on XYZ topic" \
    --repo "https://github.com/username/my-research" \
    --path "/home/greg/my-research"
```

#### **Available Project Types**
- `software` - Software development projects
- `research` - Research and analysis projects  
- `genealogy` - Genealogy and family history
- `ai` - AI and machine learning projects
- `general` - General purpose projects

### **Project Operations**

#### **List All Projects**
```bash
python3 project_manager.py list
```
**Output:**
```
🏗️  KnowledgePersistence-AI Projects
==================================================

📁 KnowledgePersistence-AI Development
   Name: KnowledgePersistence-AI
   Type: software
   Status: 🟢 Active
   Description: Revolutionary AI knowledge persistence...
   Created: 2025-07-03 19:46:19

📁 Genealogy AI Research
   Name: genealogy-ai
   Type: genealogy  
   Status: 🟢 Active
   Description: AI-powered genealogy research...
   Created: 2025-07-03 19:50:00
```

#### **Project Status**
```bash
python3 project_manager.py status genealogy-ai
```
**Output:**
```
📊 Project Status: Genealogy AI Research
==================================================
Name: genealogy-ai
Type: genealogy
Description: AI-powered genealogy research...
Local Path: /home/greg/genealogy-ai
Repository: N/A
Status: 🟢 Active
Created: 2025-07-03 19:50:00

📈 Statistics:
Knowledge Items: 0
AI Sessions: 0
Strategic Insights: 1
Last Activity: Never
```

#### **Switch Between Projects**
```bash
# Switch to genealogy-ai
python3 project_manager.py switch genealogy-ai
source switch_to_genealogy-ai.sh

# Switch to main project
python3 project_manager.py switch KnowledgePersistence-AI
source switch_to_KnowledgePersistence-AI.sh
```

---

## 🤖 USING CCR (CLAUDE CODE ROUTER)

### **CCR with Project Context**

#### **1. Basic CCR Usage**
```bash
# Switch to project context
cd /home/greg/genealogy-ai
export CURRENT_PROJECT="genealogy-ai"

# Start CCR interactive session
ccr code
```

#### **2. CCR with Knowledge Persistence**
When you use CCR in a project directory, it automatically:
- Loads project-specific knowledge from the database
- Accesses cross-project strategic insights
- Maintains session context tied to the current project
- Saves new knowledge with project association

#### **3. CCR Configuration for Projects**
CCR automatically detects project context through:
```bash
# Environment variables set by project switching
export CURRENT_PROJECT="genealogy-ai"
export PROJECT_PATH="/home/greg/genealogy-ai"
export PROJECT_TYPE="genealogy"
export MCP_CONFIG="/home/greg/genealogy-ai/claude-mcp-config.json"
```

#### **4. Example CCR Session**
```bash
# Switch to genealogy project
cd /home/greg/genealogy-ai
source /home/greg/KnowledgePersistence-AI/switch_to_genealogy-ai.sh

# Start CCR
ccr code

# CCR will now:
# ✅ Load genealogy-specific knowledge
# ✅ Access family history patterns
# ✅ Apply genealogy best practices
# ✅ Save new insights to genealogy-ai project
```

### **CCR Multi-Model Routing with Projects**

#### **Project-Specific Model Selection**
```bash
# For genealogy research (detail-oriented)
/model anthropic-direct,claude-sonnet-4-20250514

# For code analysis (fast processing)  
/model ollama,qwen2.5-dev

# For strategic planning (high-quality reasoning)
/model openai,gpt-4o-mini
```

#### **Automatic Model Selection by Project Type**
CCR can automatically select optimal models based on project type:
- **Genealogy**: High-quality models for detailed analysis
- **Software**: Code-specialized models for development
- **Research**: Reasoning-focused models for analysis

---

## 🧠 CLAUDE DESKTOP WITH MCP

### **Claude Desktop Project Integration**

#### **1. Project-Specific MCP Configuration**
Each project has its own `claude-mcp-config.json`:
```bash
# Genealogy AI project MCP config
cat /home/greg/genealogy-ai/claude-mcp-config.json
```

#### **2. Starting Claude with Project Context**
```bash
# Switch to project
cd /home/greg/genealogy-ai

# Start Claude with project MCP config
claude --mcp-config ./claude-mcp-config.json
```

#### **3. Available MCP Tools per Project**
Each project includes:
- **knowledge-persistence**: Project-specific knowledge access
- **sequential-thinking**: Structured reasoning for the project domain
- **think-mcp**: Anthropic's think tool for complex analysis
- **filesystem**: Project directory access

### **MCP Tools Usage Examples**

#### **Knowledge Persistence Tool**
```python
# Access project-specific knowledge
knowledge_search("family tree analysis methods")

# Add knowledge to current project
store_knowledge("genealogy research", "DNA analysis revealed...")

# Get cross-project insights
get_strategic_insights("research methodology")
```

#### **Sequential Thinking Tool**
```python
# Start structured thinking for genealogy research
sequential_thinking(
    thought="First, I need to identify all known family members",
    thoughtNumber=1,
    totalThoughts=5,
    nextThoughtNeeded=True
)

# Continue the thought process
sequential_thinking(
    thought="Next, I'll search historical records for each person",
    thoughtNumber=2,
    totalThoughts=5,
    nextThoughtNeeded=True
)
```

#### **Think Tool**
```python
# Use for complex genealogy analysis
think("I need to analyze this DNA match. Let me consider: 1) The cM value suggests a 2nd-3rd cousin relationship, 2) The shared segments are on chromosomes 7 and 12, 3) Looking at my tree, this could connect through the Smith line...")
```

---

## 📁 PROJECT DIRECTORY STRUCTURE

### **Standard Project Layout**
```
/home/greg/genealogy-ai/
├── PROJECT.md                 # Project configuration
├── claude-mcp-config.json     # MCP server configuration
├── README.md                  # Project documentation
├── data/                      # Project data files
├── docs/                      # Project documentation
├── research/                  # Research notes and findings
└── tools/                     # Project-specific tools
```

### **Knowledge Persistence Integration**
```
/home/greg/KnowledgePersistence-AI/
├── projects/
│   ├── genealogy-ai/          # Project knowledge cache
│   │   ├── knowledge/         # Cached knowledge items
│   │   └── sessions/          # Session histories
│   └── NavyCMMS/
│       ├── knowledge/
│       └── sessions/
├── shared/
│   ├── strategic-insights/    # Cross-project insights
│   └── patterns/             # Universal patterns
└── core/                     # Core system components
```

---

## 🔄 WORKFLOW EXAMPLES

### **Example 1: Genealogy Research Session**

#### **Setup**
```bash
# 1. Switch to genealogy project
cd /home/greg/KnowledgePersistence-AI
python3 project_manager.py switch genealogy-ai
source switch_to_genealogy-ai.sh

# 2. Navigate to project directory  
cd /home/greg/genealogy-ai

# 3. Start AI session
ccr code
```

#### **Research Workflow**
```
User: I want to research the Smith family line from Ireland

AI: I'll help you research the Smith family line from Ireland. Let me start with a structured approach using our sequential thinking process.

[Uses sequential-thinking MCP tool]
Thought 1/5: First, let's identify what we already know about the Smith family - names, dates, locations, and any existing documentation.

[Uses knowledge-persistence MCP tool]  
Accessing genealogy-specific knowledge... Found 3 relevant patterns from previous research.

[Uses think MCP tool]
Let me think about the best approach for Irish genealogy research. Irish records can be challenging due to the 1922 fire that destroyed many civil records. I should focus on: 1) Church records, 2) Griffith's Valuation, 3) Census substitutes, 4) DNA analysis if available...
```

### **Example 2: Software Development Session**

#### **Setup**
```bash
# 1. Switch to NavyCMMS project (when created)
python3 project_manager.py switch NavyCMMS
source switch_to_NavyCMMS.sh

# 2. Navigate to project
cd /home/greg/NavyCMMS

# 3. Start development session
ccr code
```

#### **Development Workflow**
```
User: I need to refactor the database connection code

AI: I'll help you refactor the NavyCMMS database connection code. Let me apply software development best practices and leverage insights from other projects.

[Uses knowledge-persistence MCP tool]
Loading NavyCMMS-specific knowledge... Found database architecture patterns and PHP modernization insights.

[Uses sequential-thinking MCP tool]
Thought 1/4: First, let's analyze the current database connection implementation to identify improvement opportunities.

[Applies strategic insights from KnowledgePersistence-AI project]
Based on our experience with PostgreSQL optimization in the KnowledgePersistence-AI project, I recommend implementing connection pooling and prepared statements...
```

---

## 🛠️ ADVANCED CONFIGURATION

### **Custom Project Types**

#### **Creating Custom Project Types**
You can extend the system with custom project types by modifying `project_manager.py`:

```python
# Add custom project type contexts
def get_project_type_context(self, project_type):
    contexts = {
        'software': 'Software development project...',
        'genealogy': 'Genealogy and family history...',
        'medical-research': 'Medical research with focus on clinical data...',  # Custom
        'legal-analysis': 'Legal research and case analysis...',              # Custom
        # Add your custom types here
    }
    return contexts.get(project_type, 'General purpose project')
```

### **Environment Variables**

#### **Global Configuration**
```bash
# Core system paths
export KNOWLEDGE_AI_HOME="/home/greg/KnowledgePersistence-AI"
export KNOWLEDGE_AI_DB="postgresql://postgres:SecureKnowledgePassword2025@192.168.10.90:5432/knowledge_persistence"

# Current project context (set by project switching)
export CURRENT_PROJECT="genealogy-ai"
export PROJECT_PATH="/home/greg/genealogy-ai"
export PROJECT_TYPE="genealogy"
export MCP_CONFIG="/home/greg/genealogy-ai/claude-mcp-config.json"
```

#### **Project-Specific Environment**
Each project can define custom environment variables in its `PROJECT.md`:
```bash
# Genealogy-specific tools
export GEDCOM_VIEWER="/usr/bin/gramps"
export DNA_ANALYSIS_TOOL="/home/greg/tools/dna-analyzer"

# Research databases  
export ANCESTRY_COM_LOGIN="your-username"
export FAMILYSEARCH_API_KEY="your-api-key"
```

---

## 🧪 TESTING AND VERIFICATION

### **Test Project Setup**
```bash
# 1. Verify project creation
python3 project_manager.py status genealogy-ai

# 2. Test project switching
python3 project_manager.py switch genealogy-ai
echo $CURRENT_PROJECT  # Should output: genealogy-ai

# 3. Test MCP configuration
cd /home/greg/genealogy-ai
python3 -c "import json; print(json.load(open('claude-mcp-config.json'))['mcpServers'].keys())"

# 4. Test knowledge persistence
# Start a CCR session and verify project context is loaded
```

### **Verify Database Integration**
```bash
# Check project exists in database
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && PGPASSWORD=SecureKnowledgePassword2025 psql -h localhost -U postgres -d knowledge_persistence -c \"SELECT name, display_name, project_type FROM projects;\""
```

---

## 🔧 TROUBLESHOOTING

### **Common Issues**

#### **Project Not Found**
```bash
# Problem: "Project 'genealogy-ai' not found"
# Solution: Verify project exists
python3 project_manager.py list

# If missing, recreate:
python3 project_manager.py create genealogy-ai --type genealogy --path "/home/greg/genealogy-ai"
```

#### **MCP Server Errors**
```bash
# Problem: MCP server fails to start
# Solution: Check environment variables
echo $PROJECT_NAME
echo $PROJECT_PATH

# Verify MCP config file exists
ls -la /home/greg/genealogy-ai/claude-mcp-config.json
```

#### **Database Connection Issues**
```bash
# Problem: Cannot connect to knowledge database
# Solution: Test database connectivity
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python3 -c 'import psycopg; psycopg.connect(host=\"localhost\", dbname=\"knowledge_persistence\", user=\"postgres\", password=\"SecureKnowledgePassword2025\"); print(\"OK\")'"
```

#### **CCR Not Using Project Context**
```bash
# Problem: CCR doesn't load project-specific knowledge
# Solution: Ensure environment variables are set
source /home/greg/KnowledgePersistence-AI/switch_to_genealogy-ai.sh
ccr status  # Should show project context
```

---

## 🎯 BEST PRACTICES

### **Project Organization**
1. **Consistent Naming**: Use lowercase, hyphenated names (e.g., `genealogy-ai`, `navy-cmms`)
2. **Clear Types**: Choose appropriate project types for optimal AI assistance
3. **Good Descriptions**: Provide detailed descriptions for better context loading
4. **Regular Switching**: Always switch project context before starting work

### **Knowledge Management**
1. **Project Isolation**: Keep project-specific knowledge separate
2. **Strategic Sharing**: Let cross-project insights flow naturally
3. **Regular Updates**: Update project configurations as needs evolve
4. **Documentation**: Maintain clear project documentation

### **AI Interaction**
1. **Context Awareness**: Always verify current project before starting sessions
2. **Tool Usage**: Leverage MCP tools for structured thinking and knowledge access
3. **Model Selection**: Choose appropriate models for project type and task complexity
4. **Session Continuity**: Maintain session context within project boundaries

---

## 🚀 FUTURE ENHANCEMENTS

### **Planned Features**
1. **Auto-Detection**: Automatic project context detection based on working directory
2. **Team Collaboration**: Multi-user project sharing and collaboration
3. **Integration Hub**: Direct integration with external tools and services
4. **Advanced Analytics**: Project progress tracking and insight generation

### **Integration Opportunities**
1. **GitHub Integration**: Automatic project creation from repositories
2. **Cloud Sync**: Project synchronization across multiple machines
3. **External APIs**: Integration with project-specific APIs and services
4. **Workflow Automation**: Automated project setup and configuration

---

**This multi-project system transforms KnowledgePersistence-AI from a single-purpose tool into a comprehensive strategic partnership platform that scales across your entire professional portfolio while maintaining perfect project isolation and cross-project strategic intelligence transfer.**