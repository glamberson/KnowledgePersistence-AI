#!/usr/bin/env python3
"""
Knowledge Persistence MCP Server
================================
Model Context Protocol (MCP) server that provides Claude Code with real-time access 
to the KnowledgePersistence-AI database for context loading and knowledge retrieval.

This enables true context persistence across Claude Code sessions by providing
tools for:
- Loading relevant session context at startup
- Searching for similar knowledge during tasks
- Storing new insights and discoveries
- Retrieving project-specific knowledge patterns

Installation:
    pip install mcp psycopg[binary] numpy python-dotenv

Usage:
    python3 knowledge-mcp-server.py

Claude Code Configuration (~/.claude/settings.json):
{
  "mcpServers": {
    "knowledge-persistence": {
      "command": "python3",
      "args": ["/path/to/knowledge-mcp-server.py"]
    }
  }
}
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource
)

# Database imports
import psycopg
from psycopg.rows import dict_row
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knowledge-mcp-server")

# Database Configuration
DB_CONFIG = {
    "host": "192.168.10.90",
    "port": 5432,
    "database": "knowledge_persistence",
    "user": "postgres", 
    "password": "SecureKnowledgePassword2025"
}

class KnowledgeDatabase:
    """Database interface for knowledge persistence operations"""
    
    def __init__(self):
        self.conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    
    def get_connection(self):
        """Get database connection with dict row factory"""
        return psycopg.connect(self.conn_string, row_factory=dict_row)
    
    def semantic_search(self, query: str, limit: int = 10, project: str = None, min_importance: int = 0) -> List[Dict]:
        """Search for semantically similar knowledge items"""
        # For now, use text search until we implement embedding generation
        # In production, would use vector similarity with query embeddings
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                base_query = """
                SELECT id, knowledge_type, category, title, content, importance_score, 
                       context_data, created_by, created_at
                FROM knowledge_items 
                WHERE importance_score >= %s
                  AND (content ILIKE %s OR title ILIKE %s)
                """
                params = [min_importance, f"%{query}%", f"%{query}%"]
                
                if project:
                    base_query += " AND context_data->>'project' = %s"
                    params.append(project)
                
                base_query += " ORDER BY importance_score DESC, created_at DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(base_query, params)
                results = cur.fetchall()
                
                return [dict(row) for row in results]
    
    def get_recent_knowledge(self, days: int = 7, project: str = None, min_importance: int = 50, limit: int = 20) -> List[Dict]:
        """Get recent high-value knowledge items"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                base_query = """
                SELECT id, knowledge_type, category, title, content, importance_score,
                       context_data, created_by, created_at
                FROM knowledge_items 
                WHERE created_at >= %s AND importance_score >= %s
                """
                params = [datetime.now() - timedelta(days=days), min_importance]
                
                if project:
                    base_query += " AND context_data->>'project' = %s"
                    params.append(project)
                
                base_query += " ORDER BY importance_score DESC, created_at DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(base_query, params)
                results = cur.fetchall()
                
                return [dict(row) for row in results]
    
    def get_project_knowledge(self, project: str, knowledge_types: List[str] = None, limit: int = 15) -> List[Dict]:
        """Get project-specific knowledge"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                base_query = """
                SELECT id, knowledge_type, category, title, content, importance_score,
                       context_data, created_by, created_at
                FROM knowledge_items 
                WHERE context_data->>'project' = %s
                """
                params = [project]
                
                if knowledge_types:
                    placeholders = ','.join(['%s'] * len(knowledge_types))
                    base_query += f" AND knowledge_type IN ({placeholders})"
                    params.extend(knowledge_types)
                
                base_query += " ORDER BY importance_score DESC, created_at DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(base_query, params)
                results = cur.fetchall()
                
                return [dict(row) for row in results]
    
    def get_recent_sessions(self, count: int = 5, project: str = None) -> List[Dict]:
        """Get recent AI session summaries"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                base_query = """
                SELECT id, session_identifier, project_context, start_time,
                       session_metadata, user_feedback
                FROM ai_sessions 
                WHERE 1=1
                """
                params = []
                
                if project:
                    base_query += " AND project_context = %s"
                    params.append(project)
                
                base_query += " ORDER BY start_time DESC LIMIT %s"
                params.append(count)
                
                cur.execute(base_query, params)
                results = cur.fetchall()
                
                return [dict(row) for row in results]
    
    def store_knowledge_item(self, knowledge_data: Dict) -> str:
        """Store a new knowledge item"""
        item_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                insert_query = """
                INSERT INTO knowledge_items (
                    id, knowledge_type, category, title, content,
                    importance_score, context_data, created_by, retrieval_triggers
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Handle retrieval_triggers as PostgreSQL array
                retrieval_triggers = knowledge_data.get('retrieval_triggers', [])
                if retrieval_triggers and isinstance(retrieval_triggers, list):
                    triggers_array = retrieval_triggers
                else:
                    triggers_array = []
                
                cur.execute(insert_query, (
                    item_id,
                    knowledge_data.get('knowledge_type', 'experiential'),
                    knowledge_data.get('category', 'general'),
                    knowledge_data.get('title', 'Untitled Knowledge'),
                    knowledge_data.get('content', ''),
                    knowledge_data.get('importance_score', 50),
                    json.dumps(knowledge_data.get('context_data', {})),
                    knowledge_data.get('created_by', 'mcp-client'),
                    triggers_array
                ))
                
                conn.commit()
                return item_id
    
    def get_technical_gotchas(self, problem_signature: str, limit: int = 5) -> List[Dict]:
        """Get technical gotchas for similar problems"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT id, problem_signature, working_solution, problem_context, last_encountered
                FROM technical_gotchas 
                WHERE problem_signature ILIKE %s OR problem_description ILIKE %s
                ORDER BY last_encountered DESC 
                LIMIT %s
                """, (f"%{problem_signature}%", f"%{problem_signature}%", limit))
                
                results = cur.fetchall()
                return [dict(row) for row in results]

class KnowledgeMCPServer:
    """MCP Server for Knowledge Persistence System"""
    
    def __init__(self):
        self.db = KnowledgeDatabase()
        self.server = Server("knowledge-persistence")
        self.setup_tools()
    
    def setup_tools(self):
        """Register all MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available knowledge persistence tools"""
            return [
                Tool(
                    name="get_session_context",
                    description="Load relevant context for session startup including recent insights, project knowledge, and session history",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project": {
                                "type": "string",
                                "description": "Project name to filter context (optional)"
                            },
                            "max_items": {
                                "type": "integer", 
                                "description": "Maximum number of context items to retrieve",
                                "default": 20
                            }
                        }
                    }
                ),
                Tool(
                    name="search_knowledge",
                    description="Search for knowledge items semantically similar to a query or current task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query or task description"
                            },
                            "project": {
                                "type": "string",
                                "description": "Project name to filter results (optional)"
                            },
                            "knowledge_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by knowledge types: factual, procedural, contextual, relational, experiential, technical_discovery"
                            },
                            "min_importance": {
                                "type": "integer",
                                "description": "Minimum importance score (0-100)",
                                "default": 50
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_contextual_knowledge", 
                    description="Get contextual knowledge for current situation, automatically selecting relevant insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "situation": {
                                "type": "string",
                                "description": "Description of current situation or task"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["situation"]
                    }
                ),
                Tool(
                    name="store_knowledge",
                    description="Store new knowledge item discovered during session",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "knowledge_type": {
                                "type": "string",
                                "enum": ["factual", "procedural", "contextual", "relational", "experiential", "technical_discovery"],
                                "description": "Type of knowledge being stored"
                            },
                            "category": {
                                "type": "string",
                                "description": "Knowledge category (e.g., troubleshooting, configuration, research)"
                            },
                            "title": {
                                "type": "string",
                                "description": "Brief descriptive title for the knowledge"
                            },
                            "content": {
                                "type": "string", 
                                "description": "Detailed knowledge content"
                            },
                            "importance_score": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100,
                                "description": "Importance score (0-100)",
                                "default": 50
                            },
                            "project": {
                                "type": "string",
                                "description": "Associated project name (optional)"
                            },
                            "context_metadata": {
                                "type": "object",
                                "description": "Additional context metadata (optional)"
                            },
                            "retrieval_triggers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords that should trigger this knowledge (optional)"
                            }
                        },
                        "required": ["knowledge_type", "title", "content"]
                    }
                ),
                Tool(
                    name="get_technical_gotchas",
                    description="Get technical gotchas and solutions for similar problems",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_signature": {
                                "type": "string", 
                                "description": "Description of the technical problem"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 5
                            }
                        },
                        "required": ["problem_signature"]
                    }
                ),
                Tool(
                    name="get_project_patterns",
                    description="Get established patterns and procedures for a specific project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project": {
                                "type": "string",
                                "description": "Project name"
                            },
                            "pattern_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Types of patterns to retrieve (procedural, technical_discovery, etc.)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of patterns",
                                "default": 15
                            }
                        },
                        "required": ["project"]
                    }
                ),
                Tool(
                    name="start_session",
                    description="Start a new AI session with project context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_context": {
                                "type": "string",
                                "description": "Project context description"
                            }
                        },
                        "required": ["project_context"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_session_context":
                    return await self.get_session_context(**arguments)
                elif name == "search_knowledge":
                    return await self.search_knowledge(**arguments)
                elif name == "get_contextual_knowledge":
                    return await self.get_contextual_knowledge(**arguments)
                elif name == "store_knowledge":
                    return await self.store_knowledge(**arguments)
                elif name == "get_technical_gotchas":
                    return await self.get_technical_gotchas(**arguments)
                elif name == "get_project_patterns":
                    return await self.get_project_patterns(**arguments)
                elif name == "start_session":
                    return await self.start_session(**arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def get_session_context(self, project: str = None, max_items: int = 20) -> List[TextContent]:
        """Load comprehensive session context"""
        try:
            context_components = []
            
            # Get recent high-importance knowledge
            recent_knowledge = self.db.get_recent_knowledge(
                days=7, 
                project=project, 
                min_importance=60,
                limit=max_items // 2
            )
            
            # Get project-specific procedures and patterns
            project_knowledge = []
            if project:
                project_knowledge = self.db.get_project_knowledge(
                    project=project,
                    knowledge_types=['procedural', 'technical_discovery'],
                    limit=max_items // 3
                )
            
            # Get recent session summaries
            session_history = self.db.get_recent_sessions(
                count=3,
                project=project
            )
            
            # Format context response
            context_sections = []
            
            if recent_knowledge:
                context_sections.append("## Recent Key Insights (Last 7 Days)")
                for item in recent_knowledge[:5]:  # Top 5 most important
                    context_sections.append(f"### {item['title']} (Importance: {item['importance_score']})")
                    context_sections.append(f"**Type**: {item['knowledge_type']} | **Category**: {item['category']}")
                    context_sections.append(f"**Content**: {item['content'][:300]}...")
                    context_sections.append("")
            
            if project_knowledge:
                context_sections.append(f"## {project} Project Patterns & Procedures")
                for item in project_knowledge[:5]:
                    context_sections.append(f"### {item['title']}")
                    context_sections.append(f"**Type**: {item['knowledge_type']}")
                    context_sections.append(f"**Content**: {item['content'][:200]}...")
                    context_sections.append("")
            
            if session_history:
                context_sections.append("## Recent Session History")
                for session in session_history:
                    context_sections.append(f"### Session {session['start_time'].strftime('%Y-%m-%d')}")
                    context_sections.append(f"**Project**: {session.get('project_context', 'Unknown')}")
                    if session.get('user_feedback'):
                        context_sections.append(f"**Feedback**: {session['user_feedback'][:150]}...")
                    if session.get('session_metadata'):
                        context_sections.append(f"**Metadata**: {str(session['session_metadata'])[:100]}...")
                    context_sections.append("")
            
            # Summary statistics
            stats_section = [
                "## Knowledge Base Statistics",
                f"- Recent insights loaded: {len(recent_knowledge)}",
                f"- Project patterns available: {len(project_knowledge)}",
                f"- Session history depth: {len(session_history)}",
                f"- Project context: {project or 'All projects'}",
                ""
            ]
            
            response_text = "\n".join(stats_section + context_sections)
            
            return [TextContent(
                type="text", 
                text=response_text if response_text.strip() else "No relevant context found for the specified criteria."
            )]
            
        except Exception as e:
            logger.error(f"Error getting session context: {e}")
            return [TextContent(type="text", text=f"Error loading session context: {str(e)}")]
    
    async def search_knowledge(self, query: str, project: str = None, knowledge_types: List[str] = None, 
                             min_importance: int = 50, limit: int = 10) -> List[TextContent]:
        """Search for relevant knowledge"""
        try:
            results = self.db.semantic_search(
                query=query,
                limit=limit,
                project=project,
                min_importance=min_importance
            )
            
            if not results:
                return [TextContent(type="text", text=f"No knowledge found matching '{query}' with minimum importance {min_importance}")]
            
            # Format results
            response_sections = [f"## Knowledge Search Results for: '{query}'", ""]
            
            for i, item in enumerate(results, 1):
                response_sections.extend([
                    f"### {i}. {item['title']} (Score: {item['importance_score']})",
                    f"**Type**: {item['knowledge_type']} | **Category**: {item['category']}",
                    f"**Created**: {item['created_at'].strftime('%Y-%m-%d %H:%M')} by {item['created_by']}",
                    f"**Content**: {item['content'][:400]}{'...' if len(item['content']) > 400 else ''}",
                    ""
                ])
            
            response_text = "\n".join(response_sections)
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return [TextContent(type="text", text=f"Error searching knowledge: {str(e)}")]
    
    async def get_contextual_knowledge(self, situation: str, max_results: int = 10) -> List[TextContent]:
        """Get contextual knowledge for current situation"""
        try:
            # Use semantic search to find relevant knowledge
            results = self.db.semantic_search(
                query=situation,
                limit=max_results,
                min_importance=40
            )
            
            if not results:
                return [TextContent(type="text", text=f"No contextual knowledge found for situation: '{situation}'")]
            
            response_sections = [f"## Contextual Knowledge for: '{situation}'", ""]
            
            # Group by knowledge type for better organization
            by_type = {}
            for item in results:
                knowledge_type = item['knowledge_type']
                if knowledge_type not in by_type:
                    by_type[knowledge_type] = []
                by_type[knowledge_type].append(item)
            
            for knowledge_type, items in by_type.items():
                response_sections.append(f"### {knowledge_type.title()} Knowledge")
                for item in items[:3]:  # Limit items per type
                    response_sections.extend([
                        f"**{item['title']}** (Importance: {item['importance_score']})",
                        f"{item['content'][:250]}{'...' if len(item['content']) > 250 else ''}",
                        ""
                    ])
            
            response_text = "\n".join(response_sections)
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"Error getting contextual knowledge: {e}")
            return [TextContent(type="text", text=f"Error getting contextual knowledge: {str(e)}")]
    
    async def store_knowledge(self, knowledge_type: str, title: str, content: str,
                            category: str = "general", importance_score: int = 50,
                            project: str = None, context_metadata: Dict = None, 
                            retrieval_triggers: List[str] = None) -> List[TextContent]:
        """Store new knowledge item"""
        try:
            knowledge_data = {
                'knowledge_type': knowledge_type,
                'category': category,
                'title': title,
                'content': content,
                'importance_score': importance_score,
                'context_data': {
                    'project': project,
                    'source': 'mcp-client',
                    'timestamp': datetime.now().isoformat(),
                    **(context_metadata or {})
                },
                'created_by': 'mcp-client',
                'retrieval_triggers': retrieval_triggers or []
            }
            
            item_id = self.db.store_knowledge_item(knowledge_data)
            
            return [TextContent(
                type="text",
                text=f"Knowledge item stored successfully!\n\n**ID**: {item_id}\n**Title**: {title}\n**Type**: {knowledge_type}\n**Importance**: {importance_score}"
            )]
            
        except Exception as e:
            logger.error(f"Error storing knowledge: {e}")
            return [TextContent(type="text", text=f"Error storing knowledge: {str(e)}")]
    
    async def get_technical_gotchas(self, problem_signature: str, max_results: int = 5) -> List[TextContent]:
        """Get technical gotchas for similar problems"""
        try:
            results = self.db.get_technical_gotchas(problem_signature, max_results)
            
            if not results:
                return [TextContent(type="text", text=f"No technical gotchas found for problem: '{problem_signature}'")]
            
            response_sections = [f"## Technical Gotchas for: '{problem_signature}'", ""]
            
            for i, item in enumerate(results, 1):
                response_sections.extend([
                    f"### {i}. {item['problem_signature']}",
                    f"**Working Solution**: {item['working_solution']}",
                    f"**Date**: {item['last_encountered'].strftime('%Y-%m-%d')}",
                    ""
                ])
            
            response_text = "\n".join(response_sections)
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"Error getting technical gotchas: {e}")
            return [TextContent(type="text", text=f"Error getting technical gotchas: {str(e)}")]
    
    async def get_project_patterns(self, project: str, pattern_types: List[str] = None, limit: int = 15) -> List[TextContent]:
        """Get project-specific patterns and procedures"""
        try:
            results = self.db.get_project_knowledge(
                project=project,
                knowledge_types=pattern_types or ['procedural', 'technical_discovery'],
                limit=limit
            )
            
            if not results:
                return [TextContent(type="text", text=f"No patterns found for project: '{project}'")]
            
            response_sections = [f"## {project} Project Patterns", ""]
            
            # Group by category
            by_category = {}
            for item in results:
                category = item['category']
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(item)
            
            for category, items in by_category.items():
                response_sections.append(f"### {category.title()}")
                for item in items:
                    response_sections.extend([
                        f"**{item['title']}** ({item['knowledge_type']})",
                        f"{item['content'][:200]}{'...' if len(item['content']) > 200 else ''}",
                        ""
                    ])
            
            response_text = "\n".join(response_sections)
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"Error getting project patterns: {e}")
            return [TextContent(type="text", text=f"Error getting project patterns: {str(e)}")]
    
    async def start_session(self, project_context: str) -> List[TextContent]:
        """Start a new AI session with project context"""
        try:
            # Get contextual knowledge for the project context
            contextual_knowledge = await self.get_contextual_knowledge(project_context)
            
            response_sections = [
                f"# Session Started: {project_context}",
                "",
                "## Relevant Knowledge Retrieved",
                ""
            ]
            
            # Extract the contextual knowledge content
            for content_item in contextual_knowledge:
                if hasattr(content_item, 'text'):
                    response_sections.append(content_item.text)
                    response_sections.append("")
            
            response_sections.extend([
                "---",
                f"Session initialized successfully at {datetime.now().isoformat()}",
                f"Project Context: {project_context}"
            ])
            
            return [TextContent(type="text", text="\n".join(response_sections))]
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return [TextContent(type="text", text=f"Error starting session: {str(e)}")]

async def main():
    """Run the MCP server"""
    knowledge_server = KnowledgeMCPServer()
    
    # Test database connection
    try:
        with knowledge_server.db.get_connection() as conn:
            logger.info("Successfully connected to knowledge database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)
    
    logger.info("Starting Knowledge Persistence MCP Server...")
    
    async with stdio_server() as streams:
        await knowledge_server.server.run(
            streams[0], 
            streams[1], 
            knowledge_server.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())