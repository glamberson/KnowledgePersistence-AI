#!/usr/bin/env python3
"""
Session Framework Processor
Implements complete session data storage and dynamic categorization
Date: 2025-07-04
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg
from psycopg.rows import dict_row
import openai
import numpy as np

class SessionFrameworkProcessor:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.openai_client = openai.OpenAI()
        self.current_session_id = None
        self.verification_required = True
        
    async def connect_db(self):
        """Establish database connection"""
        conn = await psycopg.AsyncConnection.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            row_factory=dict_row
        )
        return conn
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate OpenAI embedding for text"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    async def digest_prompt(self, user_prompt: str, session_context: Dict) -> Dict:
        """Mandatory prompt digestion before action"""
        
        # Extract intent and context
        intent_analysis = {
            'user_intent': self.extract_intent(user_prompt),
            'session_context': session_context,
            'knowledge_requirements': await self.identify_knowledge_needs(user_prompt),
            'categorization_implications': await self.assess_categorization(user_prompt),
            'previous_session_relevance': await self.check_previous_session_relevance(user_prompt)
        }
        
        # Create verification summary
        verification_summary = self.create_verification_summary(intent_analysis)
        
        # Store prompt digestion
        await self.store_prompt_digestion(user_prompt, intent_analysis, verification_summary)
        
        return {
            'analysis': intent_analysis,
            'verification_summary': verification_summary,
            'requires_confirmation': self.verification_required
        }
    
    def extract_intent(self, prompt: str) -> str:
        """Extract user intent from prompt"""
        # Simple intent analysis - can be enhanced with NLP
        if 'continue' in prompt.lower() or 'previous' in prompt.lower():
            return 'continuation'
        elif 'new' in prompt.lower() or 'start' in prompt.lower():
            return 'new_topic'
        elif 'implement' in prompt.lower() or 'deploy' in prompt.lower():
            return 'implementation'
        elif 'analyze' in prompt.lower() or 'understand' in prompt.lower():
            return 'analysis'
        else:
            return 'general'
    
    async def identify_knowledge_needs(self, prompt: str) -> List[str]:
        """Identify what knowledge is needed for this prompt"""
        
        # Generate embedding for prompt
        prompt_embedding = await self.generate_embedding(prompt)
        
        # Query similar knowledge items
        conn = await self.connect_db()
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT title, knowledge_type, content, 
                       1 - (embedding <=> %s::vector) as similarity
                FROM knowledge_items
                WHERE 1 - (embedding <=> %s::vector) > 0.7
                ORDER BY similarity DESC
                LIMIT 10;
            """, (prompt_embedding, prompt_embedding))
            
            similar_items = await cur.fetchall()
        
        await conn.close()
        
        return [item['title'] for item in similar_items]
    
    async def assess_categorization(self, prompt: str) -> Dict:
        """Assess categorization implications of prompt"""
        
        categories = {
            'project_category': 'KnowledgePersistence-AI',  # Default
            'action_type': self.extract_intent(prompt),
            'technical_domain': self.extract_technical_domain(prompt),
            'priority_level': self.assess_priority(prompt)
        }
        
        return categories
    
    def extract_technical_domain(self, prompt: str) -> str:
        """Extract technical domain from prompt"""
        domains = {
            'database': ['database', 'sql', 'postgres', 'schema'],
            'ai_ml': ['ai', 'machine learning', 'embedding', 'vector'],
            'framework': ['framework', 'architecture', 'implementation'],
            'session': ['session', 'continuity', 'storage'],
            'knowledge': ['knowledge', 'categorization', 'retrieval']
        }
        
        prompt_lower = prompt.lower()
        for domain, keywords in domains.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return domain
        
        return 'general'
    
    def assess_priority(self, prompt: str) -> str:
        """Assess priority level of prompt"""
        high_priority_keywords = ['critical', 'urgent', 'immediate', 'important']
        medium_priority_keywords = ['should', 'need', 'required']
        
        prompt_lower = prompt.lower()
        
        if any(keyword in prompt_lower for keyword in high_priority_keywords):
            return 'high'
        elif any(keyword in prompt_lower for keyword in medium_priority_keywords):
            return 'medium'
        else:
            return 'normal'
    
    async def check_previous_session_relevance(self, prompt: str) -> Optional[Dict]:
        """Check if prompt relates to previous sessions"""
        
        # Generate embedding for prompt
        prompt_embedding = await self.generate_embedding(prompt)
        
        # Check for similar previous sessions
        conn = await self.connect_db()
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT session_id, project_name, session_type,
                       insights_discovered, created_at
                FROM session_complete_data
                ORDER BY created_at DESC
                LIMIT 5;
            """)
            
            recent_sessions = await cur.fetchall()
        
        await conn.close()
        
        # Simple relevance check - can be enhanced
        if recent_sessions:
            return {
                'most_recent_session': recent_sessions[0]['session_id'],
                'project_continuity': recent_sessions[0]['project_name'],
                'session_count': len(recent_sessions)
            }
        
        return None
    
    def create_verification_summary(self, analysis: Dict) -> str:
        """Create verification summary for user confirmation"""
        
        summary = f"""
VERIFICATION SUMMARY:
- Intent: {analysis['user_intent']}
- Technical Domain: {analysis['categorization_implications']['technical_domain']}
- Priority: {analysis['categorization_implications']['priority_level']}
- Knowledge Requirements: {len(analysis['knowledge_requirements'])} items identified
- Previous Session Relevance: {'Yes' if analysis['previous_session_relevance'] else 'No'}

Is this understanding correct? Should I proceed with this analysis?
        """
        
        return summary.strip()
    
    async def store_prompt_digestion(self, prompt: str, analysis: Dict, verification: str):
        """Store prompt digestion results"""
        
        if not self.current_session_id:
            self.current_session_id = str(uuid.uuid4())
        
        # Store in session_complete_data
        conn = await self.connect_db()
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO session_complete_data 
                (session_id, repo_context, project_name, session_type, 
                 verification_summaries, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO UPDATE SET
                    verification_summaries = session_complete_data.verification_summaries || %s,
                    updated_at = CURRENT_TIMESTAMP;
            """, (
                self.current_session_id,
                'KnowledgePersistence-AI',
                analysis['categorization_implications']['project_category'],
                analysis['user_intent'],
                json.dumps({'prompt': prompt, 'analysis': analysis, 'verification': verification}),
                datetime.now(),
                json.dumps({'prompt': prompt, 'analysis': analysis, 'verification': verification})
            ))
        
        await conn.commit()
        await conn.close()
    
    async def create_dynamic_association(self, data_items: List[str], context: str, strength: float):
        """Create vector-based associations from data interactions"""
        
        # Generate embedding for association
        association_text = f"{context} - {' '.join(data_items)}"
        embedding = await self.generate_embedding(association_text)
        
        # Store dynamic category
        conn = await self.connect_db()
        async with conn.cursor() as cur:
            category_id = str(uuid.uuid4())
            await cur.execute("""
                INSERT INTO dynamic_categories 
                (id, category_name, strength_score, association_vector, 
                 created_from_session_id, usage_frequency)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                category_id,
                self.extract_category_name(context),
                strength,
                embedding,
                self.current_session_id,
                1
            ))
        
        await conn.commit()
        await conn.close()
        
        return category_id
    
    def extract_category_name(self, context: str) -> str:
        """Extract category name from context"""
        # Simple extraction - can be enhanced
        words = context.split()
        if len(words) >= 2:
            return f"{words[0]}_{words[1]}"
        elif len(words) == 1:
            return words[0]
        else:
            return "general_category"
    
    async def store_complete_session(self, session_data: Dict):
        """Store complete session data"""
        
        conn = await self.connect_db()
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO session_complete_data 
                (session_id, repo_context, project_name, session_type,
                 full_conversation_data, insights_discovered, 
                 knowledge_items_created, knowledge_items_referenced,
                 vector_associations, category_classifications)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO UPDATE SET
                    full_conversation_data = %s,
                    insights_discovered = %s,
                    knowledge_items_created = %s,
                    knowledge_items_referenced = %s,
                    vector_associations = %s,
                    category_classifications = %s,
                    updated_at = CURRENT_TIMESTAMP;
            """, (
                self.current_session_id,
                session_data.get('repo_context', 'KnowledgePersistence-AI'),
                session_data.get('project_name', 'KnowledgePersistence-AI'),
                session_data.get('session_type', 'implementation'),
                json.dumps(session_data.get('conversation_data', {})),
                json.dumps(session_data.get('insights', {})),
                session_data.get('knowledge_items_created', []),
                session_data.get('knowledge_items_referenced', []),
                json.dumps(session_data.get('vector_associations', {})),
                json.dumps(session_data.get('category_classifications', {})),
                # Conflict resolution values
                json.dumps(session_data.get('conversation_data', {})),
                json.dumps(session_data.get('insights', {})),
                session_data.get('knowledge_items_created', []),
                session_data.get('knowledge_items_referenced', []),
                json.dumps(session_data.get('vector_associations', {})),
                json.dumps(session_data.get('category_classifications', {}))
            ))
        
        await conn.commit()
        await conn.close()

# Database configuration
DB_CONFIG = {
    'host': '192.168.10.90',
    'port': 5432,
    'dbname': 'knowledge_persistence',
    'user': 'postgres',
    'password': 'SecureKnowledgePassword2025'
}

# Example usage
async def main():
    processor = SessionFrameworkProcessor(DB_CONFIG)
    
    # Test prompt digestion
    test_prompt = "Continue from the previous session about CAG implementation"
    session_context = {'repo': 'KnowledgePersistence-AI', 'project': 'session-framework'}
    
    result = await processor.digest_prompt(test_prompt, session_context)
    print("Prompt Digestion Result:")
    print(result['verification_summary'])
    
    # Store complete session example
    session_data = {
        'conversation_data': {'test': 'session framework implementation'},
        'insights': {'breakthrough': 'CAG+RAG integration framework'},
        'knowledge_items_created': ['8d23c8dd-2458-4552-9387-3ac758601335'],
        'knowledge_items_referenced': []
    }
    
    await processor.store_complete_session(session_data)
    print(f"Session stored with ID: {processor.current_session_id}")

if __name__ == "__main__":
    asyncio.run(main())