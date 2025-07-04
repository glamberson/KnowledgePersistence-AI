#!/usr/bin/env python3
"""
CAG Context Manager
Core component for Cache-Augmented Generation context management
Based on CAG_ARCHITECTURE_DESIGN.md specifications
"""

import asyncio
import json
from typing import Dict, List, Optional
from enum import Enum
import psycopg
from psycopg.rows import dict_row

class KnowledgeType(Enum):
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    CONTEXTUAL = "contextual"
    RELATIONAL = "relational"
    EXPERIENTIAL = "experiential"
    TECHNICAL_DISCOVERY = "technical"
    PATTERN_RECOGNITION = "patterns"

class ContextLayer(Enum):
    SYSTEM = "system"
    PROJECT = "project"
    SESSION = "session"
    DOMAIN = "domain"
    EXPERIENCE = "experience"
    STRATEGIC = "strategic"
    DYNAMIC = "dynamic"
    RESPONSE = "response"

class CAGContextManager:
    def __init__(self, max_context_tokens=128000, db_config=None):
        self.max_context_tokens = max_context_tokens
        self.db_config = db_config
        
        # Context layer allocation from CAG architecture
        self.context_layers = {
            ContextLayer.SYSTEM: 2000,
            ContextLayer.PROJECT: 8000,
            ContextLayer.SESSION: 16000,
            ContextLayer.DOMAIN: 32000,
            ContextLayer.EXPERIENCE: 24000,
            ContextLayer.STRATEGIC: 16000,
            ContextLayer.DYNAMIC: 24000,
            ContextLayer.RESPONSE: 6000
        }
        
        self.loaded_context = {}
        self.knowledge_cache = {}
        
    async def connect_db(self):
        """Connect to knowledge persistence database"""
        if not self.db_config:
            return None
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
        return len(text.split()) * 1.3
    
    async def load_system_instructions(self) -> str:
        """Load core system instructions and personality"""
        return """CAG-Enabled AI Assistant with KnowledgePersistence-AI integration.
Revolutionary Cache-Augmented Generation system providing instant knowledge access.
Strategic partnership capabilities with continuous learning and pattern recognition."""
    
    async def load_project_context(self) -> str:
        """Load current project state and context"""
        return """Project: KnowledgePersistence-AI
Status: Phase 5 - CAG Implementation Active
Architecture: PostgreSQL + pgvector, 336+ knowledge items
Framework: Complete session storage, redirection analysis operational
Current Focus: Cache-Augmented Generation implementation"""
    
    async def load_session_history(self, session_id: str) -> str:
        """Load current session conversation history"""
        if not self.db_config:
            return "Session history unavailable - no database connection"
        
        try:
            conn = await self.connect_db()
            if not conn:
                return "Session history unavailable"
                
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT full_conversation_data 
                    FROM session_complete_data 
                    WHERE session_id = %s
                ''', (session_id,))
                result = await cur.fetchone()
                
            await conn.close()
            
            if result:
                session_data = result['full_conversation_data']
                history = []
                for exchange in session_data['complete_chat_history']:
                    if exchange['type'] == 'user_prompt':
                        history.append(f"USER: {exchange['content']}")
                    elif exchange['type'] == 'ai_response':
                        history.append(f"AI: {exchange['content']}")
                return "\n".join(history[-10:])  # Last 10 exchanges
            
            return "No session history found"
            
        except Exception as e:
            return f"Session history error: {str(e)}"
    
    async def load_domain_knowledge(self, domains: List[str]) -> str:
        """Load domain-specific knowledge"""
        if not self.db_config:
            return "Domain knowledge unavailable - no database connection"
        
        try:
            conn = await self.connect_db()
            if not conn:
                return "Domain knowledge unavailable"
                
            async with conn.cursor() as cur:
                domain_filter = " OR ".join([f"category ILIKE '%{domain}%'" for domain in domains])
                await cur.execute(f'''
                    SELECT title, content, knowledge_type
                    FROM knowledge_items 
                    WHERE {domain_filter}
                    ORDER BY created_at DESC
                    LIMIT 10
                ''')
                results = await cur.fetchall()
                
            await conn.close()
            
            knowledge_items = []
            for item in results:
                knowledge_items.append(f"[{item['knowledge_type']}] {item['title']}: {item['content'][:200]}...")
                
            return "\n".join(knowledge_items) if knowledge_items else "No domain knowledge found"
            
        except Exception as e:
            return f"Domain knowledge error: {str(e)}"
    
    async def load_relevant_experience(self, query: str) -> str:
        """Load experience memory based on query similarity"""
        if not self.db_config:
            return "Experience memory unavailable - no database connection"
        
        try:
            conn = await self.connect_db()
            if not conn:
                return "Experience memory unavailable"
                
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT title, content, category
                    FROM knowledge_items 
                    WHERE knowledge_type = 'experiential'
                    ORDER BY created_at DESC
                    LIMIT 5
                ''')
                results = await cur.fetchall()
                
            await conn.close()
            
            experiences = []
            for item in results:
                experiences.append(f"[{item['category']}] {item['title']}: {item['content'][:150]}...")
                
            return "\n".join(experiences) if experiences else "No experience memory available"
            
        except Exception as e:
            return f"Experience memory error: {str(e)}"
    
    async def load_strategic_insights(self, query: str) -> str:
        """Load strategic insights based on patterns"""
        if not self.db_config:
            return "Strategic insights unavailable - no database connection"
        
        try:
            conn = await self.connect_db()
            if not conn:
                return "Strategic insights unavailable"
                
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT title, content, knowledge_type
                    FROM knowledge_items 
                    WHERE knowledge_type IN ('procedural', 'technical_discovery')
                    ORDER BY created_at DESC
                    LIMIT 5
                ''')
                results = await cur.fetchall()
                
            await conn.close()
            
            insights = []
            for item in results:
                insights.append(f"[{item['knowledge_type']}] {item['title']}: {item['content'][:150]}...")
                
            return "\n".join(insights) if insights else "No strategic insights available"
            
        except Exception as e:
            return f"Strategic insights error: {str(e)}"
    
    def analyze_query_domains(self, query: str) -> List[str]:
        """Analyze query to identify relevant domains"""
        domains = []
        query_lower = query.lower()
        
        domain_keywords = {
            'database': ['database', 'postgresql', 'sql', 'pgvector'],
            'architecture': ['architecture', 'design', 'system', 'framework'],
            'implementation': ['implement', 'code', 'develop', 'build'],
            'configuration': ['config', 'setup', 'install', 'deploy'],
            'testing': ['test', 'validate', 'verify', 'debug'],
            'knowledge': ['knowledge', 'learning', 'pattern', 'insight']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ['general']
    
    async def load_dynamic_content(self, query: str, available_tokens: int) -> str:
        """Load dynamic content based on available token space"""
        if available_tokens < 1000:
            return "Limited space for dynamic content"
        
        # Load additional knowledge based on query
        try:
            conn = await self.connect_db()
            if not conn:
                return "Dynamic content unavailable"
                
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT title, content, knowledge_type
                    FROM knowledge_items 
                    ORDER BY created_at DESC
                    LIMIT 3
                ''')
                results = await cur.fetchall()
                
            await conn.close()
            
            content = []
            for item in results:
                content.append(f"[{item['knowledge_type']}] {item['title']}: {item['content'][:100]}...")
                
            return "\n".join(content)
            
        except Exception as e:
            return f"Dynamic content error: {str(e)}"
    
    def calculate_remaining_tokens(self, context: Dict) -> int:
        """Calculate remaining tokens in context window"""
        used_tokens = 0
        for layer_name, content in context.items():
            if layer_name in [l.value for l in ContextLayer]:
                used_tokens += self.count_tokens(str(content))
        
        return max(0, self.max_context_tokens - used_tokens)
    
    async def load_context_for_query(self, query: str, session_id: str) -> Dict:
        """Load optimal context for query - core CAG function"""
        context = {}
        
        # Always load system instructions
        context[ContextLayer.SYSTEM.value] = await self.load_system_instructions()
        
        # Load project context based on current state
        context[ContextLayer.PROJECT.value] = await self.load_project_context()
        
        # Load session history
        context[ContextLayer.SESSION.value] = await self.load_session_history(session_id)
        
        # Load domain knowledge based on query intent
        relevant_domains = self.analyze_query_domains(query)
        context[ContextLayer.DOMAIN.value] = await self.load_domain_knowledge(relevant_domains)
        
        # Load experience memory based on similarity
        context[ContextLayer.EXPERIENCE.value] = await self.load_relevant_experience(query)
        
        # Load strategic insights based on patterns
        context[ContextLayer.STRATEGIC.value] = await self.load_strategic_insights(query)
        
        # Use remaining space for dynamic content
        remaining_tokens = self.calculate_remaining_tokens(context)
        context[ContextLayer.DYNAMIC.value] = await self.load_dynamic_content(query, remaining_tokens)
        
        return self.compile_context(context)
    
    def compile_context(self, context: Dict) -> str:
        """Compile context layers into single context string"""
        compiled = []
        
        for layer in ContextLayer:
            layer_name = layer.value
            if layer_name in context and context[layer_name]:
                compiled.append(f"=== {layer_name.upper()} CONTEXT ===")
                compiled.append(str(context[layer_name]))
                compiled.append("")
        
        return "\n".join(compiled)

# Database configuration
DB_CONFIG = {
    'host': '192.168.10.90',
    'port': 5432,
    'dbname': 'knowledge_persistence',
    'user': 'postgres',
    'password': 'SecureKnowledgePassword2025'
}

async def test_context_manager():
    """Test CAG Context Manager functionality"""
    manager = CAGContextManager(db_config=DB_CONFIG)
    
    print("Testing CAG Context Manager...")
    test_query = "Implement CAG architecture with knowledge preloading"
    test_session = "test-session-123"
    
    context = await manager.load_context_for_query(test_query, test_session)
    
    print(f"Generated context ({manager.count_tokens(context)} tokens):")
    print(context[:1000] + "..." if len(context) > 1000 else context)

if __name__ == "__main__":
    asyncio.run(test_context_manager())