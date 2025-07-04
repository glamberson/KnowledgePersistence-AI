#!/usr/bin/env python3
"""
CAG Cache Warming Engine
Implements cache warming strategies for Cache-Augmented Generation
Based on CAG_ARCHITECTURE_DESIGN.md specifications
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row

class CacheWarmingEngine:
    def __init__(self, db_config, pattern_recognizer=None):
        self.db_config = db_config
        self.pattern_recognizer = pattern_recognizer
        self.warm_cache = {}
        self.cache_priority_threshold = 0.3
        self.max_cache_items = 100
        
    async def connect_db(self):
        """Connect to knowledge persistence database"""
        return await psycopg.AsyncConnection.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            row_factory=dict_row
        )
    
    def calculate_cache_priority(self, knowledge_item: Dict) -> float:
        """Calculate priority for cache inclusion based on CAG algorithm"""
        priority_score = 0.0
        
        # Recency factor (0-1)
        created_at = knowledge_item.get('created_at', datetime.now())
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        days_old = (datetime.now() - created_at.replace(tzinfo=None)).days
        recency = max(0, 1 - (days_old / 30))  # Decay over 30 days
        priority_score += recency * 0.3
        
        # Strategic importance (0-1) - estimated from knowledge type
        knowledge_type = knowledge_item.get('knowledge_type', 'factual')
        strategic_value = {
            'technical_discovery': 0.9,
            'procedural': 0.8,
            'experiential': 0.7,
            'contextual': 0.6,
            'factual': 0.5,
            'relational': 0.4
        }.get(knowledge_type, 0.5)
        priority_score += strategic_value * 0.25
        
        # Usage frequency (0-1) - estimated
        access_count = knowledge_item.get('access_count', 1)
        frequency = min(1.0, access_count / 10)  # Normalize to max 10 accesses
        priority_score += frequency * 0.25
        
        # Knowledge type weighting
        knowledge_type = knowledge_item.get('knowledge_type', 'factual')
        type_weights = {
            'procedural': 0.9,
            'technical_discovery': 0.8,
            'experiential': 0.7,
            'contextual': 0.6,
            'factual': 0.5,
            'relational': 0.4
        }
        type_weight = type_weights.get(knowledge_type, 0.5)
        priority_score += type_weight * 0.2
        
        return min(1.0, priority_score)
    
    async def load_core_knowledge(self) -> List[Dict]:
        """Load core knowledge that should always be cached"""
        conn = await self.connect_db()
        
        try:
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT id, knowledge_type, category, title, content, created_at
                    FROM knowledge_items 
                    WHERE knowledge_type IN ('procedural', 'technical_discovery', 'experiential')
                    ORDER BY created_at DESC
                    LIMIT 20
                ''')
                results = await cur.fetchall()
                
        finally:
            await conn.close()
        
        core_knowledge = []
        for item in results:
            cache_item = {
                'id': item['id'],
                'knowledge_type': item['knowledge_type'],
                'category': item['category'],
                'title': item['title'],
                'content': item['content'],
                'created_at': item['created_at'],
                'cache_priority': self.calculate_cache_priority(item),
                'cache_layer': self.determine_cache_layer(item)
            }
            core_knowledge.append(cache_item)
        
        return sorted(core_knowledge, key=lambda x: x['cache_priority'], reverse=True)
    
    def determine_cache_layer(self, knowledge_item: Dict) -> str:
        """Determine which cache layer knowledge belongs to"""
        knowledge_type = knowledge_item.get('knowledge_type', 'factual')
        
        if knowledge_type in ['procedural', 'technical_discovery']:
            return 'domain'
        elif knowledge_type == 'experiential':
            return 'experience'
        elif knowledge_type == 'contextual':
            return 'session'
        else:
            return 'dynamic'
    
    async def predict_session_knowledge(self, user_context: Dict) -> List[Dict]:
        """Predict knowledge needed for session based on context"""
        conn = await self.connect_db()
        
        try:
            # Look for knowledge related to user context
            context_keywords = user_context.get('keywords', [])
            project_name = user_context.get('project', 'KnowledgePersistence-AI')
            
            if context_keywords:
                keyword_filter = " OR ".join([f"content ILIKE '%{kw}%'" for kw in context_keywords])
                query = f'''
                    SELECT id, knowledge_type, category, title, content, created_at
                    FROM knowledge_items 
                    WHERE ({keyword_filter})
                       OR category ILIKE '%{project_name}%'
                    ORDER BY created_at DESC
                    LIMIT 15
                '''
            else:
                query = '''
                    SELECT id, knowledge_type, category, title, content, created_at
                    FROM knowledge_items 
                    ORDER BY created_at DESC
                    LIMIT 10
                '''
            
            async with conn.cursor() as cur:
                await cur.execute(query)
                results = await cur.fetchall()
                
        finally:
            await conn.close()
        
        session_knowledge = []
        for item in results:
            cache_item = {
                'id': item['id'],
                'knowledge_type': item['knowledge_type'],
                'category': item['category'],
                'title': item['title'],
                'content': item['content'],
                'created_at': item['created_at'],
                'cache_priority': self.calculate_cache_priority(item),
                'cache_layer': self.determine_cache_layer(item)
            }
            session_knowledge.append(cache_item)
        
        return sorted(session_knowledge, key=lambda x: x['cache_priority'], reverse=True)
    
    async def pattern_predict_knowledge(self, session_id: str) -> List[Dict]:
        """Use pattern recognition to predict needed knowledge"""
        if not self.pattern_recognizer:
            return []
        
        # Placeholder for pattern-based prediction
        # In full implementation, this would use the pattern recognition system
        conn = await self.connect_db()
        
        try:
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT id, knowledge_type, category, title, content, created_at
                    FROM knowledge_items 
                    WHERE knowledge_type = 'experiential'
                    ORDER BY created_at DESC
                    LIMIT 5
                ''')
                results = await cur.fetchall()
                
        finally:
            await conn.close()
        
        predicted_knowledge = []
        for item in results:
            cache_item = {
                'id': item['id'],
                'knowledge_type': item['knowledge_type'],
                'category': item['category'],
                'title': item['title'],
                'content': item['content'],
                'created_at': item['created_at'],
                'cache_priority': self.calculate_cache_priority(item),
                'cache_layer': 'experience',
                'prediction_confidence': 0.7
            }
            predicted_knowledge.append(cache_item)
        
        return predicted_knowledge
    
    async def load_strategic_insights(self) -> List[Dict]:
        """Load strategic insights for cache warming"""
        conn = await self.connect_db()
        
        try:
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT id, knowledge_type, category, title, content, created_at
                    FROM knowledge_items 
                    WHERE knowledge_type IN ('procedural', 'technical_discovery')
                    ORDER BY created_at DESC
                    LIMIT 8
                ''')
                results = await cur.fetchall()
                
        finally:
            await conn.close()
        
        strategic_knowledge = []
        for item in results:
            cache_item = {
                'id': item['id'],
                'knowledge_type': item['knowledge_type'],
                'category': item['category'],
                'title': item['title'],
                'content': item['content'],
                'created_at': item['created_at'],
                'cache_priority': self.calculate_cache_priority(item),
                'cache_layer': 'strategic'
            }
            strategic_knowledge.append(cache_item)
        
        return strategic_knowledge
    
    def preload_to_context(self, knowledge_items: List[Dict]):
        """Preload knowledge items to context cache"""
        for item in knowledge_items:
            if item['cache_priority'] >= self.cache_priority_threshold:
                cache_key = f"{item['cache_layer']}:{item['id']}"
                self.warm_cache[cache_key] = {
                    'content': item['content'],
                    'title': item['title'],
                    'knowledge_type': item['knowledge_type'],
                    'priority': item['cache_priority'],
                    'loaded_at': datetime.now()
                }
    
    def background_preload(self, knowledge_items: List[Dict]):
        """Background preload for lower priority items"""
        # In full implementation, this would use async background tasks
        self.preload_to_context(knowledge_items)
    
    async def warm_cache_for_session(self, session_id: str, user_context: Dict = None) -> Dict:
        """Warm cache at session startup - main CAG function"""
        if user_context is None:
            user_context = {'keywords': ['CAG', 'implementation'], 'project': 'KnowledgePersistence-AI'}
        
        warming_start = time.time()
        cache_stats = {
            'phases_completed': 0,
            'items_loaded': 0,
            'cache_size': 0,
            'warming_time': 0
        }
        
        # Phase 1: Load core knowledge (immediate)
        print(f"Phase 1: Loading core knowledge...")
        core_knowledge = await self.load_core_knowledge()
        self.preload_to_context(core_knowledge)
        cache_stats['phases_completed'] += 1
        cache_stats['items_loaded'] += len(core_knowledge)
        print(f"Loaded {len(core_knowledge)} core knowledge items")
        
        # Phase 2: Load session-specific knowledge (2-3 seconds)
        print(f"Phase 2: Loading session-specific knowledge...")
        session_knowledge = await self.predict_session_knowledge(user_context)
        self.preload_to_context(session_knowledge)
        cache_stats['phases_completed'] += 1
        cache_stats['items_loaded'] += len(session_knowledge)
        print(f"Loaded {len(session_knowledge)} session-specific items")
        
        # Phase 3: Load pattern-predicted knowledge (background)
        print(f"Phase 3: Loading pattern-predicted knowledge...")
        predicted_knowledge = await self.pattern_predict_knowledge(session_id)
        self.background_preload(predicted_knowledge)
        cache_stats['phases_completed'] += 1
        cache_stats['items_loaded'] += len(predicted_knowledge)
        print(f"Loaded {len(predicted_knowledge)} pattern-predicted items")
        
        # Phase 4: Load strategic insights (background)
        print(f"Phase 4: Loading strategic insights...")
        strategic_knowledge = await self.load_strategic_insights()
        self.background_preload(strategic_knowledge)
        cache_stats['phases_completed'] += 1
        cache_stats['items_loaded'] += len(strategic_knowledge)
        print(f"Loaded {len(strategic_knowledge)} strategic insight items")
        
        cache_stats['cache_size'] = len(self.warm_cache)
        cache_stats['warming_time'] = time.time() - warming_start
        
        print(f"Cache warming complete: {cache_stats['items_loaded']} items in {cache_stats['warming_time']:.2f}s")
        return cache_stats
    
    def get_cached_knowledge(self, layer: str = None, limit: int = 10) -> List[Dict]:
        """Retrieve cached knowledge by layer"""
        if layer:
            filtered_cache = {k: v for k, v in self.warm_cache.items() if k.startswith(f"{layer}:")}
        else:
            filtered_cache = self.warm_cache
        
        # Sort by priority and return top items
        sorted_items = sorted(
            filtered_cache.items(), 
            key=lambda x: x[1]['priority'], 
            reverse=True
        )
        
        return [{'key': k, **v} for k, v in sorted_items[:limit]]
    
    def get_cache_stats(self) -> Dict:
        """Get current cache statistics"""
        return {
            'total_items': len(self.warm_cache),
            'cache_layers': len(set(k.split(':')[0] for k in self.warm_cache.keys())),
            'average_priority': sum(item['priority'] for item in self.warm_cache.values()) / len(self.warm_cache) if self.warm_cache else 0,
            'memory_usage_estimate': sum(len(str(item)) for item in self.warm_cache.values())
        }

# Database configuration
DB_CONFIG = {
    'host': '192.168.10.90',
    'port': 5432,
    'dbname': 'knowledge_persistence',
    'user': 'postgres',
    'password': 'SecureKnowledgePassword2025'
}

async def test_cache_warmer():
    """Test CAG Cache Warming Engine"""
    warmer = CacheWarmingEngine(DB_CONFIG)
    
    print("Testing CAG Cache Warming Engine...")
    
    user_context = {
        'keywords': ['CAG', 'architecture', 'implementation'],
        'project': 'KnowledgePersistence-AI'
    }
    
    cache_stats = await warmer.warm_cache_for_session("test-session-123", user_context)
    
    print(f"\nCache Statistics:")
    print(f"- Phases completed: {cache_stats['phases_completed']}")
    print(f"- Items loaded: {cache_stats['items_loaded']}")
    print(f"- Cache size: {cache_stats['cache_size']}")
    print(f"- Warming time: {cache_stats['warming_time']:.2f}s")
    
    # Show sample cached items
    print(f"\nSample cached items:")
    cached_items = warmer.get_cached_knowledge(limit=3)
    for item in cached_items:
        print(f"- [{item['knowledge_type']}] {item['title'][:50]}... (Priority: {item['priority']:.2f})")

if __name__ == "__main__":
    asyncio.run(test_cache_warmer())