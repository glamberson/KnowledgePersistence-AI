# Multi-Project Architecture for KnowledgePersistence-AI

**Date**: 2025-07-03  
**Purpose**: Design multi-project support for NavyCMMS, Genealogy, and future projects  
**Context**: Scaling KnowledgePersistence-AI to support multiple independent projects  

---

## 🎯 EXECUTIVE SUMMARY

This document outlines the architecture for extending KnowledgePersistence-AI to support multiple independent projects while maintaining knowledge isolation, shared strategic insights, and seamless project switching. The design ensures each project maintains its own knowledge domain while benefiting from cross-project strategic capabilities.

**Key Innovation**: Project-scoped knowledge persistence with cross-project strategic intelligence sharing.

---

## 🏗️ MULTI-PROJECT ARCHITECTURE

### **1. Project Isolation Strategy**

```
┌─────────────────────────────────────────────────────────────┐
│                 PROJECT ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────┤
│ PROJECT ISOLATION    │ SHARED INFRASTRUCTURE               │
│ • Project-specific   │ • Core AI capabilities              │
│   knowledge bases    │ • MCP tools                         │
│ • Separate contexts  │ • Pattern recognition               │
│ • Independent        │ • Strategic reasoning               │
│   configurations     │ • Session management                │
├─────────────────────────────────────────────────────────────┤
│ CROSS-PROJECT INTELLIGENCE                                  │
│ • Strategic insights shared across projects                 │
│ • Problem-solving patterns transferable                     │
│ • Development methodologies reusable                        │
│ • User preferences and working styles persistent            │
└─────────────────────────────────────────────────────────────┘
```

### **2. Database Schema Extension**

```sql
-- Project management tables
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    project_type VARCHAR(50), -- 'software', 'research', 'genealogy', etc.
    repository_url TEXT,
    local_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}'
);

-- Project-scoped knowledge items
ALTER TABLE knowledge_items 
ADD COLUMN project_id UUID REFERENCES projects(id),
ADD COLUMN is_cross_project BOOLEAN DEFAULT false;

-- Project-scoped sessions
ALTER TABLE ai_sessions 
ADD COLUMN project_id UUID REFERENCES projects(id);

-- Cross-project strategic insights
CREATE TABLE strategic_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    insight_type VARCHAR(50) NOT NULL, -- 'methodology', 'pattern', 'approach'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    source_project_id UUID REFERENCES projects(id),
    applicable_project_types TEXT[], -- Array of project types this applies to
    confidence_score FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content JSONB,
    embedding VECTOR(1536)
);
```

### **3. Project Configuration Structure**

```
┌─────────────────────────────────────────────────────────────┐
│                PROJECT DIRECTORY STRUCTURE                  │
├─────────────────────────────────────────────────────────────┤
│ KnowledgePersistence-AI/                                    │
│ ├── projects/                                               │
│ │   ├── KnowledgePersistence-AI/     # Self-reference      │
│ │   │   ├── PROJECT.md               # Project config      │
│ │   │   ├── knowledge/               # Project knowledge   │
│ │   │   └── sessions/                # Project sessions    │
│ │   ├── NavyCMMS/                                           │
│ │   │   ├── PROJECT.md                                      │
│ │   │   ├── knowledge/                                      │
│ │   │   └── sessions/                                       │
│ │   └── genealogy/                                          │
│ │       ├── PROJECT.md                                      │
│ │       ├── knowledge/                                      │
│ │       └── sessions/                                       │
│ ├── shared/                                                 │
│ │   ├── strategic-insights/          # Cross-project       │
│ │   ├── methodologies/               # Reusable approaches │
│ │   └── patterns/                    # Universal patterns  │
│ └── core/                           # Core system          │
│     ├── mcp-integration/                                    │
│     ├── pattern-recognition/                                │
│     └── session-management/                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 PROJECT CONFIGURATION SYSTEM

### **1. Project Configuration File (PROJECT.md)**

```markdown
# NavyCMMS Project Configuration

**Project Type**: Software Development  
**Domain**: Navy Computerized Maintenance Management System  
**Repository**: https://github.com/glamberson/NavyCMMS  
**Local Path**: /home/greg/NavyCMMS  

## Project Context
- Legacy PHP application modernization
- Database migration and optimization
- User interface improvements
- Security enhancements

## Knowledge Domains
- PHP/Laravel development
- Database design and migration
- Navy maintenance procedures
- Legacy system modernization

## AI Assistance Preferences
- Focus on code quality and security
- Prefer detailed explanations for complex systems
- Emphasize testing and documentation
- Consider Navy-specific requirements

## Cross-Project Learning
- Apply software modernization patterns
- Leverage database optimization techniques
- Share testing methodologies
- Transfer project management approaches
```

### **2. Project Initialization Script**

```python
class ProjectManager:
    def create_new_project(self, project_name, project_type, config=None):
        """Initialize a new project in the knowledge persistence system"""
        
        # 1. Create project record in database
        project_id = self.db.create_project({
            'name': project_name,
            'display_name': config.get('display_name', project_name),
            'project_type': project_type,
            'repository_url': config.get('repository_url'),
            'local_path': config.get('local_path'),
            'settings': config.get('settings', {})
        })
        
        # 2. Create project directory structure
        project_path = f"/home/greg/KnowledgePersistence-AI/projects/{project_name}"
        os.makedirs(f"{project_path}/knowledge", exist_ok=True)
        os.makedirs(f"{project_path}/sessions", exist_ok=True)
        
        # 3. Create PROJECT.md configuration file
        self.create_project_config(project_path, config)
        
        # 4. Initialize project-specific MCP configuration
        self.setup_project_mcp_config(project_name, project_path)
        
        # 5. Load applicable strategic insights from other projects
        self.load_cross_project_insights(project_id, project_type)
        
        return project_id

    def setup_project_mcp_config(self, project_name, project_path):
        """Create project-specific MCP configuration"""
        mcp_config = {
            "mcpServers": {
                "knowledge-persistence": {
                    "command": "python3",
                    "args": ["/home/greg/KnowledgePersistence-AI/mcp-integration/knowledge-mcp-server.py"],
                    "env": {
                        "PROJECT_NAME": project_name,
                        "PROJECT_PATH": project_path,
                        "PYTHONPATH": "/home/greg/KnowledgePersistence-AI"
                    }
                },
                "sequential-thinking": {
                    "command": "python3",
                    "args": ["/home/greg/KnowledgePersistence-AI/mcp-integration/python-sequential-thinking-mcp/sequential-thinking-mcp/main.py"],
                    "env": {
                        "PROJECT_CONTEXT": project_name
                    }
                },
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", project_path]
                }
            }
        }
        
        with open(f"{project_path}/claude-mcp-config.json", 'w') as f:
            json.dump(mcp_config, f, indent=2)
```

---

## 🔄 PROJECT SWITCHING MECHANISM

### **1. Session Context Management**

```python
class SessionManager:
    def switch_project_context(self, session_id, project_name):
        """Switch AI context to specific project"""
        
        # 1. Save current project state
        self.save_current_project_state(session_id)
        
        # 2. Load project configuration
        project_config = self.load_project_config(project_name)
        
        # 3. Load project-specific knowledge
        project_knowledge = self.load_project_knowledge(project_name)
        
        # 4. Load cross-project strategic insights
        strategic_insights = self.load_applicable_insights(project_name)
        
        # 5. Update session context
        self.update_session_context(session_id, {
            'current_project': project_name,
            'project_config': project_config,
            'project_knowledge': project_knowledge,
            'strategic_insights': strategic_insights
        })
        
        # 6. Warm cache for project-specific context
        self.warm_project_cache(session_id, project_name)

    def load_project_knowledge(self, project_name):
        """Load all knowledge specific to project"""
        return self.db.query("""
            SELECT * FROM knowledge_items 
            WHERE project_id = (SELECT id FROM projects WHERE name = %s)
               OR is_cross_project = true
            ORDER BY strategic_value DESC, created_at DESC
        """, [project_name])
```

### **2. CLI Project Commands**

```bash
# Project management commands
python knowledge_cli.py create-project --name "genealogy" --type "research" 
python knowledge_cli.py switch-project --name "NavyCMMS"
python knowledge_cli.py list-projects
python knowledge_cli.py project-status --name "genealogy"

# Project-specific session start
python knowledge_cli.py start-session --project "NavyCMMS"
python knowledge_cli.py start-session --project "genealogy"
```

---

## 🧠 CROSS-PROJECT INTELLIGENCE

### **1. Strategic Insight Sharing**

```python
class StrategicInsightEngine:
    def extract_transferable_insights(self, source_project, target_project_type):
        """Extract insights applicable to other project types"""
        
        # Analyze source project patterns
        patterns = self.pattern_recognizer.analyze_project_patterns(source_project)
        
        transferable_insights = []
        for pattern in patterns:
            if self.is_transferable(pattern, target_project_type):
                insight = {
                    'type': pattern.category,
                    'title': pattern.title,
                    'description': pattern.description,
                    'methodology': pattern.methodology,
                    'applicable_types': self.determine_applicable_types(pattern),
                    'confidence': pattern.confidence_score
                }
                transferable_insights.append(insight)
        
        return transferable_insights

    def suggest_cross_project_learning(self, current_project, current_challenge):
        """Suggest insights from other projects for current challenge"""
        
        similar_challenges = self.find_similar_challenges(current_challenge)
        
        suggestions = []
        for challenge in similar_challenges:
            if challenge.project != current_project:
                suggestion = {
                    'source_project': challenge.project,
                    'solution_approach': challenge.solution,
                    'relevance_score': challenge.similarity_score,
                    'adaptation_needed': self.assess_adaptation_needed(challenge, current_challenge)
                }
                suggestions.append(suggestion)
        
        return sorted(suggestions, key=lambda x: x['relevance_score'], reverse=True)
```

### **2. Universal Patterns Database**

```sql
-- Store patterns that apply across projects
CREATE TABLE universal_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(200) NOT NULL,
    pattern_type VARCHAR(100), -- 'development', 'research', 'problem-solving'
    description TEXT,
    methodology TEXT,
    examples JSONB, -- Examples from different projects
    success_metrics JSONB,
    applicable_domains TEXT[],
    usage_frequency INTEGER DEFAULT 0,
    effectiveness_rating FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR(1536)
);
```

---

## 🚀 IMPLEMENTATION ROADMAP

### **Phase 1: Core Multi-Project Infrastructure (Week 1)**

#### **Database Schema Updates**
```sql
-- Implement project tables and relationships
CREATE TABLE projects (...);
ALTER TABLE knowledge_items ADD COLUMN project_id UUID;
ALTER TABLE ai_sessions ADD COLUMN project_id UUID;
CREATE TABLE strategic_insights (...);
```

#### **Project Management System**
```python
# Implement ProjectManager class
class ProjectManager:
    def create_new_project(self, name, type, config): pass
    def switch_project_context(self, session_id, project): pass
    def load_project_knowledge(self, project): pass
```

### **Phase 2: Project Creation and Configuration (Week 2)**

#### **1. NavyCMMS Project Setup**
```bash
# Create NavyCMMS project
python knowledge_cli.py create-project \
    --name "NavyCMMS" \
    --type "software" \
    --repo "https://github.com/glamberson/NavyCMMS" \
    --path "/home/greg/NavyCMMS"
```

#### **2. Genealogy Project Setup**
```bash
# Create Genealogy project  
python knowledge_cli.py create-project \
    --name "genealogy" \
    --type "research" \
    --description "Multiple genealogy research projects"
```

#### **3. MCP Configuration per Project**
```json
{
  "mcpServers": {
    "knowledge-persistence": {
      "env": {
        "PROJECT_NAME": "NavyCMMS",
        "PROJECT_PATH": "/home/greg/KnowledgePersistence-AI/projects/NavyCMMS"
      }
    }
  }
}
```

### **Phase 3: Cross-Project Intelligence (Week 3)**

#### **Strategic Insight Engine**
```python
# Implement cross-project learning
class StrategicInsightEngine:
    def extract_transferable_insights(self): pass
    def suggest_cross_project_learning(self): pass
```

#### **Universal Patterns Database**
```sql
-- Populate with patterns from KnowledgePersistence-AI project
INSERT INTO universal_patterns (pattern_name, methodology, ...)
VALUES ('Iterative Development', 'Phase-based implementation with continuous refinement', ...);
```

---

## 🔧 PRACTICAL SETUP STEPS

### **For NavyCMMS Project:**

1. **Database Setup**
   ```sql
   INSERT INTO projects (name, display_name, project_type, repository_url, local_path)
   VALUES ('NavyCMMS', 'Navy CMMS Modernization', 'software', 
           'https://github.com/glamberson/NavyCMMS', '/home/greg/NavyCMMS');
   ```

2. **Directory Structure**
   ```bash
   mkdir -p /home/greg/KnowledgePersistence-AI/projects/NavyCMMS/{knowledge,sessions}
   ```

3. **Project Configuration**
   ```markdown
   # NavyCMMS/PROJECT.md
   **Project Type**: Software Development
   **Domain**: Navy Maintenance Management
   **Focus**: Legacy modernization, security, database optimization
   ```

### **For Genealogy Project:**

1. **Database Setup**
   ```sql
   INSERT INTO projects (name, display_name, project_type, description)
   VALUES ('genealogy', 'Genealogy Research Projects', 'research',
           'Multiple genealogy projects and family history research');
   ```

2. **Directory Structure**
   ```bash
   mkdir -p /home/greg/KnowledgePersistence-AI/projects/genealogy/{knowledge,sessions}
   ```

3. **Project Configuration**
   ```markdown
   # genealogy/PROJECT.md
   **Project Type**: Research
   **Domain**: Genealogy and Family History
   **Focus**: Family tree research, historical records, DNA analysis
   ```

### **Session Switching**
```bash
# Switch to NavyCMMS context
export CURRENT_PROJECT="NavyCMMS"
export PROJECT_CONFIG="/home/greg/KnowledgePersistence-AI/projects/NavyCMMS/PROJECT.md"

# Switch to Genealogy context  
export CURRENT_PROJECT="genealogy"
export PROJECT_CONFIG="/home/greg/KnowledgePersistence-AI/projects/genealogy/PROJECT.md"
```

---

## 🎯 BENEFITS OF MULTI-PROJECT ARCHITECTURE

### **1. Project Isolation**
- Each project maintains its own knowledge domain
- No cross-contamination of project-specific information
- Clean context switching between different work areas

### **2. Strategic Intelligence Sharing**
- Problem-solving patterns transfer across projects
- Development methodologies reusable
- Strategic insights accumulate across all work

### **3. Scalable Growth**
- Easy addition of new projects
- Consistent structure and configuration
- Shared infrastructure reduces setup complexity

### **4. Enhanced Strategic Partnership**
- AI learns your working patterns across all projects
- Cross-project experience improves all future work
- True strategic partner that grows with your portfolio

---

**This multi-project architecture transforms KnowledgePersistence-AI from a single-project tool to a comprehensive strategic partnership platform that scales across your entire professional portfolio while maintaining project-specific expertise and cross-project strategic intelligence.**