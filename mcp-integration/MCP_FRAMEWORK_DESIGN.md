# MCP Framework Design for KnowledgePersistence-AI
**Model Context Protocol Integration Architecture**

**Created**: 2025-07-02  
**Purpose**: Seamless AI knowledge access via MCP protocol  
**Integration**: PostgreSQL + pgvector + Supabase + Claude Code  
**Goal**: Transparent knowledge persistence without workflow disruption  

---

## MCP Integration Overview

### **Current MCP Configuration** (NavyCMMS)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/greg"]
    },
    "desktop-commander": {
      "command": "desktop-commander"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### **Enhanced MCP Configuration** (KnowledgePersistence-AI)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/greg"]
    },
    "github": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "knowledge-persistence": {
      "command": "node",
      "args": ["/home/greg/KnowledgePersistence-AI/mcp-integration/server/knowledge-server.js"],
      "env": {
        "DATABASE_URL": "${KNOWLEDGE_DB_URL}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "SESSION_ID": "${CURRENT_SESSION_ID}"
      }
    },
    "navycmms-integration": {
      "command": "node", 
      "args": ["/home/greg/KnowledgePersistence-AI/mcp-integration/server/navycmms-bridge.js"],
      "env": {
        "NAVYCMMS_PROJECT_PATH": "/home/greg/NavyCMMS-ProjectMgt",
        "NAVYCMMS_REPO_PATH": "/home/greg/NavyCMMS",
        "KNOWLEDGE_DB_URL": "${KNOWLEDGE_DB_URL}"
      }
    }
  }
}
```

---

## Custom MCP Server Architecture

### **1. Knowledge Persistence MCP Server**

#### **Core Tools Provided**
```typescript
// knowledge-server.js - Custom MCP server for AI knowledge persistence

interface KnowledgeTools {
  // Session Management
  start_session: (project_context: string) => SessionInfo;
  end_session: (insights: string[], breakthroughs: string[]) => SessionSummary;
  
  // Knowledge Retrieval
  get_contextual_knowledge: (situation: string, max_results?: number) => KnowledgeItem[];
  search_similar_knowledge: (query: string, knowledge_type?: string) => KnowledgeItem[];
  get_technical_gotchas: (problem_signature: string) => TechnicalGotcha[];
  
  // Knowledge Storage
  store_knowledge: (knowledge: KnowledgeInput) => KnowledgeItem;
  store_technical_discovery: (problem: string, solution: string, context: string) => TechnicalGotcha;
  store_interaction_pattern: (pattern: InteractionPattern) => PatternInfo;
  
  // Relationship Mapping
  link_knowledge: (source_id: string, target_id: string, relationship: string) => RelationshipInfo;
  get_knowledge_network: (knowledge_id: string, depth?: number) => KnowledgeNetwork;
  
  // Validation and Testing
  run_knowledge_tests: (test_category?: string) => ValidationResults;
  validate_knowledge_retention: (session_id: string) => RetentionMetrics;
}
```

#### **Session Management Implementation**
```javascript
// Session startup with automatic knowledge loading
async function start_session(project_context) {
  const sessionId = generateSessionId();
  const currentSession = await db.createSession({
    session_identifier: sessionId,
    project_context: project_context,
    start_time: new Date()
  });
  
  // Load contextual knowledge for session startup
  const contextualKnowledge = await getContextualStartupKnowledge(project_context);
  const interactionPatterns = await getRelevantInteractionPatterns(project_context);
  const technicalGotchas = await getRecentTechnicalDiscoveries();
  
  return {
    session_id: sessionId,
    startup_knowledge: contextualKnowledge,
    interaction_patterns: interactionPatterns,
    technical_context: technicalGotchas,
    validation_tests: await getStartupValidationTests()
  };
}

// Automatic knowledge capture during session
async function captureSessionActivity(activity) {
  await db.recordKnowledgeInteraction({
    session_id: getCurrentSessionId(),
    interaction_type: activity.type,
    knowledge_accessed: activity.knowledge_ids,
    learning_context: activity.context,
    breakthrough_indicator: activity.is_breakthrough
  });
}
```

### **2. NavyCMMS Integration Bridge**

#### **Project Context Integration**
```javascript
// navycmms-bridge.js - Bridge between knowledge system and NavyCMMS project

class NavyCMMSKnowledgeBridge {
  async getProjectContext() {
    const gitStatus = await this.getGitStatus();
    const openIssues = await this.getOpenIssues();
    const recentCommits = await this.getRecentCommits();
    const handoffContext = await this.getLatestHandoff();
    
    return {
      project_state: gitStatus,
      active_issues: openIssues,
      recent_changes: recentCommits,
      session_context: handoffContext,
      foundation_status: await this.getFoundationStatus()
    };
  }
  
  async storeProjectInsight(insight) {
    // Store NavyCMMS-specific insights in knowledge database
    await knowledgeDB.store_knowledge({
      knowledge_type: 'experiential',
      category: 'navycmms_project',
      title: insight.title,
      content: insight.description,
      context_data: {
        project: 'NavyCMMS',
        issue_references: insight.related_issues,
        git_context: insight.git_state
      },
      retrieval_triggers: insight.triggers
    });
  }
  
  async getFoundationStatus() {
    // Analyze actual project state vs claims
    const issues = await github.getIssues('lamco-admin', 'NavyCMMS-ProjectMgt');
    const foundationIssues = issues.filter(i => 
      i.labels.includes('foundation') || 
      i.title.includes('ARCHITECTURE') ||
      i.labels.includes('standards')
    );
    
    return {
      foundation_complete: foundationIssues.filter(i => i.state === 'closed').length,
      foundation_pending: foundationIssues.filter(i => i.state === 'open').length,
      critical_blockers: foundationIssues.filter(i => 
        i.labels.includes('priority-critical') && i.state === 'open'
      ),
      evidence_based_assessment: this.analyzeFoundationEvidence(foundationIssues)
    };
  }
}
```

---

## Automatic Knowledge Capture System

### **Transparent Knowledge Collection**
```javascript
// Automatic capture without disrupting workflow
class TransparentKnowledgeCapture {
  
  // Capture tool usage patterns
  async onToolUse(tool_name, tool_args, tool_result) {
    if (this.isLearningOpportunity(tool_name, tool_result)) {
      await this.captureToolPattern({
        tool: tool_name,
        context: tool_args,
        outcome: tool_result,
        success: !tool_result.error,
        session_id: getCurrentSessionId()
      });
    }
  }
  
  // Capture problem-solving patterns
  async onProblemSolved(problem_description, solution_steps, outcome) {
    await knowledgeDB.store_technical_discovery(
      problem_description,
      solution_steps.join(' → '),
      {
        session_context: getCurrentContext(),
        success_indicators: outcome.success_metrics,
        failure_prevention: outcome.gotchas_avoided
      }
    );
  }
  
  // Capture interaction dynamics
  async onUserInteraction(user_input, ai_response, interaction_outcome) {
    if (this.isSignificantInteraction(user_input, ai_response)) {
      await knowledgeDB.store_interaction_pattern({
        situation_type: this.classifyInteraction(user_input),
        user_behavior: user_input,
        ai_response_pattern: ai_response,
        effectiveness_indicators: interaction_outcome,
        session_id: getCurrentSessionId()
      });
    }
  }
}
```

### **Contextual Knowledge Retrieval**
```javascript
// Automatic knowledge injection based on context
class ContextualKnowledgeInjection {
  
  async onSituationDetected(situation_type, context) {
    const relevantKnowledge = await knowledgeDB.get_contextual_knowledge(
      situation_type, 
      context.project_name,
      10 // max results
    );
    
    if (relevantKnowledge.length > 0) {
      return {
        type: 'knowledge_injection',
        knowledge_items: relevantKnowledge,
        application_guidance: this.generateApplicationGuidance(relevantKnowledge, context)
      };
    }
  }
  
  // Devil's advocate trigger
  async onCompletionClaim(claim_text, project_context) {
    const devilsAdvocateKnowledge = await knowledgeDB.search_similar_knowledge(
      'devil advocate completion claim evidence project data',
      'procedural'
    );
    
    const projectEvidence = await navycmmsBridge.getProjectEvidence(claim_text);
    
    return {
      type: 'verification_prompt',
      methodology: devilsAdvocateKnowledge,
      evidence_to_check: projectEvidence,
      verification_questions: this.generateVerificationQuestions(claim_text)
    };
  }
}
```

---

## Session Continuity Protocol

### **Enhanced Session Startup**
```javascript
// Comprehensive session initialization
async function enhancedSessionStartup(project_context = 'NavyCMMS') {
  
  // Phase 1: Basic session setup
  const session = await knowledgeDB.start_session(project_context);
  
  // Phase 2: Project context loading
  const projectState = await navycmmsBridge.getProjectContext();
  
  // Phase 3: Contextual knowledge retrieval
  const startupKnowledge = await knowledgeDB.get_contextual_knowledge(
    `session_startup project_${project_context}`,
    project_context,
    20
  );
  
  // Phase 4: Validation testing
  const validationResults = await knowledgeDB.run_knowledge_tests('startup');
  
  // Phase 5: Capability calibration
  const retentionMetrics = await knowledgeDB.validate_knowledge_retention(session.session_id);
  
  return {
    session_info: session,
    project_context: projectState,
    available_knowledge: startupKnowledge,
    validation_status: validationResults,
    retention_quality: retentionMetrics,
    recommended_actions: generateStartupRecommendations(
      projectState, 
      startupKnowledge, 
      validationResults
    )
  };
}
```

### **Automatic Knowledge Updates**
```javascript
// Real-time knowledge system updates
class RealTimeKnowledgeSync {
  
  constructor() {
    this.supabase = createSupabaseClient(DATABASE_URL);
    this.setupRealTimeSubscriptions();
  }
  
  setupRealTimeSubscriptions() {
    // Subscribe to knowledge updates
    this.supabase
      .channel('knowledge_updates')
      .on('postgres_changes', { 
        event: '*', 
        schema: 'public', 
        table: 'knowledge_items' 
      }, (payload) => {
        this.handleKnowledgeUpdate(payload);
      })
      .subscribe();
      
    // Subscribe to session activities
    this.supabase
      .channel('session_activity')
      .on('postgres_changes', {
        event: '*',
        schema: 'public', 
        table: 'session_knowledge_links'
      }, (payload) => {
        this.handleSessionActivity(payload);
      })
      .subscribe();
  }
  
  async handleKnowledgeUpdate(update) {
    // Automatically refresh relevant knowledge in current session
    if (update.new.importance_score > 80) {
      await this.notifyHighImportanceKnowledge(update.new);
    }
  }
}
```

---

## Vector Embedding Integration

### **OpenAI Embeddings Service**
```javascript
// Automatic embedding generation for semantic search
class EmbeddingService {
  
  constructor(openai_api_key) {
    this.openai = new OpenAI({ apiKey: openai_api_key });
  }
  
  async generateEmbedding(text) {
    const response = await this.openai.embeddings.create({
      model: "text-embedding-3-small",
      input: text,
      encoding_format: "float"
    });
    
    return response.data[0].embedding;
  }
  
  async storeKnowledgeWithEmbedding(knowledge_item) {
    const embedding = await this.generateEmbedding(
      `${knowledge_item.title} ${knowledge_item.content}`
    );
    
    return await knowledgeDB.store_knowledge({
      ...knowledge_item,
      content_embedding: embedding
    });
  }
  
  async semanticSearch(query, knowledge_type = null, limit = 10) {
    const queryEmbedding = await this.generateEmbedding(query);
    
    return await knowledgeDB.query(`
      SELECT * FROM find_similar_knowledge($1, $2, $3, 0.7)
    `, [queryEmbedding, knowledge_type, limit]);
  }
}
```

---

## Tool Integration Examples

### **Enhanced GitHub Operations**
```javascript
// GitHub tools with automatic knowledge capture
class EnhancedGitHubTools {
  
  async createIssue(repo, title, body, labels) {
    const result = await github.issues.create({
      owner: 'lamco-admin',
      repo: repo,
      title: title,
      body: body,
      labels: labels
    });
    
    // Automatically capture issue creation pattern
    await knowledgeDB.store_knowledge({
      knowledge_type: 'procedural',
      category: 'github_operations',
      title: `Issue Creation Pattern: ${title}`,
      content: `Successfully created issue ${result.data.number} with pattern: ${this.extractPattern(title, labels)}`,
      context_data: {
        repo: repo,
        issue_number: result.data.number,
        labels_used: labels
      },
      retrieval_triggers: ['github', 'issue', 'creation', repo]
    });
    
    return result;
  }
  
  async analyzeIssueForKnowledge(repo, issue_number) {
    const issue = await github.issues.get({ owner: 'lamco-admin', repo, issue_number });
    const comments = await github.issues.listComments({ owner: 'lamco-admin', repo, issue_number });
    
    // Extract user guidance and insights from comments
    const userInsights = this.extractUserInsights(comments.data);
    
    for (const insight of userInsights) {
      await knowledgeDB.store_knowledge({
        knowledge_type: 'contextual',
        category: 'user_guidance',
        title: `User Insight: ${insight.topic}`,
        content: insight.content,
        context_data: {
          source_issue: issue_number,
          repo: repo,
          guidance_type: insight.type
        },
        retrieval_triggers: insight.triggers
      });
    }
  }
}
```

---

## Implementation Roadmap

### **Phase 1: Basic MCP Server (Week 1-2)**
- Custom knowledge-persistence MCP server
- Basic CRUD operations for knowledge
- Session management integration
- PostgreSQL + pgvector connection

### **Phase 2: NavyCMMS Integration (Week 3-4)**  
- NavyCMMS bridge MCP server
- Project context integration
- Automatic knowledge capture from NavyCMMS activities
- Foundation status verification automation

### **Phase 3: Advanced Features (Week 5-8)**
- Vector similarity search
- Contextual knowledge injection
- Real-time Supabase subscriptions
- Validation and testing systems

### **Phase 4: Production Optimization (Week 9-12)**
- Performance optimization
- Advanced relationship mapping
- Breakthrough moment detection
- Full session continuity pipeline

---

## Server Deployment Configuration

### **MCP Server Package Structure**
```
mcp-integration/
├── server/
│   ├── knowledge-server.js          # Main knowledge persistence server
│   ├── navycmms-bridge.js           # NavyCMMS project integration
│   ├── embedding-service.js         # OpenAI embeddings integration
│   ├── validation-service.js        # Knowledge validation and testing
│   └── utils/
│       ├── database.js              # PostgreSQL/Supabase client
│       ├── session-manager.js       # Session lifecycle management
│       └── knowledge-analyzer.js    # Pattern recognition and analysis
├── package.json                     # Node.js dependencies
├── docker-compose.yml               # Local development setup
└── deployment/
    ├── systemd/                     # Service configuration
    └── nginx/                       # Reverse proxy config
```

### **Environment Configuration**
```bash
# .env file for MCP servers
DATABASE_URL="postgresql://user:pass@localhost:5432/knowledge_persistence"
OPENAI_API_KEY="sk-..."
GITHUB_PERSONAL_ACCESS_TOKEN="ghp_..."
SUPABASE_URL="http://localhost:8000"
SUPABASE_ANON_KEY="ey..."
NAVYCMMS_PROJECT_PATH="/home/greg/NavyCMMS-ProjectMgt"
NAVYCMMS_REPO_PATH="/home/greg/NavyCMMS"
```

---

**STATUS**: MCP framework designed - ready for implementation and seamless AI knowledge persistence integration.