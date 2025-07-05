# V2 Reference Documentation System

## Architecture: Immutable References with Analysis Overlays

**Core Principle**: Separate authoritative reference materials from adaptive knowledge stores. Reference docs remain immutable while analysis and insights are stored as overlays.

```
┌─────────────────────────────────────────────────────────────────┐
│                    V2 Knowledge Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────────────────┐  │
│  │   Reference Docs    │    │      Adaptive Knowledge        │  │
│  │   (Immutable)       │    │      (Learning System)         │  │
│  │                     │    │                                 │  │
│  │ • Python Manual     │    │ • Session Patterns             │  │
│  │ • PostgreSQL Docs   │    │ • Usage Analytics              │  │
│  │ • PM Methodologies  │    │ • Learned Insights             │  │
│  │ • Technical Specs   │    │ • Cross-references             │  │
│  │                     │    │                                 │  │
│  └─────────────────────┘    └─────────────────────────────────┘  │
│           │                                    │                 │
│           └────────────────┬───────────────────┘                 │
│                           │                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              Analysis Overlay System                        │  │
│  │                                                             │  │
│  │ • Cross-references between reference docs and patterns     │  │
│  │ • Usage frequency analysis of reference sections           │  │
│  │ • Contextual annotations and insights                      │  │
│  │ • Project-specific methodology enhancements                │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Reference Documentation Database Schema

```sql
-- Reference document collections (immutable)
CREATE TABLE reference_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    version VARCHAR(50),
    source_url TEXT,
    collection_type VARCHAR(50), -- 'manual', 'methodology', 'specification'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'
);

-- Reference documents (immutable content)
CREATE TABLE reference_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID REFERENCES reference_collections(id),
    title VARCHAR(200) NOT NULL,
    section_path VARCHAR(500), -- e.g., 'chapter_5/section_3/subsection_2'
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text', -- 'text', 'code', 'diagram'
    content_hash VARCHAR(64) NOT NULL, -- SHA256 hash for integrity
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    
    -- Full-text search
    content_tsvector tsvector GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || content)) STORED
);

-- Reference document embeddings (for semantic search)
CREATE TABLE reference_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES reference_documents(id),
    embedding VECTOR(768), -- Using 768-dim for efficiency
    embedding_model VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis overlays (mutable insights on immutable content)
CREATE TABLE reference_analysis_overlays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES reference_documents(id),
    overlay_type VARCHAR(50), -- 'usage_frequency', 'cross_reference', 'annotation', 'enhancement'
    analysis_data JSONB NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    
    -- Allow multiple overlays per document
    UNIQUE(document_id, overlay_type, created_by)
);

-- Usage tracking for reference documents
CREATE TABLE reference_usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES reference_documents(id),
    session_id UUID, -- References from main system
    usage_context JSONB,
    usage_type VARCHAR(50), -- 'search', 'direct_access', 'cross_reference'
    usage_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effectiveness_score FLOAT
);

-- Cross-references between reference docs and adaptive knowledge
CREATE TABLE knowledge_reference_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_document_id UUID REFERENCES reference_documents(id),
    knowledge_item_id UUID, -- References adaptive knowledge system
    link_type VARCHAR(50), -- 'implements', 'explains', 'contradicts', 'enhances'
    link_strength FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    validation_status VARCHAR(20) DEFAULT 'pending'
);

-- Create indexes for performance
CREATE INDEX idx_reference_documents_collection ON reference_documents(collection_id);
CREATE INDEX idx_reference_documents_path ON reference_documents(section_path);
CREATE INDEX idx_reference_documents_hash ON reference_documents(content_hash);
CREATE INDEX idx_reference_documents_fts ON reference_documents USING GIN(content_tsvector);
CREATE INDEX idx_reference_embeddings_document ON reference_embeddings(document_id);
CREATE INDEX idx_reference_usage_document ON reference_usage_tracking(document_id);
CREATE INDEX idx_reference_usage_timestamp ON reference_usage_tracking(usage_timestamp DESC);
```

## Reference Document Loader

```python
class ReferenceDocumentLoader:
    def __init__(self):
        self.embedding_model = LocalEmbedding("all-mpnet-base-v2")
        self.content_hasher = ContentHasher()
        self.document_parser = DocumentParser()
        
    async def load_python_manual(self, python_version="3.11"):
        """Load Python documentation as reference"""
        print(f"Loading Python {python_version} documentation...")
        
        # Create collection
        collection = await self.create_collection({
            'name': f'python_{python_version}_manual',
            'description': f'Python {python_version} Official Documentation',
            'version': python_version,
            'source_url': f'https://docs.python.org/{python_version}/',
            'collection_type': 'manual'
        })
        
        # Load Python documentation
        python_docs = await self.fetch_python_docs(python_version)
        
        # Process and store documents
        for doc_section in python_docs:
            await self.process_reference_document(doc_section, collection['id'])
        
        print(f"Loaded {len(python_docs)} Python documentation sections")
        return collection
    
    async def load_postgresql_manual(self, postgres_version="15"):
        """Load PostgreSQL documentation as reference"""
        print(f"Loading PostgreSQL {postgres_version} documentation...")
        
        # Create collection
        collection = await self.create_collection({
            'name': f'postgresql_{postgres_version}_manual',
            'description': f'PostgreSQL {postgres_version} Official Documentation',
            'version': postgres_version,
            'source_url': f'https://www.postgresql.org/docs/{postgres_version}/',
            'collection_type': 'manual'
        })
        
        # Load PostgreSQL documentation
        postgres_docs = await self.fetch_postgres_docs(postgres_version)
        
        # Process and store documents
        for doc_section in postgres_docs:
            await self.process_reference_document(doc_section, collection['id'])
        
        print(f"Loaded {len(postgres_docs)} PostgreSQL documentation sections")
        return collection
    
    async def load_pm_methodologies(self):
        """Load project management methodologies as reference"""
        print("Loading project management methodologies...")
        
        # Create collection
        collection = await self.create_collection({
            'name': 'pm_methodologies',
            'description': 'Project Management Methodologies and Best Practices',
            'version': '1.0',
            'collection_type': 'methodology'
        })
        
        # Load various PM methodologies
        methodologies = [
            await self.load_agile_methodology(),
            await self.load_scrum_methodology(),
            await self.load_lean_methodology(),
            await self.load_waterfall_methodology(),
            await self.load_risk_management_frameworks(),
            await self.load_quality_assurance_frameworks()
        ]
        
        # Process and store documents
        for methodology in methodologies:
            for doc_section in methodology:
                await self.process_reference_document(doc_section, collection['id'])
        
        print(f"Loaded {sum(len(m) for m in methodologies)} PM methodology sections")
        return collection
    
    async def process_reference_document(self, doc_data, collection_id):
        """Process and store a reference document"""
        # Calculate content hash for integrity
        content_hash = self.content_hasher.calculate_hash(doc_data['content'])
        
        # Check if document already exists
        existing_doc = await self.check_existing_document(content_hash)
        if existing_doc:
            print(f"Document already exists: {doc_data['title']}")
            return existing_doc
        
        # Create document record
        document = await self.create_document({
            'collection_id': collection_id,
            'title': doc_data['title'],
            'section_path': doc_data.get('section_path', ''),
            'content': doc_data['content'],
            'content_type': doc_data.get('content_type', 'text'),
            'content_hash': content_hash,
            'word_count': len(doc_data['content'].split()),
            'metadata': doc_data.get('metadata', {})
        })
        
        # Generate and store embedding
        embedding = await self.embedding_model.encode(
            f"{doc_data['title']} {doc_data['content']}"
        )
        
        await self.store_embedding({
            'document_id': document['id'],
            'embedding': embedding,
            'embedding_model': 'all-mpnet-base-v2'
        })
        
        return document
    
    async def fetch_python_docs(self, version):
        """Fetch Python documentation from official source"""
        # Implementation would scrape or use API to get Python docs
        # For now, return mock structure
        return [
            {
                'title': 'Built-in Functions',
                'section_path': 'library/functions',
                'content': 'Documentation for Python built-in functions...',
                'content_type': 'text',
                'metadata': {'category': 'library', 'importance': 'high'}
            },
            {
                'title': 'Data Structures',
                'section_path': 'tutorial/datastructures',
                'content': 'Documentation for Python data structures...',
                'content_type': 'text',
                'metadata': {'category': 'tutorial', 'importance': 'high'}
            }
            # ... more sections
        ]
    
    async def fetch_postgres_docs(self, version):
        """Fetch PostgreSQL documentation from official source"""
        # Implementation would scrape or use API to get PostgreSQL docs
        return [
            {
                'title': 'SQL Commands',
                'section_path': 'sql-commands',
                'content': 'Documentation for PostgreSQL SQL commands...',
                'content_type': 'text',
                'metadata': {'category': 'reference', 'importance': 'high'}
            },
            {
                'title': 'Data Types',
                'section_path': 'datatype',
                'content': 'Documentation for PostgreSQL data types...',
                'content_type': 'text',
                'metadata': {'category': 'reference', 'importance': 'high'}
            }
            # ... more sections
        ]
    
    async def load_agile_methodology(self):
        """Load Agile methodology documentation"""
        return [
            {
                'title': 'Agile Principles',
                'section_path': 'agile/principles',
                'content': '''The Agile Manifesto outlines four key values:
                1. Individuals and interactions over processes and tools
                2. Working software over comprehensive documentation
                3. Customer collaboration over contract negotiation
                4. Responding to change over following a plan''',
                'content_type': 'text',
                'metadata': {'methodology': 'agile', 'importance': 'high'}
            },
            {
                'title': 'User Stories',
                'section_path': 'agile/user_stories',
                'content': '''User stories are short, simple descriptions of features told from the user's perspective.
                Format: "As a [type of user], I want [some goal] so that [some reason]"''',
                'content_type': 'text',
                'metadata': {'methodology': 'agile', 'importance': 'medium'}
            }
            # ... more agile concepts
        ]
```

## Reference Search and Integration Engine

```python
class ReferenceSearchEngine:
    def __init__(self):
        self.embedding_model = LocalEmbedding("all-mpnet-base-v2")
        self.usage_tracker = UsageTracker()
        self.cross_reference_engine = CrossReferenceEngine()
        
    async def search_references(self, query, context=None, limit=10):
        """Search reference documents with context awareness"""
        
        # Generate query embedding
        query_embedding = await self.embedding_model.encode(query)
        
        # Multi-modal search
        search_results = await self.execute_multi_modal_search(
            query, query_embedding, context, limit
        )
        
        # Rank results based on context and usage patterns
        ranked_results = await self.rank_search_results(
            search_results, query, context
        )
        
        # Track usage
        await self.usage_tracker.track_reference_search(
            query, context, ranked_results
        )
        
        return ranked_results
    
    async def execute_multi_modal_search(self, query, query_embedding, context, limit):
        """Execute search across multiple modalities"""
        
        # Semantic search using embeddings
        semantic_results = await self.semantic_search(query_embedding, limit)
        
        # Full-text search
        fts_results = await self.full_text_search(query, limit)
        
        # Context-aware search
        context_results = await self.context_aware_search(query, context, limit)
        
        # Combine and deduplicate results
        combined_results = await self.combine_search_results(
            semantic_results, fts_results, context_results
        )
        
        return combined_results
    
    async def semantic_search(self, query_embedding, limit):
        """Semantic search using vector similarity"""
        async with self.get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT 
                        rd.id,
                        rd.title,
                        rd.section_path,
                        rd.content,
                        rc.name as collection_name,
                        re.embedding <-> %s as similarity_score
                    FROM reference_documents rd
                    JOIN reference_collections rc ON rd.collection_id = rc.id
                    JOIN reference_embeddings re ON rd.id = re.document_id
                    WHERE rc.is_active = TRUE
                    ORDER BY re.embedding <-> %s
                    LIMIT %s
                """, (query_embedding, query_embedding, limit))
                
                return await cur.fetchall()
    
    async def full_text_search(self, query, limit):
        """Full-text search using PostgreSQL FTS"""
        async with self.get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT 
                        rd.id,
                        rd.title,
                        rd.section_path,
                        rd.content,
                        rc.name as collection_name,
                        ts_rank(rd.content_tsvector, plainto_tsquery('english', %s)) as rank_score
                    FROM reference_documents rd
                    JOIN reference_collections rc ON rd.collection_id = rc.id
                    WHERE rc.is_active = TRUE
                      AND rd.content_tsvector @@ plainto_tsquery('english', %s)
                    ORDER BY ts_rank(rd.content_tsvector, plainto_tsquery('english', %s)) DESC
                    LIMIT %s
                """, (query, query, query, limit))
                
                return await cur.fetchall()
    
    async def context_aware_search(self, query, context, limit):
        """Context-aware search based on current session context"""
        if not context:
            return []
        
        # Determine relevant collections based on context
        relevant_collections = await self.determine_relevant_collections(context)
        
        if not relevant_collections:
            return []
        
        # Search within relevant collections
        async with self.get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT 
                        rd.id,
                        rd.title,
                        rd.section_path,
                        rd.content,
                        rc.name as collection_name,
                        'context_match' as score_type
                    FROM reference_documents rd
                    JOIN reference_collections rc ON rd.collection_id = rc.id
                    WHERE rc.is_active = TRUE
                      AND rc.name = ANY(%s)
                      AND (rd.content_tsvector @@ plainto_tsquery('english', %s)
                           OR rd.title ILIKE %s)
                    ORDER BY rd.word_count DESC
                    LIMIT %s
                """, (relevant_collections, query, f'%{query}%', limit))
                
                return await cur.fetchall()
    
    async def determine_relevant_collections(self, context):
        """Determine which reference collections are relevant to current context"""
        relevant_collections = []
        
        # Check for coding context
        if context.get('coding_focus', 0) > 0.5:
            relevant_collections.extend(['python_3.11_manual', 'postgresql_15_manual'])
        
        # Check for project management context
        if context.get('domain_classification', {}).get('primary') == 'project_management':
            relevant_collections.append('pm_methodologies')
        
        # Check for specific technology mentions
        if 'python' in context.get('keywords', []):
            relevant_collections.append('python_3.11_manual')
        
        if 'postgresql' in context.get('keywords', []) or 'postgres' in context.get('keywords', []):
            relevant_collections.append('postgresql_15_manual')
        
        return relevant_collections
```

## Analysis Overlay System

```python
class AnalysisOverlayEngine:
    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.usage_analyzer = UsageAnalyzer()
        self.cross_reference_analyzer = CrossReferenceAnalyzer()
        
    async def generate_usage_frequency_overlay(self, document_id):
        """Generate usage frequency analysis overlay"""
        
        # Get usage data for document
        usage_data = await self.get_document_usage_data(document_id)
        
        # Analyze usage patterns
        usage_analysis = {
            'total_accesses': len(usage_data),
            'unique_sessions': len(set(u['session_id'] for u in usage_data)),
            'average_effectiveness': sum(u['effectiveness_score'] for u in usage_data) / len(usage_data),
            'usage_over_time': await self.analyze_usage_over_time(usage_data),
            'context_patterns': await self.analyze_usage_contexts(usage_data),
            'peak_usage_times': await self.identify_peak_usage_times(usage_data)
        }
        
        # Store overlay
        await self.store_analysis_overlay(document_id, 'usage_frequency', usage_analysis)
        
        return usage_analysis
    
    async def generate_cross_reference_overlay(self, document_id):
        """Generate cross-reference analysis overlay"""
        
        # Find related adaptive knowledge
        related_knowledge = await self.find_related_adaptive_knowledge(document_id)
        
        # Find related reference documents
        related_docs = await self.find_related_reference_documents(document_id)
        
        # Analyze cross-references
        cross_reference_analysis = {
            'adaptive_knowledge_links': related_knowledge,
            'reference_document_links': related_docs,
            'concept_overlap': await self.analyze_concept_overlap(document_id),
            'implementation_examples': await self.find_implementation_examples(document_id),
            'contradiction_alerts': await self.detect_contradictions(document_id)
        }
        
        # Store overlay
        await self.store_analysis_overlay(document_id, 'cross_reference', cross_reference_analysis)
        
        return cross_reference_analysis
    
    async def generate_enhancement_overlay(self, document_id):
        """Generate enhancement suggestions overlay"""
        
        # Get document content
        document = await self.get_document(document_id)
        
        # Analyze for enhancement opportunities
        enhancement_analysis = {
            'practical_examples': await self.suggest_practical_examples(document),
            'common_pitfalls': await self.identify_common_pitfalls(document),
            'best_practices': await self.extract_best_practices(document),
            'related_tools': await self.identify_related_tools(document),
            'update_suggestions': await self.suggest_updates(document)
        }
        
        # Store overlay
        await self.store_analysis_overlay(document_id, 'enhancement', enhancement_analysis)
        
        return enhancement_analysis
    
    async def suggest_practical_examples(self, document):
        """Suggest practical examples based on document content"""
        # Analyze document content to suggest practical examples
        # This would use the adaptive knowledge system to find real-world usage
        examples = await self.find_practical_examples_from_sessions(document)
        
        return {
            'code_examples': examples.get('code_examples', []),
            'use_cases': examples.get('use_cases', []),
            'common_scenarios': examples.get('common_scenarios', [])
        }
    
    async def identify_common_pitfalls(self, document):
        """Identify common pitfalls related to document content"""
        # Analyze session data to find common errors or issues
        pitfalls = await self.analyze_error_patterns_for_document(document)
        
        return {
            'common_errors': pitfalls.get('common_errors', []),
            'gotchas': pitfalls.get('gotchas', []),
            'performance_issues': pitfalls.get('performance_issues', [])
        }
```

## Integration with Adaptive System

```python
class ReferenceIntegrationEngine:
    def __init__(self):
        self.reference_search = ReferenceSearchEngine()
        self.overlay_engine = AnalysisOverlayEngine()
        self.adaptive_connector = AdaptiveKnowledgeConnector()
        
    async def enhance_adaptive_response(self, user_query, adaptive_response, context):
        """Enhance adaptive response with reference documentation"""
        
        # Search for relevant reference materials
        relevant_references = await self.reference_search.search_references(
            user_query, context, limit=5
        )
        
        # Get analysis overlays for relevant references
        enhanced_references = []
        for ref in relevant_references:
            overlays = await self.overlay_engine.get_all_overlays(ref['id'])
            enhanced_references.append({
                'reference': ref,
                'overlays': overlays
            })
        
        # Integrate references into response
        enhanced_response = await self.integrate_references_into_response(
            adaptive_response, enhanced_references
        )
        
        # Create cross-links between adaptive knowledge and references
        await self.create_cross_links(
            adaptive_response, enhanced_references, context
        )
        
        return enhanced_response
    
    async def integrate_references_into_response(self, adaptive_response, references):
        """Integrate reference materials into adaptive response"""
        
        if not references:
            return adaptive_response
        
        # Add reference section to response
        reference_section = {
            'type': 'reference_materials',
            'references': [],
            'cross_references': []
        }
        
        for ref_data in references:
            reference_info = {
                'title': ref_data['reference']['title'],
                'section': ref_data['reference']['section_path'],
                'collection': ref_data['reference']['collection_name'],
                'relevance_score': ref_data['reference'].get('similarity_score', 0),
                'excerpt': ref_data['reference']['content'][:200] + '...',
                'analysis_insights': self.extract_overlay_insights(ref_data['overlays'])
            }
            
            reference_section['references'].append(reference_info)
        
        # Enhanced response with references
        enhanced_response = {
            'adaptive_response': adaptive_response,
            'reference_materials': reference_section,
            'integration_metadata': {
                'reference_count': len(references),
                'enhancement_type': 'reference_integration',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return enhanced_response
```

This reference documentation system provides:

1. **Immutable Reference Storage**: Python/PostgreSQL manuals and PM methodologies stored as authoritative sources
2. **Analysis Overlays**: Mutable insights and annotations without corrupting source materials
3. **Cross-Reference Engine**: Links between reference docs and your adaptive knowledge
4. **Usage Tracking**: Analytics on how reference materials are used
5. **Context-Aware Search**: Intelligent retrieval based on current session context
6. **Enhancement Suggestions**: AI-generated improvements based on usage patterns

The system keeps your reference materials pristine while building rich analytical overlays that enhance their value through your usage patterns.

