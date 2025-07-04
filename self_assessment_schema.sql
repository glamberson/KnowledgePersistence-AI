-- Self-Assessment Framework Schema for KnowledgePersistence-AI
-- Purpose: Enable AI performance measurement, reflection, and improvement
-- Created: 2025-07-04
-- Responsibility: Claude AI Assistant (self-implementation)

-- AI Self-Assessment Tracking
CREATE TABLE IF NOT EXISTS ai_self_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES ai_sessions(id),
    assessment_type VARCHAR(50) NOT NULL, -- 'context_comprehension', 'task_accuracy', 'information_quality', 'session_reflection'
    task_description TEXT,
    initial_understanding_score INTEGER CHECK (initial_understanding_score BETWEEN 0 AND 100),
    final_understanding_score INTEGER CHECK (final_understanding_score BETWEEN 0 AND 100),
    redirection_count INTEGER DEFAULT 0,
    comprehension_gaps JSONB DEFAULT '[]'::jsonb,
    improvement_actions JSONB DEFAULT '[]'::jsonb,
    reflection_notes TEXT,
    performance_score INTEGER CHECK (performance_score BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge Retrieval Performance Tracking
CREATE TABLE IF NOT EXISTS knowledge_retrieval_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES ai_sessions(id),
    query_intent TEXT NOT NULL,
    search_strategy TEXT,
    information_retrieved JSONB,
    documents_accessed TEXT[],
    relevance_score INTEGER CHECK (relevance_score BETWEEN 0 AND 100),
    completeness_score INTEGER CHECK (completeness_score BETWEEN 0 AND 100), 
    quality_score INTEGER CHECK (quality_score BETWEEN 0 AND 100),
    efficiency_score INTEGER CHECK (efficiency_score BETWEEN 0 AND 100),
    redirection_required BOOLEAN DEFAULT false,
    missing_information TEXT,
    improvement_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Learning and Improvement Tracking
CREATE TABLE IF NOT EXISTS ai_learning_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES ai_sessions(id),
    learning_event_type VARCHAR(50), -- 'correction', 'clarification', 'breakthrough', 'improvement'
    trigger_event TEXT,
    previous_understanding TEXT,
    corrected_understanding TEXT,
    learning_effectiveness INTEGER CHECK (learning_effectiveness BETWEEN 0 AND 100),
    retention_predicted BOOLEAN DEFAULT true,
    knowledge_item_created UUID REFERENCES knowledge_items(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Trends and Analysis
CREATE TABLE IF NOT EXISTS ai_performance_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date_period DATE NOT NULL,
    session_count INTEGER DEFAULT 0,
    avg_context_comprehension DECIMAL(5,2),
    avg_information_quality DECIMAL(5,2),
    avg_redirection_count DECIMAL(5,2),
    improvement_trend VARCHAR(20), -- 'improving', 'stable', 'declining'
    key_weaknesses JSONB DEFAULT '[]'::jsonb,
    key_strengths JSONB DEFAULT '[]'::jsonb,
    action_items JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_assessments_session ON ai_self_assessments(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_assessments_type ON ai_self_assessments(assessment_type);
CREATE INDEX IF NOT EXISTS idx_retrieval_assessments_session ON knowledge_retrieval_assessments(session_id);
CREATE INDEX IF NOT EXISTS idx_learning_metrics_session ON ai_learning_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_performance_trends_date ON ai_performance_trends(date_period DESC);

-- Create performance dashboard view
CREATE OR REPLACE VIEW ai_performance_dashboard AS
SELECT 
    s.session_identifier,
    s.project_context,
    s.start_time,
    COUNT(asa.id) as assessment_count,
    AVG(asa.initial_understanding_score) as avg_initial_comprehension,
    AVG(asa.final_understanding_score) as avg_final_comprehension,
    AVG(asa.final_understanding_score - asa.initial_understanding_score) as comprehension_improvement,
    SUM(asa.redirection_count) as total_redirections,
    AVG(kra.relevance_score) as avg_information_relevance,
    AVG(kra.completeness_score) as avg_information_completeness,
    AVG(kra.quality_score) as avg_information_quality,
    AVG(kra.efficiency_score) as avg_retrieval_efficiency,
    COUNT(alm.id) as learning_events_count
FROM ai_sessions s
LEFT JOIN ai_self_assessments asa ON s.id = asa.session_id
LEFT JOIN knowledge_retrieval_assessments kra ON s.id = kra.session_id
LEFT JOIN ai_learning_metrics alm ON s.id = alm.session_id
GROUP BY s.id, s.session_identifier, s.project_context, s.start_time
ORDER BY s.start_time DESC;

-- Function to automatically assess session performance
CREATE OR REPLACE FUNCTION assess_session_performance(p_session_id UUID)
RETURNS TABLE (
    overall_score INTEGER,
    comprehension_score INTEGER,
    retrieval_score INTEGER,
    efficiency_score INTEGER,
    improvement_recommendations TEXT[]
) AS $$
DECLARE
    comprehension_avg DECIMAL;
    retrieval_avg DECIMAL;
    redirection_penalty INTEGER;
    efficiency_avg DECIMAL;
    overall_calc INTEGER;
BEGIN
    -- Calculate averages
    SELECT 
        COALESCE(AVG(final_understanding_score), 0),
        COALESCE(AVG((relevance_score + completeness_score + quality_score) / 3), 0),
        COALESCE(SUM(redirection_count), 0),
        COALESCE(AVG(efficiency_score), 0)
    INTO comprehension_avg, retrieval_avg, redirection_penalty, efficiency_avg
    FROM ai_self_assessments asa
    LEFT JOIN knowledge_retrieval_assessments kra ON asa.session_id = kra.session_id
    WHERE asa.session_id = p_session_id;
    
    -- Calculate overall score with penalties
    overall_calc := GREATEST(0, 
        (comprehension_avg * 0.3 + 
         retrieval_avg * 0.3 + 
         efficiency_avg * 0.2 + 
         GREATEST(0, 100 - redirection_penalty * 10) * 0.2)::INTEGER
    );
    
    RETURN QUERY SELECT 
        overall_calc,
        comprehension_avg::INTEGER,
        retrieval_avg::INTEGER,
        efficiency_avg::INTEGER,
        ARRAY['Implement performance improvements based on assessment data']::TEXT[];
END;
$$ LANGUAGE plpgsql;

COMMIT;