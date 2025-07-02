# PostgreSQL + pgvector Architecture Design
**KnowledgePersistence-AI Database Schema**

**Created**: 2025-07-02  
**Purpose**: Comprehensive database architecture for AI knowledge persistence  
**Technology**: PostgreSQL 17+ with pgvector extension + on-premises Supabase  
**Target**: Revolutionary AI session continuity and knowledge accumulation  

---

## Database Architecture Overview

### **Core Technology Stack**
- **PostgreSQL 17+**: Primary database with advanced JSON support
- **pgvector Extension**: Vector similarity search for semantic knowledge retrieval
- **Supabase (Self-hosted)**: Real-time subscriptions, REST API, row-level security
- **Custom Server**: On-premises deployment for full control and customization

### **Knowledge Storage Strategy**
- **Relational Structure**: Traditional tables for structured knowledge
- **Vector Embeddings**: Semantic similarity and contextual retrieval
- **JSON Fields**: Complex knowledge structures and metadata
- **Real-time Sync**: Live knowledge updates across sessions

---

## Comprehensive Database Schema

### **1. Core Knowledge Storage**

```sql
-- Primary knowledge items table
CREATE TABLE knowledge_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_type VARCHAR(50) NOT NULL CHECK (knowledge_type IN (
        'factual', 'procedural', 'contextual', 'relational', 'experiential', 'technical_discovery'
    )),
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_embedding VECTOR(1536), -- OpenAI embedding dimension
    context_data JSONB,
    importance_score INTEGER DEFAULT 50 CHECK (importance_score BETWEEN 1 AND 100),
    retrieval_triggers TEXT[], -- Keywords that should trigger this knowledge
    validation_status VARCHAR(20) DEFAULT 'pending' CHECK (validation_status IN (
        'pending', 'validated', 'needs_update', 'deprecated'
    )),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    created_by VARCHAR(100), -- Session or user identifier
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_knowledge_type ON knowledge_items(knowledge_type);
CREATE INDEX idx_category ON knowledge_items(category);
CREATE INDEX idx_importance ON knowledge_items(importance_score DESC);
CREATE INDEX idx_retrieval_triggers ON knowledge_items USING GIN(retrieval_triggers);
CREATE INDEX idx_content_embedding ON knowledge_items USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_context_data ON knowledge_items USING GIN(context_data);
```

### **2. Session Management and Tracking**

```sql
-- AI sessions tracking
CREATE TABLE ai_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_identifier VARCHAR(200) UNIQUE NOT NULL,
    project_context VARCHAR(200),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    session_duration INTERVAL,
    knowledge_items_accessed INTEGER DEFAULT 0,
    knowledge_items_created INTEGER DEFAULT 0,
    breakthrough_moments INTEGER DEFAULT 0,
    session_quality_score INTEGER CHECK (session_quality_score BETWEEN 1 AND 100),
    session_metadata JSONB,
    user_feedback TEXT
);

-- Link sessions to knowledge accessed/created
CREATE TABLE session_knowledge_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES ai_sessions(id) ON DELETE CASCADE,
    knowledge_id UUID REFERENCES knowledge_items(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN (
        'accessed', 'created', 'updated', 'validated', 'breakthrough', 'applied'
    )),
    interaction_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    learning_context TEXT,
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 10),
    breakthrough_indicator BOOLEAN DEFAULT FALSE,
    application_success BOOLEAN,
    notes TEXT
);

-- Performance indexes
CREATE INDEX idx_session_project ON ai_sessions(project_context);
CREATE INDEX idx_session_start ON ai_sessions(start_time DESC);
CREATE INDEX idx_session_knowledge ON session_knowledge_links(session_id, knowledge_id);
CREATE INDEX idx_interaction_type ON session_knowledge_links(interaction_type);
```

### **3. Relationship and Pattern Recognition**

```sql
-- User-AI interaction patterns
CREATE TABLE interaction_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(200) NOT NULL,
    situation_type VARCHAR(100) NOT NULL,
    user_behavior_description TEXT,
    ai_response_expected TEXT,
    success_indicators TEXT[],
    failure_indicators TEXT[],
    pattern_frequency INTEGER DEFAULT 1,
    last_observed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    effectiveness_score INTEGER CHECK (effectiveness_score BETWEEN 1 AND 100),
    pattern_metadata JSONB,
    examples JSONB -- Array of specific examples
);

-- Knowledge relationships and connections
CREATE TABLE knowledge_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_knowledge_id UUID REFERENCES knowledge_items(id) ON DELETE CASCADE,
    target_knowledge_id UUID REFERENCES knowledge_items(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN (
        'depends_on', 'enhances', 'contradicts', 'builds_upon', 'required_for', 'similar_to'
    )),
    strength DECIMAL(3,2) CHECK (strength BETWEEN 0.0 AND 1.0),
    discovered_in_session UUID REFERENCES ai_sessions(id),
    relationship_context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Prevent duplicate relationships
CREATE UNIQUE INDEX idx_unique_relationships ON knowledge_relationships(
    source_knowledge_id, target_knowledge_id, relationship_type
);
```

### **4. Technical Discovery and Problem-Solution Mapping**

```sql
-- Technical gotchas and solutions
CREATE TABLE technical_gotchas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_signature VARCHAR(500) NOT NULL,
    problem_description TEXT NOT NULL,
    problem_context JSONB,
    attempted_solutions JSONB, -- Array of attempts with outcomes
    working_solution TEXT,
    failure_patterns TEXT[],
    discovery_session UUID REFERENCES ai_sessions(id),
    problem_category VARCHAR(100),
    severity_level INTEGER CHECK (severity_level BETWEEN 1 AND 10),
    frequency_encountered INTEGER DEFAULT 1,
    last_encountered TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolution_time_minutes INTEGER,
    prevention_guidance TEXT,
    related_gotchas UUID[] -- References to other gotcha IDs
);

-- Command and API patterns
CREATE TABLE command_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    command_signature VARCHAR(500) NOT NULL,
    command_description TEXT,
    success_pattern TEXT NOT NULL,
    failure_patterns TEXT[],
    context_requirements TEXT[],
    parameter_notes JSONB,
    discovered_in_session UUID REFERENCES ai_sessions(id),
    usage_count INTEGER DEFAULT 1,
    success_rate DECIMAL(5,2), -- Percentage
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    command_category VARCHAR(100)
);
```

### **5. Experiential and Contextual Knowledge**

```sql
-- Project intuition and experiential insights
CREATE TABLE experiential_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    insight_title VARCHAR(300) NOT NULL,
    insight_description TEXT NOT NULL,
    emotional_context TEXT,
    motivation_driver TEXT,
    project_impact_description TEXT,
    insight_embedding VECTOR(1536),
    discovery_moment TEXT,
    validation_examples TEXT[],
    retention_method TEXT,
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 100),
    applicability_scope VARCHAR(200),
    insight_metadata JSONB,
    created_in_session UUID REFERENCES ai_sessions(id),
    applied_successfully INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Decision evolution and context trails
CREATE TABLE decision_evolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_topic VARCHAR(300) NOT NULL,
    initial_understanding TEXT,
    evolution_stages JSONB, -- Array of understanding changes
    final_understanding TEXT,
    key_influences TEXT[],
    breakthrough_moments JSONB,
    decision_rationale TEXT,
    alternative_approaches JSONB,
    lessons_learned TEXT,
    evolution_timeline JSONB,
    project_context VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **6. Knowledge Validation and Quality Control**

```sql
-- Knowledge validation tests and benchmarks
CREATE TABLE knowledge_validation_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_name VARCHAR(200) NOT NULL,
    test_category VARCHAR(100),
    test_scenario TEXT NOT NULL,
    expected_response TEXT NOT NULL,
    pass_criteria TEXT NOT NULL,
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 10),
    knowledge_types_tested VARCHAR(100)[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    test_metadata JSONB
);

-- Test execution results
CREATE TABLE validation_test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID REFERENCES knowledge_validation_tests(id) ON DELETE CASCADE,
    session_id UUID REFERENCES ai_sessions(id) ON DELETE CASCADE,
    test_executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ai_response TEXT,
    pass_status BOOLEAN,
    performance_score INTEGER CHECK (performance_score BETWEEN 0 AND 100),
    response_time_seconds DECIMAL(10,3),
    evaluator_notes TEXT,
    improvement_needed TEXT
);
```

---

## Vector Search and Semantic Retrieval

### **pgvector Configuration**

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Vector similarity functions for contextual retrieval
CREATE OR REPLACE FUNCTION find_similar_knowledge(
    query_embedding VECTOR(1536),
    knowledge_type_filter VARCHAR(50) DEFAULT NULL,
    limit_results INTEGER DEFAULT 10,
    similarity_threshold DECIMAL DEFAULT 0.7
)
RETURNS TABLE (
    id UUID,
    title VARCHAR(500),
    content TEXT,
    similarity_score DECIMAL,
    knowledge_type VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ki.id,
        ki.title,
        ki.content,
        (1 - (ki.content_embedding <=> query_embedding)) AS similarity_score,
        ki.knowledge_type
    FROM knowledge_items ki
    WHERE 
        (knowledge_type_filter IS NULL OR ki.knowledge_type = knowledge_type_filter)
        AND (1 - (ki.content_embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY ki.content_embedding <=> query_embedding
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;
```

### **Contextual Knowledge Triggers**

```sql
-- Function to automatically retrieve relevant knowledge based on context
CREATE OR REPLACE FUNCTION get_contextual_knowledge(
    current_situation TEXT,
    project_context VARCHAR(200) DEFAULT NULL,
    max_results INTEGER DEFAULT 20
)
RETURNS TABLE (
    knowledge_id UUID,
    title VARCHAR(500),
    content TEXT,
    relevance_reason TEXT,
    knowledge_type VARCHAR(50)
) AS $$
DECLARE
    situation_embedding VECTOR(1536);
BEGIN
    -- This would be called with embeddings generated from current situation
    -- Placeholder for embedding generation integration
    
    RETURN QUERY
    SELECT 
        ki.id,
        ki.title,
        ki.content,
        'Contextual match based on situation similarity' AS relevance_reason,
        ki.knowledge_type
    FROM knowledge_items ki
    WHERE 
        ki.retrieval_triggers && string_to_array(current_situation, ' ')
        OR ki.context_data->>'project' = project_context
    ORDER BY ki.importance_score DESC, ki.last_accessed DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;
```

---

## Real-time Capabilities with Supabase

### **Row Level Security (RLS)**

```sql
-- Enable RLS for session isolation
ALTER TABLE knowledge_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_sessions ENABLE ROW LEVEL SECURITY;

-- Policy for session-based access
CREATE POLICY session_knowledge_access ON knowledge_items
    FOR ALL USING (
        created_by = current_setting('app.current_session', true)
        OR validation_status = 'validated'
    );
```

### **Real-time Subscriptions**

```sql
-- Function to notify on knowledge updates
CREATE OR REPLACE FUNCTION notify_knowledge_update()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'knowledge_update',
        json_build_object(
            'operation', TG_OP,
            'knowledge_id', NEW.id,
            'knowledge_type', NEW.knowledge_type,
            'session_id', NEW.created_by
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for real-time updates
CREATE TRIGGER knowledge_update_trigger
    AFTER INSERT OR UPDATE ON knowledge_items
    FOR EACH ROW EXECUTE FUNCTION notify_knowledge_update();
```

---

## Performance Optimization

### **Partitioning Strategy**

```sql
-- Partition sessions by month for performance
CREATE TABLE ai_sessions_partitioned (
    LIKE ai_sessions INCLUDING ALL
) PARTITION BY RANGE (start_time);

-- Create monthly partitions
CREATE TABLE ai_sessions_202507 PARTITION OF ai_sessions_partitioned
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
```

### **Advanced Indexes**

```sql
-- Composite indexes for complex queries
CREATE INDEX idx_knowledge_type_importance ON knowledge_items(knowledge_type, importance_score DESC);
CREATE INDEX idx_session_knowledge_time ON session_knowledge_links(session_id, interaction_timestamp DESC);
CREATE INDEX idx_pattern_effectiveness ON interaction_patterns(situation_type, effectiveness_score DESC);

-- GIN indexes for array and JSONB fields
CREATE INDEX idx_retrieval_triggers_gin ON knowledge_items USING GIN(retrieval_triggers);
CREATE INDEX idx_context_metadata ON knowledge_items USING GIN(context_data);
CREATE INDEX idx_session_metadata ON ai_sessions USING GIN(session_metadata);
```

---

## Server Configuration Requirements

### **PostgreSQL Configuration**
```ini
# postgresql.conf optimizations for knowledge persistence
shared_preload_libraries = 'pg_stat_statements,pg_prewarm,vector'
max_connections = 200
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Vector extension settings
vector.max_dimensions = 2048
```

### **Supabase Self-hosted Configuration**
```yaml
# docker-compose.yml for self-hosted Supabase
version: '3.8'
services:
  db:
    image: supabase/postgres:15.1.0.117
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: knowledge_persistence
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    
  kong:
    image: kong:2.8.1
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: /var/lib/kong/kong.yml
    ports:
      - "8000:8000"
      - "8443:8443"
      - "8001:8001"
      - "8444:8444"
    
  auth:
    image: supabase/gotrue:v2.99.0
    environment:
      GOTRUE_API_HOST: 0.0.0.0
      GOTRUE_API_PORT: 9999
      GOTRUE_DB_DRIVER: postgres
```

---

## Implementation Phases

### **Phase 1: Core Database Setup**
1. PostgreSQL 17 installation with pgvector
2. Core schema deployment
3. Basic CRUD operations
4. Vector embedding integration

### **Phase 2: Supabase Integration**
5. Self-hosted Supabase deployment
6. Real-time subscriptions setup
7. REST API configuration
8. Row-level security implementation

### **Phase 3: Advanced Features**
9. Contextual knowledge retrieval
10. Relationship mapping algorithms
11. Validation system implementation
12. Performance optimization

---

**STATUS**: Architecture designed - ready for database server deployment and implementation.