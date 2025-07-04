#!/usr/bin/env python3
"""
import os
CAG Engine - Core Cache-Augmented Generation System
Integrates Context Manager and Cache Warmer for revolutionary AI knowledge access
Based on CAG_ARCHITECTURE_DESIGN.md specifications
"""

import asyncio
import json
import time
import sys
from typing import Dict, List, Optional
from datetime import datetime
import psycopg
from psycopg.rows import dict_row

from cag_context_manager import CAGContextManager, KnowledgeType, ContextLayer
from cag_cache_warmer import CacheWarmingEngine

class CAGEngine:
    def __init__(self, db_config, max_tokens=128000):
        self.db_config = db_config
        self.context_manager = CAGContextManager(max_tokens, db_config)
        self.cache_warmer = CacheWarmingEngine(db_config)
        self.session_cache_warmed = {}
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'average_response_time': 0,
            'total_queries': 0
        }
        
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
    
    async def ensure_cache_warmed(self, session_id: str, user_context: Dict = None) -> bool:
        """Ensure cache is warmed for session"""
        if session_id in self.session_cache_warmed:
            print(f"Cache already warmed for session {session_id}")
            return True
        
        print(f"Warming cache for session {session_id}...")
        
        if user_context is None:
            user_context = {
                'keywords': ['CAG', 'implementation', 'knowledge'],
                'project': 'KnowledgePersistence-AI'
            }
        
        cache_stats = await self.cache_warmer.warm_cache_for_session(session_id, user_context)
        self.session_cache_warmed[session_id] = {
            'warmed_at': datetime.now(),
            'cache_stats': cache_stats
        }
        
        print(f"Cache warmed: {cache_stats['items_loaded']} items in {cache_stats['warming_time']:.2f}s")
        return True
    
    async def process_query(self, query: str, session_id: str, user_context: Dict = None) -> Dict:
        """Process query with full CAG pipeline"""
        query_start = time.time()
        
        # Ensure cache is warmed
        await self.ensure_cache_warmed(session_id, user_context)
        
        # Load context for query (knowledge already cached)
        context_start = time.time()
        context = await self.context_manager.load_context_for_query(query, session_id)
        context_time = time.time() - context_start
        
        # Prepare response data
        response = {
            'query': query,
            'session_id': session_id,
            'context_loaded': True,
            'context_size_tokens': self.context_manager.count_tokens(context),
            'cached_knowledge_items': len(self.cache_warmer.warm_cache),
            'performance': {
                'context_load_time': context_time,
                'total_processing_time': time.time() - query_start,
                'cache_hit': session_id in self.session_cache_warmed
            },
            'context_layers': self._analyze_context_layers(context),
            'full_context': context
        }
        
        # Update performance metrics
        self._update_performance_metrics(response['performance'])
        
        return response
    
    def _analyze_context_layers(self, context: str) -> Dict:
        """Analyze which context layers are included"""
        layers = {}
        for layer in ContextLayer:
            layer_marker = f"=== {layer.value.upper()} CONTEXT ==="
            layers[layer.value] = layer_marker in context
        return layers
    
    def _update_performance_metrics(self, performance: Dict):
        """Update engine performance metrics"""
        self.performance_metrics['total_queries'] += 1
        
        if performance['cache_hit']:
            self.performance_metrics['cache_hits'] += 1
        else:
            self.performance_metrics['cache_misses'] += 1
        
        # Update rolling average response time
        current_avg = self.performance_metrics['average_response_time']
        total_queries = self.performance_metrics['total_queries']
        new_time = performance['total_processing_time']
        
        self.performance_metrics['average_response_time'] = (
            (current_avg * (total_queries - 1) + new_time) / total_queries
        )
    
    async def update_knowledge_from_interaction(self, query: str, response: Dict, session_id: str):
        """Update knowledge based on interaction"""
        try:
            conn = await self.connect_db()
            
            # Store interaction knowledge
            interaction_knowledge = {
                'knowledge_type': 'contextual',
                'category': 'interaction',
                'title': f"CAG Query: {query[:50]}...",
                'content': f"Query: {query}\nProcessing time: {response['performance']['total_processing_time']:.2f}s\nContext tokens: {response['context_size_tokens']}",
                'session_id': session_id
            }
            
            async with conn.cursor() as cur:
                await cur.execute('''
                    INSERT INTO knowledge_items 
                    (knowledge_type, category, title, content)
                    VALUES (%s, %s, %s, %s)
                ''', (
                    interaction_knowledge['knowledge_type'],
                    interaction_knowledge['category'],
                    interaction_knowledge['title'],
                    interaction_knowledge['content']
                ))
            
            await conn.commit()
            await conn.close()
            
        except Exception as e:
            print(f"Error storing interaction knowledge: {e}")
    
    async def get_cached_knowledge_summary(self, layer: str = None) -> Dict:
        """Get summary of cached knowledge"""
        cached_items = self.cache_warmer.get_cached_knowledge(layer)
        cache_stats = self.cache_warmer.get_cache_stats()
        
        return {
            'total_cached_items': cache_stats['total_items'],
            'cache_layers': cache_stats['cache_layers'],
            'average_priority': cache_stats['average_priority'],
            'memory_usage_estimate': cache_stats['memory_usage_estimate'],
            'sample_items': cached_items[:5],
            'performance_metrics': self.performance_metrics
        }
    
    async def warm_domain_cache(self, domain: str, priority: str = "normal") -> Dict:
        """Warm cache for specific domain"""
        print(f"Warming cache for domain: {domain}")
        
        try:
            conn = await self.connect_db()
            
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT id, knowledge_type, category, title, content, created_at
                    FROM knowledge_items 
                    WHERE category ILIKE %s OR content ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT 10
                ''', (f'%{domain}%', f'%{domain}%'))
                results = await cur.fetchall()
            
            await conn.close()
            
            # Convert to cache format and preload
            domain_knowledge = []
            for item in results:
                cache_item = {
                    'id': item['id'],
                    'knowledge_type': item['knowledge_type'],
                    'category': item['category'],
                    'title': item['title'],
                    'content': item['content'],
                    'created_at': item['created_at'],
                    'cache_priority': self.cache_warmer.calculate_cache_priority(item),
                    'cache_layer': 'domain'
                }
                domain_knowledge.append(cache_item)
            
            self.cache_warmer.preload_to_context(domain_knowledge)
            
            return {
                'domain': domain,
                'items_loaded': len(domain_knowledge),
                'priority': priority,
                'success': True
            }
            
        except Exception as e:
            return {
                'domain': domain,
                'error': str(e),
                'success': False
            }

# Database configuration
DB_CONFIG = {
    'host': '192.168.10.90',
    'port': 5432,
    'dbname': 'knowledge_persistence',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD', '')
}

async def test_cag_engine():
    """Test complete CAG Engine functionality"""
    engine = CAGEngine(DB_CONFIG)
    
    print("=== CAG ENGINE TEST ===")
    print("Initializing Cache-Augmented Generation Engine...")
    
    test_session = "cag-test-session-001"
    test_queries = [
        "How do I implement CAG architecture?",
        "What is the database schema for knowledge persistence?",
        "Show me pattern recognition implementation details"
    ]
    
    user_context = {
        'keywords': ['CAG', 'implementation', 'architecture'],
        'project': 'KnowledgePersistence-AI'
    }
    
    print(f"\nTesting CAG Engine with {len(test_queries)} queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        response = await engine.process_query(query, test_session, user_context)
        
        print(f"Context loaded: {response['context_loaded']}")
        print(f"Context size: {response['context_size_tokens']} tokens")
        print(f"Cached items: {response['cached_knowledge_items']}")
        print(f"Processing time: {response['performance']['total_processing_time']:.2f}s")
        print(f"Cache hit: {response['performance']['cache_hit']}")
        
        # Update knowledge from interaction
        await engine.update_knowledge_from_interaction(query, response, test_session)
    
    # Get final cache summary
    print(f"\n--- FINAL CACHE SUMMARY ---")
    cache_summary = await engine.get_cached_knowledge_summary()
    print(f"Total cached items: {cache_summary['total_cached_items']}")
    print(f"Cache layers: {cache_summary['cache_layers']}")
    print(f"Average priority: {cache_summary['average_priority']:.2f}")
    print(f"Memory usage estimate: {cache_summary['memory_usage_estimate']} chars")
    
    print(f"\n--- PERFORMANCE METRICS ---")
    metrics = cache_summary['performance_metrics']
    print(f"Total queries: {metrics['total_queries']}")
    print(f"Cache hits: {metrics['cache_hits']}")
    print(f"Cache misses: {metrics['cache_misses']}")
    print(f"Average response time: {metrics['average_response_time']:.2f}s")
    print(f"Cache hit rate: {(metrics['cache_hits'] / metrics['total_queries'] * 100):.1f}%")

async def main():
    """Main function with command line interface"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            await test_cag_engine()
        elif command == "query" and len(sys.argv) > 2:
            engine = CAGEngine(DB_CONFIG)
            query = " ".join(sys.argv[2:])
            session_id = "cli-session"
            
            print(f"Processing query: {query}")
            response = await engine.process_query(query, session_id)
            
            print(f"\nResponse Summary:")
            print(f"- Context tokens: {response['context_size_tokens']}")
            print(f"- Processing time: {response['performance']['total_processing_time']:.2f}s")
            print(f"- Cache status: {'HIT' if response['performance']['cache_hit'] else 'MISS'}")
            
        else:
            print("Usage:")
            print("  python cag_engine.py test                    # Run full test")
            print("  python cag_engine.py query <your question>   # Process single query")
    else:
        await test_cag_engine()

if __name__ == "__main__":
    asyncio.run(main())