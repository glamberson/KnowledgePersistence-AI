# Supabase Integration Strategy

## Why Supabase for Team Knowledge Intelligence

**Context**: Private company team tool requiring real-time collaboration, project-based access control, and reduced infrastructure overhead.

### Core Benefits for Your Use Case

1. **Real-Time Pattern Sharing**: Team members see pattern discoveries instantly
2. **Row-Level Security**: Project-based access control without complex auth logic
3. **Built-in API**: Reduces server maintenance overhead
4. **Edge Functions**: Pattern processing without managing separate services
5. **File Storage**: Code artifacts, diagrams, documentation
6. **Team Dashboard**: Built-in admin interface

## Migration Strategy

### Phase 1: Database Migration (Week 1)

**Current State**: PostgreSQL 17.5 + pgvector on pgdbsrv (192.168.10.90)
**Target State**: Supabase (PostgreSQL 15+ with pgvector)

```bash
# 1. Export current schema and data
pg_dump -h 192.168.10.90 -U postgres -d knowledge_persistence \
  --schema-only > current_schema.sql

pg_dump -h 192.168.10.90 -U postgres -d knowledge_persistence \
  --data-only --inserts > current_data.sql

# 2. Set up Supabase project
# Create new project at supabase.com
# Enable pgvector extension in SQL editor
# Import schema with modifications for RLS
```

**Enhanced Schema for Supabase**:
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Projects table with team support
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    project_type VARCHAR(50) DEFAULT 'general',
    repository_url TEXT,
    local_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}'::jsonb,
    
    -- Team ownership
    owner_id UUID REFERENCES auth.users(id),
    team_id UUID REFERENCES teams(id)
);

-- Teams table for organization
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_id UUID REFERENCES auth.users(id)
);

-- Team members with roles
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id),
    user_id UUID REFERENCES auth.users(id),
    role VARCHAR(20) DEFAULT 'member',  -- 'admin', 'member', 'viewer'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(team_id, user_id)
);

-- Enhanced patterns table
CREATE TABLE patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content JSONB NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_id UUID REFERENCES projects(id),
    created_by UUID REFERENCES auth.users(id),
    
    -- Pattern metadata
    embedding VECTOR(768),
    validation_status VARCHAR(20) DEFAULT 'pending',
    is_active BOOLEAN DEFAULT TRUE,
    tags TEXT[] DEFAULT '{}'
);

-- Row-Level Security policies
ALTER TABLE patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;

-- Patterns access policy
CREATE POLICY "Users can access patterns from their team's projects" ON patterns
    FOR ALL USING (
        project_id IN (
            SELECT p.id FROM projects p
            JOIN team_members tm ON p.team_id = tm.team_id
            WHERE tm.user_id = auth.uid()
        )
    );

-- Projects access policy
CREATE POLICY "Users can access their team's projects" ON projects
    FOR ALL USING (
        team_id IN (
            SELECT tm.team_id FROM team_members tm
            WHERE tm.user_id = auth.uid()
        )
    );
```

### Phase 2: Real-Time Pattern Sharing (Week 2)

**Real-Time Subscriptions**:
```typescript
// Frontend: Subscribe to pattern updates
const supabase = createClient(supabaseUrl, supabaseKey)

// Subscribe to new patterns in current project
const patternSubscription = supabase
  .channel('pattern-updates')
  .on('postgres_changes', 
    { 
      event: 'INSERT', 
      schema: 'public', 
      table: 'patterns',
      filter: `project_id=eq.${currentProjectId}`
    }, 
    (payload) => {
      console.log('New pattern discovered:', payload.new)
      updatePatternDisplay(payload.new)
    }
  )
  .subscribe()

// Subscribe to pattern relationships
const relationshipSubscription = supabase
  .channel('relationship-updates')
  .on('postgres_changes',
    {
      event: 'INSERT',
      schema: 'public', 
      table: 'pattern_relationships'
    },
    (payload) => {
      console.log('New relationship mapped:', payload.new)
      updateRelationshipGraph(payload.new)
    }
  )
  .subscribe()
```

**Real-Time Pattern Discovery Service**:
```python
class RealtimePatternService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.pattern_processor = PatternProcessor()
    
    async def broadcast_pattern_discovery(self, pattern_data, project_id):
        """Broadcast new pattern to team members"""
        # Store pattern in database (triggers real-time update)
        result = await self.supabase.table('patterns').insert(pattern_data)
        
        # Send notification to team members
        await self.supabase.table('notifications').insert({
            'type': 'pattern_discovered',
            'project_id': project_id,
            'pattern_id': result.data[0]['id'],
            'message': f"New {pattern_data['pattern_type']} pattern discovered",
            'created_at': datetime.now().isoformat()
        })
        
        return result
    
    async def get_live_activity_feed(self, project_id):
        """Get real-time activity feed for project"""
        return await self.supabase.table('pattern_activity') \
            .select('*') \
            .eq('project_id', project_id) \
            .order('created_at', desc=True) \
            .limit(50) \
            .execute()
```

### Phase 3: Edge Functions for Pattern Processing (Week 3)

**Deploy Pattern Processing as Edge Functions**:
```typescript
// Edge function: extract-patterns
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL') ?? '',
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
)

interface PatternExtractionRequest {
  interaction_data: any
  project_id: string
  user_id: string
  processing_preference: 'local' | 'commercial' | 'hybrid'
}

serve(async (req) => {
  try {
    const { interaction_data, project_id, user_id, processing_preference } = 
      await req.json() as PatternExtractionRequest
    
    // Check user permissions
    const { data: hasAccess } = await supabase
      .from('projects')
      .select('id')
      .eq('id', project_id)
      .single()
    
    if (!hasAccess) {
      return new Response('Unauthorized', { status: 403 })
    }
    
    // Route to appropriate processing
    const processingResult = await routePatternExtraction(
      interaction_data, 
      processing_preference
    )
    
    // Store patterns (triggers real-time updates)
    const { data: patterns, error } = await supabase
      .from('patterns')
      .insert(processingResult.patterns.map(p => ({
        ...p,
        project_id,
        created_by: user_id
      })))
    
    if (error) throw error
    
    // Store relationships
    const { data: relationships, error: relError } = await supabase
      .from('pattern_relationships')
      .insert(processingResult.relationships)
    
    if (relError) throw relError
    
    return new Response(
      JSON.stringify({ 
        success: true, 
        patterns_created: patterns.length,
        relationships_created: relationships.length,
        processing_method: processingResult.method
      }),
      { headers: { "Content-Type": "application/json" } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    )
  }
})

async function routePatternExtraction(interactionData: any, preference: string) {
  // Assess complexity and route appropriately
  const complexity = await assessInteractionComplexity(interactionData)
  
  if (preference === 'local' || (preference === 'hybrid' && complexity < 0.5)) {
    return await processWithLocalModel(interactionData)
  } else {
    return await processWithCommercialModel(interactionData)
  }
}
```

### Phase 4: Team Dashboard and Analytics (Week 4)

**Supabase Dashboard Extension**:
```sql
-- Create views for team analytics
CREATE VIEW team_pattern_analytics AS
SELECT 
    t.name as team_name,
    p.name as project_name,
    pt.pattern_type,
    COUNT(pt.id) as pattern_count,
    AVG(pt.confidence) as avg_confidence,
    AVG(pt.success_rate) as avg_success_rate,
    DATE_TRUNC('week', pt.created_at) as week_created
FROM teams t
JOIN projects p ON t.id = p.team_id
JOIN patterns pt ON p.id = pt.project_id
GROUP BY t.name, p.name, pt.pattern_type, DATE_TRUNC('week', pt.created_at)
ORDER BY week_created DESC;

-- Pattern usage analytics
CREATE VIEW pattern_usage_analytics AS
SELECT 
    pt.pattern_type,
    pt.title,
    pt.usage_count,
    pt.success_rate,
    COUNT(pu.id) as recent_usage_count,
    AVG(pu.effectiveness_score) as avg_effectiveness
FROM patterns pt
LEFT JOIN pattern_usage pu ON pt.id = pu.pattern_id
WHERE pu.usage_timestamp > NOW() - INTERVAL '30 days'
GROUP BY pt.id, pt.pattern_type, pt.title, pt.usage_count, pt.success_rate
ORDER BY recent_usage_count DESC, avg_effectiveness DESC;
```

**Team Dashboard Components**:
```typescript
// Dashboard component for team pattern insights
export function TeamPatternDashboard({ teamId }: { teamId: string }) {
  const [analytics, setAnalytics] = useState<any[]>([])
  const [realtimePatterns, setRealtimePatterns] = useState<any[]>([])
  
  useEffect(() => {
    // Load team analytics
    const loadAnalytics = async () => {
      const { data } = await supabase
        .from('team_pattern_analytics')
        .select('*')
        .eq('team_id', teamId)
      setAnalytics(data || [])
    }
    
    loadAnalytics()
    
    // Subscribe to real-time pattern updates
    const subscription = supabase
      .channel('team-patterns')
      .on('postgres_changes', 
        { 
          event: 'INSERT', 
          schema: 'public', 
          table: 'patterns',
          filter: `project_id=in.(${teamProjectIds.join(',')})`
        }, 
        (payload) => {
          setRealtimePatterns(prev => [payload.new, ...prev.slice(0, 9)])
        }
      )
      .subscribe()
    
    return () => subscription.unsubscribe()
  }, [teamId])
  
  return (
    <div className="team-dashboard">
      <div className="analytics-grid">
        <PatternTypeDistribution data={analytics} />
        <PatternQualityTrends data={analytics} />
        <TopPerformingPatterns data={analytics} />
        <TeamProductivityMetrics data={analytics} />
      </div>
      
      <div className="realtime-feed">
        <h3>Live Pattern Discoveries</h3>
        {realtimePatterns.map(pattern => (
          <PatternCard key={pattern.id} pattern={pattern} />
        ))}
      </div>
    </div>
  )
}
```

## Integration with Existing System

### Backward Compatibility

```python
class SupabasePatternManager:
    def __init__(self, supabase_client, legacy_db_config=None):
        self.supabase = supabase_client
        self.legacy_db = legacy_db_config
        self.migration_mode = legacy_db_config is not None
    
    async def store_pattern(self, pattern_data):
        """Store pattern with fallback to legacy system"""
        try:
            # Try Supabase first
            result = await self.supabase.table('patterns').insert(pattern_data)
            
            # Also store in legacy system during migration
            if self.migration_mode:
                await self.store_in_legacy_system(pattern_data)
            
            return result
        except Exception as e:
            if self.migration_mode:
                # Fallback to legacy system
                return await self.store_in_legacy_system(pattern_data)
            raise e
    
    async def search_patterns(self, query, project_id):
        """Search patterns across both systems during migration"""
        # Search Supabase
        supabase_results = await self.supabase.table('patterns') \
            .select('*') \
            .eq('project_id', project_id) \
            .ilike('title', f'%{query}%') \
            .execute()
        
        # Search legacy system during migration
        legacy_results = []
        if self.migration_mode:
            legacy_results = await self.search_legacy_system(query, project_id)
        
        # Combine and deduplicate results
        return self.combine_results(supabase_results.data, legacy_results)
```

### GitHub Integration Updates

```python
class GitHubSupabaseIntegration:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.github_client = GitHubClient()
    
    async def handle_webhook(self, webhook_data):
        """Handle GitHub webhook with Supabase storage"""
        event_type = webhook_data['action']
        
        if event_type == 'opened' and 'pull_request' in webhook_data:
            await self.handle_pull_request(webhook_data['pull_request'])
        elif event_type == 'opened' and 'issue' in webhook_data:
            await self.handle_issue(webhook_data['issue'])
    
    async def handle_pull_request(self, pr_data):
        # Extract patterns from PR
        patterns = await self.extract_pr_patterns(pr_data)
        
        # Store in Supabase (triggers real-time updates)
        for pattern in patterns:
            await self.supabase.table('patterns').insert({
                **pattern,
                'project_id': self.get_project_id_from_repo(pr_data['repository']),
                'source_type': 'github_pr',
                'source_id': pr_data['id']
            })
        
        # Generate insights and post to PR
        insights = await self.generate_pr_insights(patterns)
        if insights:
            await self.github_client.post_pr_comment(
                pr_data['number'],
                self.format_insights(insights)
            )
```

## Cost and Performance Optimization

### Supabase Pricing Considerations

**Free Tier Limits**:
- 500MB database storage
- 2GB bandwidth
- 50,000 monthly active users
- 500,000 Edge Function invocations

**Pro Tier ($25/month)**:
- 8GB database storage
- 250GB bandwidth
- 100,000 monthly active users
- 2,000,000 Edge Function invocations

**Optimization Strategies**:
```python
class SupabaseCostOptimizer:
    def __init__(self):
        self.usage_tracker = UsageTracker()
        self.optimization_rules = {
            'database_size': 0.8,  # Alert at 80% of limit
            'bandwidth_usage': 0.7,  # Alert at 70% of limit
            'edge_function_calls': 0.75  # Alert at 75% of limit
        }
    
    async def optimize_database_usage(self):
        """Optimize database storage usage"""
        # Archive old patterns
        await self.archive_old_patterns()
        
        # Compress pattern content
        await self.compress_pattern_content()
        
        # Remove duplicate patterns
        await self.deduplicate_patterns()
    
    async def optimize_bandwidth_usage(self):
        """Optimize bandwidth usage"""
        # Implement pagination for large queries
        # Use pattern caching
        # Compress API responses
        pass
    
    async def monitor_usage(self):
        """Monitor and alert on usage patterns"""
        current_usage = await self.get_current_usage()
        
        for resource, threshold in self.optimization_rules.items():
            if current_usage[resource] > threshold:
                await self.alert_high_usage(resource, current_usage[resource])
```

This Supabase integration strategy provides a comprehensive approach to transforming your PostgreSQL-based system into a real-time, team-collaborative pattern intelligence platform while maintaining cost efficiency and performance.
