-- Complete Schema V2 with Versioning and Migration Support
-- Knowledge Persistence AI - Production Ready Schema
-- Version: 2.0.0
-- Date: 2025-07-06

-- Schema versioning table (must be first)
CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100) DEFAULT current_user,
    migration_script TEXT,
    rollback_script TEXT,
    checksum VARCHAR(64)
);

-- Insert current version
INSERT INTO schema_versions (version, description, migration_script) 
VALUES ('2.0.0', 'Production-ready schema with pattern intelligence', '-- V2.0.0 migration script --')
ON CONFLICT (version) DO NOTHING;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector for embeddings

-- Core Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    project_type VARCHAR(50) DEFAULT 'general',
    repository_url TEXT,
    local_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}'::jsonb,
    schema_version VARCHAR(20) DEFAULT '2.0.0',
    
    -- Constraints
    CONSTRAINT valid_project_type CHECK (project_type IN ('software', 'research', 'genealogy', 'general', 'ai', 'pattern_intelligence')),
    CONSTRAINT valid_settings CHECK (jsonb_typeof(settings) = 'object')
);

-- AI Sessions with Enhanced Tracking
CREATE TABLE IF NOT EXISTS ai_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_identifier VARCHAR(200) NOT NULL,
    project_id UUID REFERENCES projects(id),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    session_type VARCHAR(50) DEFAULT 'interactive',
    user_context JSONB DEFAULT '{}'::jsonb,
    session_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Performance metrics
    total_interactions INTEGER DEFAULT 0,
    successful_interactions INTEGER DEFAULT 0,
    failed_interactions INTEGER DEFAULT 0,
    average_response_time FLOAT DEFAULT 0.0,
    
    -- AI capabilities tracking
    pattern_extraction_enabled BOOLEAN DEFAULT true,
    semantic_classification_enabled BOOLEAN DEFAULT true,
    error_recovery_enabled BOOLEAN DEFAULT true,
    
    -- Versioning
    schema_version VARCHAR(20) DEFAULT '2.0.0',
    
    UNIQUE(session_identifier, project_id)
);

-- Enhanced Knowledge Items with Semantic Classification
CREATE TABLE IF NOT EXISTS knowledge_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    project_id UUID REFERENCES projects(id),
    session_id UUID REFERENCES ai_sessions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Semantic classification
    semantic_type VARCHAR(50),
    classification_confidence FLOAT DEFAULT 0.0,
    classification_method VARCHAR(50) DEFAULT 'rule_based',
    
    -- Importance and quality metrics
    importance_score INTEGER DEFAULT 50 CHECK (importance_score BETWEEN 0 AND 100),
    quality_score INTEGER DEFAULT 50 CHECK (quality_score BETWEEN 0 AND 100),
    usage_count INTEGER DEFAULT 0,
    validation_count INTEGER DEFAULT 0,
    contradiction_count INTEGER DEFAULT 0,
    
    -- Search and retrieval
    embedding VECTOR(768),  -- 768-dimensional embeddings
    full_text_search TSVECTOR,
    
    -- Cross-project intelligence
    is_cross_project BOOLEAN DEFAULT false,
    source_projects UUID[] DEFAULT '{}',
    
    -- Versioning and lifecycle
    version INTEGER DEFAULT 1,
    superseded_by UUID REFERENCES knowledge_items(id),
    supersedes UUID[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT valid_knowledge_type CHECK (knowledge_type IN (
        'factual', 'procedural', 'contextual', 'relational', 
        'experiential', 'technical', 'patterns', 'strategic'
    )),
    CONSTRAINT valid_semantic_type CHECK (semantic_type IS NULL OR semantic_type IN (
        'factual', 'procedural', 'contextual', 'relational', 
        'experiential', 'technical_discovery', 'pattern_recognition', 'strategic_insight'
    ))
);

-- Patterns Table (Enhanced from fork)
CREATE TABLE IF NOT EXISTS patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content JSONB NOT NULL,
    confidence FLOAT DEFAULT 0.0 CHECK (confidence BETWEEN 0.0 AND 1.0),
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0 CHECK (success_rate BETWEEN 0.0 AND 1.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_id UUID REFERENCES projects(id),
    source_interaction_id UUID,
    
    -- Enhanced semantic information
    semantic_type VARCHAR(50),
    classification_confidence FLOAT DEFAULT 0.0,
    extraction_method VARCHAR(50) DEFAULT 'semantic_classifier',
    
    -- Embeddings and search
    embedding VECTOR(768),
    full_text_search TSVECTOR,
    
    -- Pattern lifecycle and validation
    validation_status VARCHAR(20) DEFAULT 'pending',
    superseded_by UUID REFERENCES patterns(id),
    supersedes UUID[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    
    -- Pattern strength and validation
    pattern_strength FLOAT DEFAULT 0.0,
    validation_count INTEGER DEFAULT 0,
    contradiction_count INTEGER DEFAULT 0,
    
    -- Extraction metadata
    extraction_model VARCHAR(100),
    extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Graph adjacency for performance
    adjacency_list UUID[] DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT valid_pattern_type CHECK (pattern_type IN (
        'procedural_sequence', 'process_flow', 'causal_relationship', 
        'dependency_relationship', 'recurring_pattern', 'content_pattern',
        'meta_pattern', 'strategic_pattern'
    )),
    CONSTRAINT valid_validation_status CHECK (validation_status IN (
        'pending', 'validated', 'contradicted', 'superseded', 'archived'
    ))
);

-- Pattern Relationships with Evidence Tracking
CREATE TABLE IF NOT EXISTS pattern_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_pattern_id UUID REFERENCES patterns(id),
    target_pattern_id UUID REFERENCES patterns(id),
    relationship_type VARCHAR(50) NOT NULL,
    strength FLOAT DEFAULT 0.0 CHECK (strength BETWEEN 0.0 AND 1.0),
    confidence FLOAT DEFAULT 0.0 CHECK (confidence BETWEEN 0.0 AND 1.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Evidence and validation
    evidence JSONB DEFAULT '{}',
    validation_count INTEGER DEFAULT 0,
    contradiction_count INTEGER DEFAULT 0,
    
    -- Extraction metadata
    extraction_method VARCHAR(50) DEFAULT 'semantic_analyzer',
    extraction_model VARCHAR(100),
    extraction_confidence FLOAT DEFAULT 0.0,
    
    -- Lifecycle
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    UNIQUE(source_pattern_id, target_pattern_id, relationship_type),
    CONSTRAINT valid_relationship_type CHECK (relationship_type IN (
        'causes', 'depends_on', 'follows', 'similar_to', 'contradicts',
        'enhances', 'replaces', 'part_of', 'example_of', 'prerequisite_for'
    )),
    CONSTRAINT no_self_reference CHECK (source_pattern_id != target_pattern_id)
);

-- Strategic Insights (Enhanced from original)
CREATE TABLE IF NOT EXISTS strategic_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    source_project_id UUID REFERENCES projects(id),
    applicable_project_types TEXT[],
    confidence_score FLOAT DEFAULT 0.0 CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    usage_count INTEGER DEFAULT 0,
    effectiveness_rating FLOAT DEFAULT 0.0 CHECK (effectiveness_rating BETWEEN 0.0 AND 1.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Enhanced content and classification
    content JSONB DEFAULT '{}',
    semantic_type VARCHAR(50),
    classification_confidence FLOAT DEFAULT 0.0,
    
    -- Search and retrieval
    embedding VECTOR(768),
    full_text_search TSVECTOR,
    
    -- Validation and lifecycle
    validation_status VARCHAR(20) DEFAULT 'pending',
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT valid_insight_type CHECK (insight_type IN (
        'methodology', 'pattern', 'approach', 'lesson', 'strategy',
        'optimization', 'risk_mitigation', 'best_practice'
    ))
);

-- Pattern Validation Tracking
CREATE TABLE IF NOT EXISTS pattern_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID REFERENCES patterns(id),
    validation_type VARCHAR(50) NOT NULL,
    validation_result BOOLEAN NOT NULL,
    validation_evidence JSONB DEFAULT '{}',
    validated_by VARCHAR(100) NOT NULL,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT DEFAULT 0.0 CHECK (confidence BETWEEN 0.0 AND 1.0),
    
    -- Context
    session_id UUID REFERENCES ai_sessions(id),
    project_id UUID REFERENCES projects(id),
    
    -- Constraints
    CONSTRAINT valid_validation_type CHECK (validation_type IN (
        'usage_success', 'outcome_verification', 'contradiction_check',
        'peer_review', 'automated_validation', 'user_feedback'
    )),
    CONSTRAINT valid_validated_by CHECK (validated_by IN (
        'system', 'user', 'llm', 'semantic_classifier', 'pattern_engine', 'peer_review'
    ))
);

-- Pattern Usage Tracking
CREATE TABLE IF NOT EXISTS pattern_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID REFERENCES patterns(id),
    session_id UUID REFERENCES ai_sessions(id),
    usage_context JSONB DEFAULT '{}',
    usage_outcome VARCHAR(50) NOT NULL,
    usage_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effectiveness_score FLOAT DEFAULT 0.0 CHECK (effectiveness_score BETWEEN 0.0 AND 1.0),
    
    -- Usage metadata
    usage_type VARCHAR(50) DEFAULT 'query_response',
    user_feedback JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT valid_usage_outcome CHECK (usage_outcome IN (
        'successful', 'failed', 'partial', 'not_applicable', 'needs_refinement'
    )),
    CONSTRAINT valid_usage_type CHECK (usage_type IN (
        'query_response', 'proactive_suggestion', 'error_recovery', 'pattern_matching'
    ))
);

-- System Health Monitoring
CREATE TABLE IF NOT EXISTS system_health_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    component VARCHAR(50) NOT NULL,
    health_status VARCHAR(20) NOT NULL,
    metrics JSONB DEFAULT '{}',
    error_details TEXT,
    recovery_actions TEXT[],
    
    -- Constraints
    CONSTRAINT valid_health_status CHECK (health_status IN (
        'healthy', 'degraded', 'critical', 'offline', 'recovering'
    )),
    CONSTRAINT valid_component CHECK (component IN (
        'database', 'cache', 'mcp_integration', 'pattern_engine', 
        'semantic_classifier', 'context_manager', 'overall_system'
    ))
);

-- MCP Tool Registry
CREATE TABLE IF NOT EXISTS mcp_tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_name VARCHAR(100) NOT NULL UNIQUE,
    tool_schema JSONB NOT NULL,
    tool_description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Health and performance
    last_health_check TIMESTAMP,
    health_status VARCHAR(20) DEFAULT 'unknown',
    average_response_time FLOAT DEFAULT 0.0,
    success_rate FLOAT DEFAULT 0.0,
    
    -- Constraints
    CONSTRAINT valid_tool_schema CHECK (jsonb_typeof(tool_schema) = 'object'),
    CONSTRAINT valid_health_status CHECK (health_status IN (
        'healthy', 'degraded', 'critical', 'offline', 'unknown'
    ))
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_items_project_id ON knowledge_items(project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_semantic_type ON knowledge_items(semantic_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_embedding ON knowledge_items USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_full_text ON knowledge_items USING gin(full_text_search);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_active ON knowledge_items(is_active) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_patterns_project_id ON patterns(project_id);
CREATE INDEX IF NOT EXISTS idx_patterns_semantic_type ON patterns(semantic_type);
CREATE INDEX IF NOT EXISTS idx_patterns_embedding ON patterns USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_patterns_full_text ON patterns USING gin(full_text_search);
CREATE INDEX IF NOT EXISTS idx_patterns_active ON patterns(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_patterns_validation_status ON patterns(validation_status);

CREATE INDEX IF NOT EXISTS idx_pattern_relationships_source ON pattern_relationships(source_pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_relationships_target ON pattern_relationships(target_pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_relationships_type ON pattern_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_pattern_relationships_active ON pattern_relationships(is_active) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_strategic_insights_project ON strategic_insights(source_project_id);
CREATE INDEX IF NOT EXISTS idx_strategic_insights_types ON strategic_insights USING gin(applicable_project_types);
CREATE INDEX IF NOT EXISTS idx_strategic_insights_embedding ON strategic_insights USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_ai_sessions_project_id ON ai_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_start_time ON ai_sessions(start_time);

CREATE INDEX IF NOT EXISTS idx_pattern_validations_pattern_id ON pattern_validations(pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_validations_result ON pattern_validations(validation_result);
CREATE INDEX IF NOT EXISTS idx_pattern_validations_timestamp ON pattern_validations(validated_at);

CREATE INDEX IF NOT EXISTS idx_pattern_usage_pattern_id ON pattern_usage(pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_usage_session_id ON pattern_usage(session_id);
CREATE INDEX IF NOT EXISTS idx_pattern_usage_outcome ON pattern_usage(usage_outcome);
CREATE INDEX IF NOT EXISTS idx_pattern_usage_timestamp ON pattern_usage(usage_timestamp);

CREATE INDEX IF NOT EXISTS idx_system_health_component ON system_health_logs(component);
CREATE INDEX IF NOT EXISTS idx_system_health_timestamp ON system_health_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_health_status ON system_health_logs(health_status);

-- Triggers for automatic updates
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_modtime BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_knowledge_items_modtime BEFORE UPDATE ON knowledge_items FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_patterns_modtime BEFORE UPDATE ON patterns FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_pattern_relationships_modtime BEFORE UPDATE ON pattern_relationships FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_strategic_insights_modtime BEFORE UPDATE ON strategic_insights FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_mcp_tools_modtime BEFORE UPDATE ON mcp_tools FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Triggers for full-text search
CREATE OR REPLACE FUNCTION update_full_text_search()
RETURNS TRIGGER AS $$
BEGIN
    NEW.full_text_search = to_tsvector('english', 
        COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER update_knowledge_items_search BEFORE INSERT OR UPDATE ON knowledge_items 
    FOR EACH ROW EXECUTE FUNCTION update_full_text_search();

CREATE OR REPLACE FUNCTION update_pattern_full_text_search()
RETURNS TRIGGER AS $$
BEGIN
    NEW.full_text_search = to_tsvector('english', 
        COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content::text, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER update_patterns_search BEFORE INSERT OR UPDATE ON patterns 
    FOR EACH ROW EXECUTE FUNCTION update_pattern_full_text_search();

CREATE TRIGGER update_strategic_insights_search BEFORE INSERT OR UPDATE ON strategic_insights 
    FOR EACH ROW EXECUTE FUNCTION update_full_text_search();

-- Functions for pattern analysis
CREATE OR REPLACE FUNCTION get_pattern_statistics(project_uuid UUID DEFAULT NULL)
RETURNS TABLE (
    total_patterns BIGINT,
    validated_patterns BIGINT,
    active_patterns BIGINT,
    pattern_types JSONB,
    avg_confidence FLOAT,
    avg_success_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_patterns,
        COUNT(*) FILTER (WHERE validation_status = 'validated') as validated_patterns,
        COUNT(*) FILTER (WHERE is_active = true) as active_patterns,
        jsonb_object_agg(pattern_type, type_count) as pattern_types,
        AVG(confidence) as avg_confidence,
        AVG(success_rate) as avg_success_rate
    FROM (
        SELECT 
            pattern_type,
            COUNT(*) as type_count,
            confidence,
            success_rate,
            validation_status,
            is_active
        FROM patterns
        WHERE (project_uuid IS NULL OR project_id = project_uuid)
        GROUP BY pattern_type, confidence, success_rate, validation_status, is_active
    ) pattern_stats;
END;
$$ LANGUAGE plpgsql;

-- Function for semantic search
CREATE OR REPLACE FUNCTION semantic_search_knowledge(
    query_embedding VECTOR(768),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INT DEFAULT 10,
    project_uuid UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    title VARCHAR(500),
    content TEXT,
    knowledge_type VARCHAR(50),
    semantic_type VARCHAR(50),
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ki.id,
        ki.title,
        ki.content,
        ki.knowledge_type,
        ki.semantic_type,
        (1 - (ki.embedding <=> query_embedding)) as similarity_score
    FROM knowledge_items ki
    WHERE 
        ki.is_active = true
        AND (project_uuid IS NULL OR ki.project_id = project_uuid)
        AND (1 - (ki.embedding <=> query_embedding)) > similarity_threshold
    ORDER BY ki.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function for pattern search
CREATE OR REPLACE FUNCTION semantic_search_patterns(
    query_embedding VECTOR(768),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INT DEFAULT 10,
    project_uuid UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    title VARCHAR(200),
    content JSONB,
    pattern_type VARCHAR(50),
    confidence FLOAT,
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.title,
        p.content,
        p.pattern_type,
        p.confidence,
        (1 - (p.embedding <=> query_embedding)) as similarity_score
    FROM patterns p
    WHERE 
        p.is_active = true
        AND (project_uuid IS NULL OR p.project_id = project_uuid)
        AND (1 - (p.embedding <=> query_embedding)) > similarity_threshold
    ORDER BY p.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Migration function
CREATE OR REPLACE FUNCTION migrate_to_version(target_version VARCHAR(20))
RETURNS BOOLEAN AS $$
DECLARE
    current_version VARCHAR(20);
    migration_successful BOOLEAN DEFAULT FALSE;
BEGIN
    -- Get current version
    SELECT version INTO current_version 
    FROM schema_versions 
    ORDER BY applied_at DESC 
    LIMIT 1;
    
    -- Simple version comparison (in production, use proper semver)
    IF current_version = target_version THEN
        RAISE NOTICE 'Already at version %', target_version;
        RETURN TRUE;
    END IF;
    
    -- Add migration logic here
    -- For now, just log the migration attempt
    INSERT INTO schema_versions (version, description, applied_at)
    VALUES (target_version, 'Migration to ' || target_version, CURRENT_TIMESTAMP);
    
    RETURN TRUE;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Migration failed: %', SQLERRM;
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Insert initial data
INSERT INTO projects (name, display_name, description, project_type, settings)
VALUES (
    'knowledge-persistence-ai',
    'Knowledge Persistence AI - Production',
    'Production-ready AI knowledge persistence system with pattern intelligence',
    'ai',
    '{
        "ai_focus": "pattern_intelligence",
        "development_stage": "production",
        "primary_technologies": ["postgresql", "pgvector", "python", "mcp", "semantic_classification"],
        "features": ["error_recovery", "graceful_degradation", "schema_versioning", "pattern_extraction"]
    }'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    settings = EXCLUDED.settings,
    updated_at = CURRENT_TIMESTAMP;

-- Register default MCP tools
INSERT INTO mcp_tools (tool_name, tool_schema, tool_description, health_status)
VALUES 
    ('get_project_context', '{"required": ["project_id"], "optional": ["include_recent"]}', 'Get project context information', 'healthy'),
    ('get_domain_knowledge', '{"required": ["domain"], "optional": ["limit"]}', 'Get domain-specific knowledge', 'healthy'),
    ('get_experience_context', '{"required": ["query"], "optional": ["limit"]}', 'Get experience-based context', 'healthy'),
    ('get_strategic_insights', '{"required": ["query"], "optional": ["limit"]}', 'Get strategic insights', 'healthy'),
    ('get_session_context', '{"required": ["session_id"], "optional": ["limit"]}', 'Get session context', 'healthy')
ON CONFLICT (tool_name) DO UPDATE SET
    tool_schema = EXCLUDED.tool_schema,
    tool_description = EXCLUDED.tool_description,
    updated_at = CURRENT_TIMESTAMP;

-- Log successful schema deployment
INSERT INTO system_health_logs (component, health_status, metrics)
VALUES ('database', 'healthy', '{"schema_version": "2.0.0", "deployment_time": "' || CURRENT_TIMESTAMP || '"}');

COMMIT;
