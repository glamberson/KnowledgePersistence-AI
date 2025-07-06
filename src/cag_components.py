#!/usr/bin/env python3
"""
Missing CAG Components - Context Manager and Cache Warmer
Complete implementation of the missing components referenced in the original code
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import psycopg
from psycopg.rows import dict_row
import numpy as np
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeType(Enum):
    """Knowledge type enumeration"""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    CONTEXTUAL = "contextual"
    RELATIONAL = "relational"
    EXPERIENTIAL = "experiential"
    TECHNICAL_DISCOVERY = "technical"
    PATTERN_RECOGNITION = "patterns"
    STRATEGIC_INSIGHT = "strategic"

class ContextLayer(Enum):
    """Context layer enumeration with priorities"""
    SYSTEM = "system"
    PROJECT = "project"
    SESSION = "session"
    DOMAIN = "domain"
    EXPERIENCE = "experience"
    STRATEGIC = "strategic"
    DYNAMIC = "dynamic"
    RESPONSE = "response"

@dataclass
class KnowledgeItem:
    """Knowledge item data structure"""
    id: str
    title: str
    content: str
    knowledge_type: KnowledgeType
    semantic_type: Optional[str] = None
    importance_score: int = 50
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    embedding: Optional[np.ndarray] = None
    usage_count: int = 0
    success_rate: float = 0.0

@dataclass
class CacheItem:
    """Cache item with metadata"""
    knowledge_item: KnowledgeItem
    cache_priority: float
    cache_layer: str
    loaded_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None

class CAGContextManager:
    """Context manager for CAG system with intelligent context assembly"""
    
    def __init__(self, max_tokens: int = 128000, db_config: Dict[str, Any] = None):
        self.max_tokens = max_tokens
        self.db_config = db_config or {}
        self.embedding_model = None
        self.context_cache = {}
        self.context_templates = {}
        
        # Context layer token allocations
        self.layer_allocations = {
            ContextLayer.SYSTEM: 2000,
            ContextLayer.PROJECT: 8000,
            ContextLayer.SESSION: 16000,
            ContextLayer.DOMAIN: 32000,
            ContextLayer.EXPERIENCE: 24000,
            ContextLayer.STRATEGIC: 16000,
            ContextLayer.DYNAMIC: 24000,
            ContextLayer.RESPONSE: 6000
        }
        
        # Initialize embedding model
        self._initialize_embedding_model()
    
    def _initialize_embedding_model(self):
        """Initialize embedding model for semantic search"""
        try:
            # Mock embedding model - in production, use sentence-transformers
            self.embedding_model = "mock_embedding_model"
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.embedding_model = None
    
    async def get_connection(self):
        """Get database connection"""
        if not self.db_config:
            raise ValueError("Database configuration not provided")
        
        return await psycopg.AsyncConnection.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            row_factory=dict_row
        )
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        if not text:
            return 0
        return int(len(text.split()) * 1.3)  # Approximate tokens
    
    def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text"""
        if not self.embedding_model:
            return None
        
        try:
            # Mock embedding generation - in production, use actual model
            embedding = np.random.random(768).astype(np.float32)
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    async def load_context_for_query(self, query: str, session_id: str) -> str:
        """Load optimal context for query"""
        # Generate query embedding for semantic search
        query_embedding = self._generate_embedding(query)
        
        # Load all context layers
        context_layers = {}
        
        # System context (always loaded)
        context_layers[ContextLayer.SYSTEM] = await self._load_system_context()
        
        # Project context
        context_layers[ContextLayer.PROJECT] = await self._load_project_context(query)
        
        # Session context
        context_layers[ContextLayer.SESSION] = await self._load_session_context(session_id)
        
        # Domain context (semantic search)
        context_layers[ContextLayer.DOMAIN] = await self._load_domain_context(
            query, query_embedding
        )
        
        # Experience context
        context_layers[ContextLayer.EXPERIENCE] = await self._load_experience_context(
            query, query_embedding
        )
        
        # Strategic context
        context_layers[ContextLayer.STRATEGIC] = await self._load_strategic_context(
            query, query_embedding
        )
        
        # Dynamic context (additional relevant content)
        context_layers[ContextLayer.DYNAMIC] = await self._load_dynamic_context(
            query, query_embedding, context_layers
        )
        
        # Compile context with token management
        return self._compile_context(context_layers)
    
    async def _load_system_context(self) -> str:
        """Load system context"""
        system_context = """
        CAG System - Cache-Augmented Generation
        - Pattern Intelligence Architecture
        - Semantic Knowledge Classification
        - Context-Aware Knowledge Retrieval
        - Multi-layer Context Management
        - Error Recovery and Graceful Degradation
        
        Current Session: Knowledge Persistence AI System
        Capabilities: Pattern extraction, semantic search, strategic insights
        """
        return system_context.strip()
    
    async def _load_project_context(self, query: str) -> str:
        """Load project-specific context"""
        try:
            if not self.db_config:
                return "Project context unavailable - no database configuration"
            
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                # Get project information
                await cur.execute("""
                    SELECT name, display_name, description, settings
                    FROM projects
                    WHERE name = 'knowledge-persistence-ai'
                    OR name = 'KnowledgePersistence-AI'
                    LIMIT 1
                """)
                project = await cur.fetchone()
                
                if project:
                    context = f"""
                    Project: {project['display_name']}
                    Description: {project['description']}
                    Settings: {json.dumps(project['settings'], indent=2)}
                    """
                    
                    # Get recent project activity
                    await cur.execute("""
                        SELECT title, content, knowledge_type, created_at
                        FROM knowledge_items
                        WHERE project_id = (
                            SELECT id FROM projects WHERE name = %s
                        )
                        ORDER BY created_at DESC
                        LIMIT 3
                    """, (project['name'],))
                    
                    recent_items = await cur.fetchall()
                    if recent_items:
                        context += "\n\nRecent Project Activity:\n"
                        for item in recent_items:
                            context += f"- [{item['knowledge_type']}] {item['title']}\n"
                    
                    await conn.close()
                    return context.strip()
                else:
                    await conn.close()
                    return "Project context not available"
                    
        except Exception as e:
            logger.error(f"Error loading project context: {e}")
            return "Project context unavailable due to error"
    
    async def _load_session_context(self, session_id: str) -> str:
        """Load session-specific context"""
        try:
            if not self.db_config:
                return f"Session context unavailable - no database configuration: {session_id}"
            
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                # Get session information
                await cur.execute("""
                    SELECT session_identifier, start_time, total_interactions,
                           user_context, session_metadata
                    FROM ai_sessions
                    WHERE id = %s OR session_identifier = %s
                    ORDER BY start_time DESC
                    LIMIT 1
                """, (session_id, session_id))
                
                session = await cur.fetchone()
                
                if session:
                    context = f"""
                    Session: {session['session_identifier']}
                    Started: {session['start_time']}
                    Interactions: {session['total_interactions']}
                    """
                    
                    # Get recent session knowledge
                    await cur.execute("""
                        SELECT title, content, knowledge_type, created_at
                        FROM knowledge_items
                        WHERE session_id = (
                            SELECT id FROM ai_sessions WHERE session_identifier = %s
                        )
                        ORDER BY created_at DESC
                        LIMIT 5
                    """, (session['session_identifier'],))
                    
                    recent_items = await cur.fetchall()
                    if recent_items:
                        context += "\n\nRecent Session Knowledge:\n"
                        for item in recent_items:
                            context += f"- {item['title'][:100]}...\n"
                    
                    await conn.close()
                    return context.strip()
                else:
                    await conn.close()
                    return f"New session: {session_id}"
                    
        except Exception as e:
            logger.error(f"Error loading session context: {e}")
            return f"Session context unavailable: {session_id}"
    
    async def _load_domain_context(self, query: str, query_embedding: Optional[np.ndarray]) -> str:
        """Load domain-specific context using semantic search"""
        try:
            if not self.db_config:
                return "Domain context unavailable - no database configuration"
            
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                # Fall back to full-text search
                await cur.execute("""
                    SELECT title, content, knowledge_type, importance_score,
                           ts_rank(full_text_search, plainto_tsquery('english', %s)) as rank
                    FROM knowledge_items
                    WHERE full_text_search @@ plainto_tsquery('english', %s)
                    AND is_active = true
                    ORDER BY rank DESC, importance_score DESC
                    LIMIT 10
                """, (query, query))
                
                items = await cur.fetchall()
                
                if items:
                    context = "Domain Knowledge:\n"
                    for item in items:
                        context += f"- [{item['knowledge_type']}] {item['title']}\n"
                        context += f"  {item['content'][:150]}...\n"
                    
                    await conn.close()
                    return context.strip()
                else:
                    await conn.close()
                    return "No relevant domain knowledge found"
                    
        except Exception as e:
            logger.error(f"Error loading domain context: {e}")
            return "Domain context unavailable due to error"
    
    async def _load_experience_context(self, query: str, query_embedding: Optional[np.ndarray]) -> str:
        """Load experience-based context"""
        try:
            if not self.db_config:
                return "Experience context unavailable - no database configuration"
            
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT title, content, created_at, importance_score
                    FROM knowledge_items
                    WHERE knowledge_type = 'experiential'
                    AND is_active = true
                    AND (title ILIKE %s OR content ILIKE %s)
                    ORDER BY importance_score DESC, created_at DESC
                    LIMIT 5
                """, (f'%{query}%', f'%{query}%'))
                
                items = await cur.fetchall()
                
                if items:
                    context = "Experience Context:\n"
                    for item in items:
                        context += f"- {item['title']}\n"
                        context += f"  {item['content'][:100]}...\n"
                    
                    await conn.close()
                    return context.strip()
                else:
                    await conn.close()
                    return "No relevant experience found"
                    
        except Exception as e:
            logger.error(f"Error loading experience context: {e}")
            return "Experience context unavailable"
    
    async def _load_strategic_context(self, query: str, query_embedding: Optional[np.ndarray]) -> str:
        """Load strategic insights context"""
        try:
            if not self.db_config:
                return "Strategic context unavailable - no database configuration"
            
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT title, description, insight_type, confidence_score
                    FROM strategic_insights
                    WHERE is_active = true
                    AND (title ILIKE %s OR description ILIKE %s)
                    ORDER BY confidence_score DESC, created_at DESC
                    LIMIT 5
                """, (f'%{query}%', f'%{query}%'))
                
                items = await cur.fetchall()
                
                if items:
                    context = "Strategic Insights:\n"
                    for item in items:
                        context += f"- [{item['insight_type']}] {item['title']}\n"
                        context += f"  {item['description'][:100]}...\n"
                    
                    await conn.close()
                    return context.strip()
                else:
                    await conn.close()
                    return "No strategic insights found"
                    
        except Exception as e:
            logger.error(f"Error loading strategic context: {e}")
            return "Strategic context unavailable"
    
    async def _load_dynamic_context(self, query: str, query_embedding: Optional[np.ndarray], 
                                  existing_context: Dict[ContextLayer, str]) -> str:
        """Load additional dynamic context based on remaining token budget"""
        # Calculate remaining tokens
        used_tokens = sum(
            self.count_tokens(content) for content in existing_context.values()
        )
        remaining_tokens = self.max_tokens - used_tokens
        
        if remaining_tokens < 1000:
            return "Dynamic context: Token budget exhausted"
        
        try:
            if not self.db_config:
                return "Dynamic context unavailable - no database configuration"
            
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                # Get additional relevant content
                await cur.execute("""
                    SELECT title, content, knowledge_type, created_at
                    FROM knowledge_items
                    WHERE is_active = true
                    AND (title ILIKE %s OR content ILIKE %s)
                    AND knowledge_type IN ('procedural', 'technical', 'patterns')
                    ORDER BY created_at DESC
                    LIMIT 3
                """, (f'%{query}%', f'%{query}%'))
                
                items = await cur.fetchall()
                
                if items:
                    context = "Additional Context:\n"
                    for item in items:
                        item_content = f"- [{item['knowledge_type']}] {item['title']}\n"
                        item_content += f"  {item['content'][:100]}...\n"
                        
                        # Check if we have token budget for this item
                        if self.count_tokens(context + item_content) > remaining_tokens:
                            break
                        
                        context += item_content
                    
                    await conn.close()
                    return context.strip()
                else:
                    await conn.close()
                    return "No additional context found"
                    
        except Exception as e:
            logger.error(f"Error loading dynamic context: {e}")
            return "Dynamic context unavailable"
    
    def _compile_context(self, context_layers: Dict[ContextLayer, str]) -> str:
        """Compile context layers into final context string"""
        compiled_context = []
        
        for layer in ContextLayer:
            if layer in context_layers and context_layers[layer]:
                compiled_context.append(f"=== {layer.value.upper()} CONTEXT ===")
                compiled_context.append(context_layers[layer])
                compiled_context.append("")
        
        return "\n".join(compiled_context)

class CacheWarmingEngine:
    """Cache warming engine for proactive knowledge loading"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.warm_cache: Dict[str, CacheItem] = {}
        self.cache_stats = {
            'total_items': 0,
            'cache_layers': {},
            'average_priority': 0.0,
            'memory_usage_estimate': 0,
            'last_warming': None
        }
        self.embedding_model = None
        self._initialize_embedding_model()
    
    def _initialize_embedding_model(self):
        """Initialize embedding model"""
        try:
            # Mock embedding model - in production, use sentence-transformers
            self.embedding_model = "mock_embedding_model"
            logger.info("Cache warming embedding model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model for cache: {e}")
            self.embedding_model = None
    
    async def get_connection(self):
        """Get database connection"""
        return await psycopg.AsyncConnection.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            row_factory=dict_row
        )
    
    def calculate_cache_priority(self, item: Dict[str, Any]) -> float:
        """Calculate cache priority for a knowledge item"""
        priority = 0.0
        
        # Base importance score (0-1)
        importance = item.get('importance_score', 50) / 100
        priority += importance * 0.3
        
        # Knowledge type weighting
        type_weights = {
            'procedural': 0.9,
            'technical': 0.8,
            'experiential': 0.7,
            'strategic': 0.85,
            'contextual': 0.6,
            'patterns': 0.8,
            'factual': 0.5,
            'relational': 0.4
        }
        
        knowledge_type = item.get('knowledge_type', 'factual')
        type_weight = type_weights.get(knowledge_type, 0.5)
        priority += type_weight * 0.3
        
        # Usage frequency
        usage_count = item.get('usage_count', 0)
        usage_factor = min(usage_count / 10, 1.0)  # Cap at 10 uses
        priority += usage_factor * 0.2
        
        # Recency factor
        created_at = item.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            days_old = (datetime.now() - created_at.replace(tzinfo=None)).days
            recency_factor = max(0, 1 - (days_old / 30))  # Decay over 30 days
            priority += recency_factor * 0.2
        
        return min(1.0, priority)
    
    def determine_cache_layer(self, item: Dict[str, Any]) -> str:
        """Determine appropriate cache layer for item"""
        knowledge_type = item.get('knowledge_type', 'factual')
        importance = item.get('importance_score', 50)
        
        if importance > 80:
            return 'strategic'
        elif knowledge_type in ['procedural', 'technical']:
            return 'domain'
        elif knowledge_type == 'experiential':
            return 'experience'
        elif knowledge_type == 'contextual':
            return 'session'
        elif knowledge_type == 'patterns':
            return 'dynamic'
        else:
            return 'response'
    
    async def warm_cache_for_session(self, session_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Warm cache for a specific session"""
        warming_start = time.time()
        
        if user_context is None:
            user_context = {
                'keywords': ['knowledge', 'intelligence', 'pattern'],
                'project': 'knowledge-persistence-ai'
            }
        
        cache_stats = {
            'phases_completed': 0,
            'items_loaded': 0,
            'cache_size': 0,
            'warming_time': 0,
            'session_id': session_id
        }
        
        try:
            # Phase 1: Load core knowledge
            logger.info("Phase 1: Loading core knowledge...")
            core_items = await self._load_core_knowledge()
            self.preload_to_context(core_items)
            cache_stats['phases_completed'] += 1
            cache_stats['items_loaded'] += len(core_items)
            
            # Phase 2: Load session-specific knowledge
            logger.info("Phase 2: Loading session-specific knowledge...")
            session_items = await self._load_session_knowledge(session_id, user_context)
            self.preload_to_context(session_items)
            cache_stats['phases_completed'] += 1
            cache_stats['items_loaded'] += len(session_items)
            
            # Phase 3: Load predictive knowledge
            logger.info("Phase 3: Loading predictive knowledge...")
            predictive_items = await self._load_predictive_knowledge(user_context)
            self.preload_to_context(predictive_items)
            cache_stats['phases_completed'] += 1
            cache_stats['items_loaded'] += len(predictive_items)
            
            # Update cache statistics
            cache_stats['cache_size'] = len(self.warm_cache)
            cache_stats['warming_time'] = time.time() - warming_start
            
            self._update_cache_stats()
            
            logger.info(f"Cache warming completed: {cache_stats['items_loaded']} items in {cache_stats['warming_time']:.2f}s")
            return cache_stats
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            cache_stats['error'] = str(e)
            cache_stats['warming_time'] = time.time() - warming_start
            return cache_stats
    
    async def _load_core_knowledge(self) -> List[Dict[str, Any]]:
        """Load core knowledge items for caching"""
        try:
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT id, title, content, knowledge_type, semantic_type,
                           importance_score, usage_count, created_at
                    FROM knowledge_items
                    WHERE importance_score > 70
                    AND is_active = true
                    ORDER BY importance_score DESC, usage_count DESC
                    LIMIT 20
                """)
                
                items = await cur.fetchall()
                await conn.close()
                
                return [dict(item) for item in items]
                
        except Exception as e:
            logger.error(f"Error loading core knowledge: {e}")
            return []
    
    async def _load_session_knowledge(self, session_id: str, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Load session-specific knowledge"""
        try:
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                # Get knowledge from this session
                await cur.execute("""
                    SELECT ki.id, ki.title, ki.content, ki.knowledge_type, 
                           ki.semantic_type, ki.importance_score, ki.usage_count, ki.created_at
                    FROM knowledge_items ki
                    JOIN ai_sessions s ON ki.session_id = s.id
                    WHERE s.session_identifier = %s
                    AND ki.is_active = true
                    ORDER BY ki.created_at DESC
                    LIMIT 15
                """, (session_id,))
                
                session_items = await cur.fetchall()
                
                # Get knowledge related to user context keywords
                keywords = user_context.get('keywords', [])
                if keywords:
                    keyword_query = ' | '.join(keywords)
                    await cur.execute("""
                        SELECT id, title, content, knowledge_type, semantic_type,
                               importance_score, usage_count, created_at
                        FROM knowledge_items
                        WHERE full_text_search @@ plainto_tsquery('english', %s)
                        AND is_active = true
                        ORDER BY ts_rank(full_text_search, plainto_tsquery('english', %s)) DESC
                        LIMIT 10
                    """, (keyword_query, keyword_query))
                    
                    keyword_items = await cur.fetchall()
                    session_items.extend(keyword_items)
                
                await conn.close()
                
                return [dict(item) for item in session_items]
                
        except Exception as e:
            logger.error(f"Error loading session knowledge: {e}")
            return []
    
    async def _load_predictive_knowledge(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Load predictive knowledge based on patterns"""
        try:
            conn = await self.get_connection()
            async with conn.cursor() as cur:
                # Get recently successful patterns
                await cur.execute("""
                    SELECT ki.id, ki.title, ki.content, ki.knowledge_type, 
                           ki.semantic_type, ki.importance_score, ki.usage_count, ki.created_at
                    FROM knowledge_items ki
                    WHERE ki.knowledge_type IN ('patterns', 'procedural', 'strategic')
                    AND ki.usage_count > 3
                    AND ki.is_active = true
                    ORDER BY ki.usage_count DESC, ki.created_at DESC
                    LIMIT 12
                """)
                
                items = await cur.fetchall()
                await conn.close()
                
                return [dict(item) for item in items]
                
        except Exception as e:
            logger.error(f"Error loading predictive knowledge: {e}")
            return []
    
    def preload_to_context(self, knowledge_items: List[Dict[str, Any]]):
        """Preload knowledge items to cache"""
        for item in knowledge_items:
            # Calculate cache priority
            cache_priority = self.calculate_cache_priority(item)
            
            # Determine cache layer
            cache_layer = self.determine_cache_layer(item)
            
            # Create KnowledgeItem
            knowledge_item = KnowledgeItem(
                id=item['id'],
                title=item['title'],
                content=item['content'],
                knowledge_type=KnowledgeType(item['knowledge_type']),
                semantic_type=item.get('semantic_type'),
                importance_score=item.get('importance_score', 50),
                usage_count=item.get('usage_count', 0),
                created_at=item.get('created_at', datetime.now())
            )
            
            # Create cache item
            cache_item = CacheItem(
                knowledge_item=knowledge_item,
                cache_priority=cache_priority,
                cache_layer=cache_layer
            )
            
            # Store in cache
            cache_key = f"{cache_layer}:{item['id']}"
            self.warm_cache[cache_key] = cache_item
    
    def get_cached_knowledge(self, layer: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get cached knowledge items, optionally filtered by layer"""
        if layer:
            items = [
                {
                    'id': item.knowledge_item.id,
                    'title': item.knowledge_item.title,
                    'content': item.knowledge_item.content,
                    'knowledge_type': item.knowledge_item.knowledge_type.value,
                    'cache_priority': item.cache_priority,
                    'cache_layer': item.cache_layer,
                    'access_count': item.access_count
                }
                for key, item in self.warm_cache.items()
                if item.cache_layer == layer
            ]
        else:
            items = [
                {
                    'id': item.knowledge_item.id,
                    'title': item.knowledge_item.title,
                    'content': item.knowledge_item.content,
                    'knowledge_type': item.knowledge_item.knowledge_type.value,
                    'cache_priority': item.cache_priority,
                    'cache_layer': item.cache_layer,
                    'access_count': item.access_count
                }
                for item in self.warm_cache.values()
            ]
        
        return sorted(items, key=lambda x: x['cache_priority'], reverse=True)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache_stats
    
    def _update_cache_stats(self):
        """Update cache statistics"""
        if not self.warm_cache:
            return
        
        priorities = [item.cache_priority for item in self.warm_cache.values()]
        layers = {}
        
        for item in self.warm_cache.values():
            layer = item.cache_layer
            if layer not in layers:
                layers[layer] = 0
            layers[layer] += 1
        
        self.cache_stats = {
            'total_items': len(self.warm_cache),
            'cache_layers': layers,
            'average_priority': sum(priorities) / len(priorities),
            'memory_usage_estimate': sum(
                len(item.knowledge_item.content) for item in self.warm_cache.values()
            ),
            'last_warming': datetime.now()
        }
    
    def clear_cache(self):
        """Clear the warm cache"""
        self.warm_cache.clear()
        self.cache_stats = {
            'total_items': 0,
            'cache_layers': {},
            'average_priority': 0.0,
            'memory_usage_estimate': 0,
            'last_warming': None
        }
        logger.info("Cache cleared")

# Example usage
async def test_components():
    """Test the context manager and cache warmer"""
    # Database configuration
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'dbname': 'knowledge_persistence',
        'user': 'postgres',
        'password': 'your_password'
    }
    
    # Test Context Manager
    print("Testing Context Manager...")
    context_manager = CAGContextManager(max_tokens=50000, db_config=db_config)
    
    try:
        context = await context_manager.load_context_for_query(
            "How do I implement pattern recognition?",
            "test-session-001"
        )
        print(f"Context loaded: {len(context)} characters")
        print(f"Estimated tokens: {context_manager.count_tokens(context)}")
    except Exception as e:
        print(f"Context manager test failed: {e}")
    
    # Test Cache Warmer
    print("\nTesting Cache Warmer...")
    cache_warmer = CacheWarmingEngine(db_config)
    
    try:
        cache_stats = await cache_warmer.warm_cache_for_session(
            "test-session-001",
            {'keywords': ['pattern', 'recognition', 'AI'], 'project': 'knowledge-persistence-ai'}
        )
        print(f"Cache warmed: {cache_stats}")
        
        # Get cached knowledge
        cached_items = cache_warmer.get_cached_knowledge()
        print(f"Cached items: {len(cached_items)}")
        
        # Get cache stats
        stats = cache_warmer.get_cache_stats()
        print(f"Cache stats: {stats}")
        
    except Exception as e:
        print(f"Cache warmer test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_components())
