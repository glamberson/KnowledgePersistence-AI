#!/usr/bin/env python3
"""
Complete Session Storage - Store ENTIRE chat history
This addresses the critical gap identified in session storage
"""

import asyncio
import json
import uuid
import sys
from datetime import datetime
import psycopg
from psycopg.rows import dict_row

class CompleteSessionStorage:
    def __init__(self, db_config):
        self.db_config = db_config
        self.session_id = None
        self.complete_chat_history = []
        self.current_exchange = 1
        
    async def connect_db(self):
        return await psycopg.AsyncConnection.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            row_factory=dict_row
        )
    
    def start_session(self, session_id=None):
        """Start tracking a new session"""
        self.session_id = session_id or str(uuid.uuid4())
        self.complete_chat_history = []
        self.current_exchange = 1
        return self.session_id
    
    def record_user_prompt(self, prompt, timestamp=None):
        """Record user prompt with full context"""
        entry = {
            'exchange_number': self.current_exchange,
            'type': 'user_prompt',
            'content': prompt,
            'timestamp': timestamp or datetime.now().isoformat(),
            'character_count': len(prompt),
            'word_count': len(prompt.split())
        }
        self.complete_chat_history.append(entry)
        
    def record_ai_response(self, response, reasoning=None, tools_used=None):
        """Record AI response with reasoning and tools"""
        entry = {
            'exchange_number': self.current_exchange,
            'type': 'ai_response',
            'content': response,
            'reasoning': reasoning,
            'tools_used': tools_used or [],
            'timestamp': datetime.now().isoformat(),
            'character_count': len(response),
            'word_count': len(response.split())
        }
        self.complete_chat_history.append(entry)
        self.current_exchange += 1
        
    def record_redirection(self, user_correction, ai_understanding, correction_type):
        """Record user redirections/corrections with analysis"""
        entry = {
            'exchange_number': self.current_exchange,
            'type': 'redirection',
            'user_correction': user_correction,
            'ai_understanding': ai_understanding,
            'correction_type': correction_type,  # 'minor', 'complementary', 'clarifying', 'fundamental'
            'timestamp': datetime.now().isoformat()
        }
        self.complete_chat_history.append(entry)
        
    async def store_complete_session(self, session_metadata=None):
        """Store complete session with full chat history"""
        
        session_data = {
            'session_id': self.session_id,
            'repo_context': 'KnowledgePersistence-AI',
            'project_name': 'KnowledgePersistence-AI',
            'session_type': 'implementation',
            'complete_chat_history': self.complete_chat_history,
            'session_statistics': {
                'total_exchanges': self.current_exchange - 1,
                'total_characters': sum(entry.get('character_count', 0) for entry in self.complete_chat_history),
                'total_words': sum(entry.get('word_count', 0) for entry in self.complete_chat_history),
                'redirections_count': len([e for e in self.complete_chat_history if e['type'] == 'redirection'])
            },
            'metadata': session_metadata or {}
        }
        
        conn = await self.connect_db()
        async with conn.cursor() as cur:
            await cur.execute('''
                INSERT INTO session_complete_data 
                (session_id, repo_context, project_name, session_type,
                 full_conversation_data, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO UPDATE SET
                    full_conversation_data = %s,
                    updated_at = CURRENT_TIMESTAMP;
            ''', (
                self.session_id,
                session_data['repo_context'],
                session_data['project_name'],
                session_data['session_type'],
                json.dumps(session_data),
                datetime.now(),
                json.dumps(session_data)
            ))
        
        await conn.commit()
        await conn.close()
        
        return self.session_id
    
    async def load_complete_session(self, session_id):
        """Load complete session data from database"""
        conn = await self.connect_db()
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
            self.session_id = session_id
            self.complete_chat_history = session_data['complete_chat_history']
            print(f"Loaded session {session_id} with {len(self.complete_chat_history)} exchanges")
            return session_data
        else:
            print(f"Session {session_id} not found")
            return None

# Database configuration
DB_CONFIG = {
    'host': '192.168.10.90',
    'port': 5432,
    'dbname': 'knowledge_persistence',
    'user': 'postgres',
    'password': 'SecureKnowledgePassword2025'
}

async def main():
    if len(sys.argv) >= 3 and sys.argv[2] == "load":
        if len(sys.argv) >= 5 and sys.argv[3] == "--session-id":
            session_id = sys.argv[4]
            storage = CompleteSessionStorage(DB_CONFIG)
            session_data = await storage.load_complete_session(session_id)
            if session_data:
                print(f"\n=== SESSION LOADED: {session_id} ===")
                print(f"Project: {session_data.get('project_name')}")
                print(f"Repository: {session_data.get('repo_context')}")
                print(f"Session Type: {session_data.get('session_type')}")
                print(f"\n=== CONVERSATION HISTORY ({len(session_data['complete_chat_history'])} exchanges) ===")
                for i, exchange in enumerate(session_data['complete_chat_history'], 1):
                    print(f"\n--- Exchange {i} [{exchange['type']}] ---")
                    if exchange['type'] == 'user_prompt':
                        print(f"USER: {exchange['content']}")
                    elif exchange['type'] == 'ai_response':
                        print(f"AI: {exchange['content']}")
                    elif exchange['type'] == 'redirection':
                        print(f"REDIRECTION: {exchange.get('user_correction', exchange.get('content', 'Unknown'))}")
                        if 'ai_error_description' in exchange:
                            print(f"AI ERROR: {exchange['ai_error_description']}")
                        if 'severity' in exchange:
                            print(f"SEVERITY: {exchange['severity']}")
                        
                print(f"\n=== SUMMARY ===")
                total_exchanges = len(session_data['complete_chat_history'])
                redirections = len([e for e in session_data['complete_chat_history'] if e['type'] == 'redirection'])
                print(f"Total Exchanges: {total_exchanges}")
                print(f"Redirections: {redirections}")
                if redirections > 0:
                    redirection_rate = (redirections / total_exchanges) * 100
                    print(f"Redirection Rate: {redirection_rate:.1f}%")
                return
            else:
                print(f"Session {session_id} not found")
                return
        else:
            print("Usage: python complete_session_storage.py --action load --session-id <session_id>")
            return
    
    # Create storage instance
    storage = CompleteSessionStorage(DB_CONFIG)
    
    # Start session
    session_id = storage.start_session()
    print(f"Started session: {session_id}")
    
    # Record example conversation
    storage.record_user_prompt("ok, read next session prompt.md but then wait for further instructions. i want to discuss some things.")
    storage.record_ai_response("I've read the session prompt. Ready to discuss - what would you like to cover before we proceed?")
    
    storage.record_user_prompt("first summarize what you understand of the current project, what we're about to do and your responsibilities so i can see if we need to make initial adjustments.")
    storage.record_ai_response("Project Understanding: KnowledgePersistence-AI - Revolutionary AI knowledge persistence database...")
    
    storage.record_redirection(
        "ok some adjustment is required. for CAG implementation, that is not tied to qwen at all. qwen is simple a tool we are going to use but it has no specific bering on CAG.",
        "I incorrectly associated qwen with CAG when qwen is simply a tool",
        "clarifying"
    )
    
    # Store complete session
    session_id = await storage.store_complete_session({
        'major_insights': ['CAG+RAG complementary framework', 'Complete session storage requirement'],
        'critical_gaps_identified': ['Missing complete chat history'],
        'corrections_applied': ['Separated qwen from CAG concept']
    })
    
    print(f"Complete session stored: {session_id}")

if __name__ == "__main__":
    asyncio.run(main())