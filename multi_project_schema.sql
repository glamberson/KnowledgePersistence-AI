-- Multi-Project Schema Extension for KnowledgePersistence-AI
-- Date: 2025-07-03
-- Purpose: Add multi-project support with project isolation and cross-project intelligence

-- Projects table for managing multiple projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    project_type VARCHAR(50) DEFAULT 'general', -- 'software', 'research', 'genealogy', etc.
    repository_url TEXT,
    local_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}'::jsonb
);

-- Add project_id to existing knowledge_items table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'knowledge_items' AND column_name = 'project_id') THEN
        ALTER TABLE knowledge_items 
        ADD COLUMN project_id UUID REFERENCES projects(id),
        ADD COLUMN is_cross_project BOOLEAN DEFAULT false;
    END IF;
END $$;

-- Add project_id to existing ai_sessions table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'ai_sessions' AND column_name = 'project_id') THEN
        ALTER TABLE ai_sessions 
        ADD COLUMN project_id UUID REFERENCES projects(id);
    END IF;
END $$;

-- Strategic insights table for cross-project intelligence
CREATE TABLE IF NOT EXISTS strategic_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    insight_type VARCHAR(50) NOT NULL, -- 'methodology', 'pattern', 'approach', 'lesson'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    source_project_id UUID REFERENCES projects(id),
    applicable_project_types TEXT[], -- Array of project types this applies to
    confidence_score FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    effectiveness_rating FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(1536)
);

-- Universal patterns table for cross-project learning
CREATE TABLE IF NOT EXISTS universal_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(200) NOT NULL,
    pattern_type VARCHAR(100), -- 'development', 'research', 'problem-solving', 'workflow'
    description TEXT,
    methodology TEXT,
    examples JSONB DEFAULT '{}'::jsonb, -- Examples from different projects
    success_metrics JSONB DEFAULT '{}'::jsonb,
    applicable_domains TEXT[],
    usage_frequency INTEGER DEFAULT 0,
    effectiveness_rating FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR(1536)
);

-- Project session contexts for maintaining state
CREATE TABLE IF NOT EXISTS project_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    session_id UUID REFERENCES ai_sessions(id),
    context_type VARCHAR(50), -- 'current', 'cached', 'archived'
    context_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(project_id, session_id, context_type)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_knowledge_items_project_id ON knowledge_items(project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_cross_project ON knowledge_items(is_cross_project) WHERE is_cross_project = true;
CREATE INDEX IF NOT EXISTS idx_ai_sessions_project_id ON ai_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_strategic_insights_source_project ON strategic_insights(source_project_id);
CREATE INDEX IF NOT EXISTS idx_strategic_insights_types ON strategic_insights USING GIN(applicable_project_types);
CREATE INDEX IF NOT EXISTS idx_universal_patterns_domains ON universal_patterns USING GIN(applicable_domains);
CREATE INDEX IF NOT EXISTS idx_project_contexts_project_session ON project_contexts(project_id, session_id);

-- Insert the current KnowledgePersistence-AI as the first project
INSERT INTO projects (name, display_name, description, project_type, local_path, settings)
VALUES (
    'KnowledgePersistence-AI',
    'KnowledgePersistence-AI Development',
    'Revolutionary AI knowledge persistence database system with strategic partnership capabilities',
    'software',
    '/home/greg/KnowledgePersistence-AI',
    '{"ai_focus": "strategic_partnership", "development_stage": "phase_4_complete", "primary_technologies": ["postgresql", "pgvector", "python", "mcp"]}'::jsonb
) ON CONFLICT (name) DO NOTHING;

-- Update existing knowledge items to belong to the main project
UPDATE knowledge_items 
SET project_id = (SELECT id FROM projects WHERE name = 'KnowledgePersistence-AI')
WHERE project_id IS NULL;

-- Update existing sessions to belong to the main project
UPDATE ai_sessions 
SET project_id = (SELECT id FROM projects WHERE name = 'KnowledgePersistence-AI')
WHERE project_id IS NULL;

-- Insert some initial strategic insights from the main project
INSERT INTO strategic_insights (insight_type, title, description, source_project_id, applicable_project_types, confidence_score, content)
SELECT 
    'methodology',
    'Phase-Based Development with Revolutionary Goals',
    'Break complex projects into phases with clear milestones while maintaining focus on revolutionary outcomes',
    (SELECT id FROM projects WHERE name = 'KnowledgePersistence-AI'),
    ARRAY['software', 'research', 'ai'],
    0.9,
    '{"approach": "iterative_development", "focus": "revolutionary_outcomes", "documentation": "comprehensive", "testing": "continuous"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM strategic_insights WHERE title = 'Phase-Based Development with Revolutionary Goals');

INSERT INTO strategic_insights (insight_type, title, description, source_project_id, applicable_project_types, confidence_score, content)
SELECT
    'pattern',
    'Knowledge Persistence Strategic Partnership',
    'Transform AI from replaceable tool to irreplaceable strategic partner through persistent knowledge accumulation',
    (SELECT id FROM projects WHERE name = 'KnowledgePersistence-AI'),
    ARRAY['software', 'research', 'ai', 'genealogy'],
    0.95,
    '{"goal": "strategic_partnership", "method": "knowledge_persistence", "outcome": "irreplaceable_ai_partner"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM strategic_insights WHERE title = 'Knowledge Persistence Strategic Partnership');

-- Function to get project statistics
CREATE OR REPLACE FUNCTION get_project_stats(project_name TEXT)
RETURNS TABLE (
    knowledge_items_count BIGINT,
    sessions_count BIGINT,
    strategic_insights_count BIGINT,
    last_activity TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM knowledge_items ki 
         JOIN projects p ON ki.project_id = p.id 
         WHERE p.name = project_name),
        (SELECT COUNT(*) FROM ai_sessions s 
         JOIN projects p ON s.project_id = p.id 
         WHERE p.name = project_name),
        (SELECT COUNT(*) FROM strategic_insights si 
         JOIN projects p ON si.source_project_id = p.id 
         WHERE p.name = project_name),
        (SELECT MAX(GREATEST(
            COALESCE((SELECT MAX(created_at) FROM knowledge_items ki 
                     JOIN projects p ON ki.project_id = p.id 
                     WHERE p.name = project_name), '1970-01-01'::timestamp),
            COALESCE((SELECT MAX(created_at) FROM ai_sessions s 
                     JOIN projects p ON s.project_id = p.id 
                     WHERE p.name = project_name), '1970-01-01'::timestamp)
        )));
END;
$$ LANGUAGE plpgsql;

COMMIT;