#!/usr/bin/env python3
"""
Enhanced Knowledge Persistence MCP Server with Self-Assessment
============================================================
Extended version with AI performance tracking, reflection, and self-improvement tools.

NEW CAPABILITIES:
- Real-time performance assessment
- Session reflection and analysis
- Learning effectiveness tracking
- Automated improvement recommendations
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
logger = logging.getLogger("enhanced-knowledge-mcp-server")

# Database Configuration
DB_CONFIG = {
    "host": "192.168.10.90",
    "port": 5432,
    "database": "knowledge_persistence",
    "user": "postgres", 
    "password": os.getenv("DB_PASSWORD", "")
}

class SelfAssessmentEngine:
    """AI self-assessment and reflection engine"""
    
    def __init__(self, db):
        self.db = db
        self.current_session_id = None
        self.session_start_time = None
        self.redirection_count = 0
        self.comprehension_gaps = []
        
    def start_session_tracking(self, session_identifier: str, project_context: str = None):
        """Initialize performance tracking for new session"""
        self.current_session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        self.redirection_count = 0
        self.comprehension_gaps = []
        
        # Store session in database
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_sessions (id, session_identifier, project_context, start_time)
                    VALUES (%s, %s, %s, %s)
                """, (self.current_session_id, session_identifier, project_context, self.session_start_time))
                conn.commit()
        
        logger.info(f"Started session tracking: {self.current_session_id}")
        return self.current_session_id
    
    def track_redirection(self, user_correction: str, ai_misunderstanding: str):
        """Track when user has to redirect AI understanding"""
        self.redirection_count += 1
        gap = {
            'correction': user_correction,
            'misunderstanding': ai_misunderstanding,
            'timestamp': datetime.now().isoformat(),
            'redirection_number': self.redirection_count
        }
        self.comprehension_gaps.append(gap)
        
        # Store learning event
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_learning_metrics (
                        session_id, learning_event_type, trigger_event,
                        previous_understanding, corrected_understanding
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    self.current_session_id, 'correction', 'user_redirection',
                    ai_misunderstanding, user_correction
                ))
                conn.commit()
    
    def assess_context_comprehension(self, task: str, initial_score: int, final_score: int):
        """Assess comprehension quality for a specific task"""
        if not self.current_session_id:
            return "No active session for assessment"
        
        improvement = final_score - initial_score
        performance_score = max(0, final_score - (self.redirection_count * 10))
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_self_assessments (
                        session_id, assessment_type, task_description,
                        initial_understanding_score, final_understanding_score,
                        redirection_count, comprehension_gaps, performance_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    self.current_session_id, 'context_comprehension', task,
                    initial_score, final_score, self.redirection_count,
                    json.dumps(self.comprehension_gaps), performance_score
                ))
                conn.commit()
        
        return {
            'task': task,
            'initial_understanding': initial_score,
            'final_understanding': final_score,
            'improvement': improvement,
            'redirections_required': self.redirection_count,
            'performance_score': performance_score,
            'comprehension_gaps': self.comprehension_gaps
        }
    
    def assess_information_retrieval(self, query: str, documents: List[str], 
                                   relevance: int, completeness: int, quality: int):
        """Assess quality of information retrieval"""
        if not self.current_session_id:
            return "No active session for assessment"
        
        efficiency = max(0, 100 - (len(documents) * 5))  # Penalty for excessive document access
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO knowledge_retrieval_assessments (
                        session_id, query_intent, documents_accessed,
                        relevance_score, completeness_score, quality_score, efficiency_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    self.current_session_id, query, documents,
                    relevance, completeness, quality, efficiency
                ))
                conn.commit()
        
        return {
            'query': query,
            'documents_accessed': len(documents),
            'relevance_score': relevance,
            'completeness_score': completeness,
            'quality_score': quality,
            'efficiency_score': efficiency,
            'overall_score': (relevance + completeness + quality + efficiency) / 4
        }
    
    def generate_session_reflection(self):
        """Generate comprehensive session reflection"""
        if not self.current_session_id:
            return "No active session for reflection"
        
        # Get session performance data
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get assessment summary
                cur.execute("""
                    SELECT 
                        COUNT(*) as assessment_count,
                        AVG(initial_understanding_score) as avg_initial,
                        AVG(final_understanding_score) as avg_final,
                        SUM(redirection_count) as total_redirections,
                        AVG(performance_score) as avg_performance
                    FROM ai_self_assessments 
                    WHERE session_id = %s
                """, (self.current_session_id,))
                assessment_summary = cur.fetchone()
                
                # Get retrieval performance
                cur.execute("""
                    SELECT 
                        COUNT(*) as retrieval_count,
                        AVG(relevance_score) as avg_relevance,
                        AVG(completeness_score) as avg_completeness,
                        AVG(quality_score) as avg_quality,
                        AVG(efficiency_score) as avg_efficiency
                    FROM knowledge_retrieval_assessments
                    WHERE session_id = %s
                """, (self.current_session_id,))
                retrieval_summary = cur.fetchone()
                
                # Get learning events
                cur.execute("""
                    SELECT learning_event_type, COUNT(*) as count
                    FROM ai_learning_metrics
                    WHERE session_id = %s
                    GROUP BY learning_event_type
                """, (self.current_session_id,))
                learning_events = cur.fetchall()
        
        # Calculate overall session score
        comprehension_score = assessment_summary['avg_final'] if assessment_summary['avg_final'] else 0
        retrieval_score = ((retrieval_summary['avg_relevance'] or 0) + 
                          (retrieval_summary['avg_completeness'] or 0) + 
                          (retrieval_summary['avg_quality'] or 0)) / 3
        efficiency_penalty = min(50, (assessment_summary['total_redirections'] or 0) * 10)
        overall_score = max(0, (comprehension_score * 0.4 + retrieval_score * 0.4 + 
                               (100 - efficiency_penalty) * 0.2))
        
        reflection = {
            'session_id': self.current_session_id,
            'session_duration_minutes': (datetime.now() - self.session_start_time).total_seconds() / 60,
            'overall_performance_score': round(overall_score, 1),
            'context_comprehension': {
                'average_initial_understanding': round(assessment_summary['avg_initial'] or 0, 1),
                'average_final_understanding': round(assessment_summary['avg_final'] or 0, 1),
                'improvement_demonstrated': round((assessment_summary['avg_final'] or 0) - 
                                                (assessment_summary['avg_initial'] or 0), 1),
                'total_redirections_required': assessment_summary['total_redirections'] or 0
            },
            'information_retrieval': {
                'average_relevance': round(retrieval_summary['avg_relevance'] or 0, 1),
                'average_completeness': round(retrieval_summary['avg_completeness'] or 0, 1),
                'average_quality': round(retrieval_summary['avg_quality'] or 0, 1),
                'average_efficiency': round(retrieval_summary['avg_efficiency'] or 0, 1)
            },
            'learning_events': {dict(event)['learning_event_type']: dict(event)['count'] 
                              for event in learning_events},
            'key_insights': self._generate_performance_insights(assessment_summary, retrieval_summary),
            'improvement_recommendations': self._generate_improvement_recommendations(overall_score, 
                                                                                    assessment_summary, 
                                                                                    retrieval_summary)
        }
        
        # Store reflection
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_self_assessments (
                        session_id, assessment_type, reflection_notes, performance_score
                    ) VALUES (%s, %s, %s, %s)
                """, (
                    self.current_session_id, 'session_reflection', 
                    json.dumps(reflection), round(overall_score)
                ))
                conn.commit()
        
        return reflection
    
    def _generate_performance_insights(self, assessment_summary, retrieval_summary):
        """Generate insights from performance data"""
        insights = []
        
        if assessment_summary['total_redirections'] and assessment_summary['total_redirections'] > 2:
            insights.append("High redirection count suggests initial context comprehension issues")
        
        if assessment_summary['avg_final'] and assessment_summary['avg_final'] > 85:
            insights.append("Strong final understanding demonstrates good learning capability")
        
        if retrieval_summary['avg_quality'] and retrieval_summary['avg_quality'] < 70:
            insights.append("Information retrieval quality needs improvement")
        
        if retrieval_summary['avg_efficiency'] and retrieval_summary['avg_efficiency'] > 80:
            insights.append("Efficient information access demonstrates good search strategy")
        
        return insights
    
    def _generate_improvement_recommendations(self, overall_score, assessment_summary, retrieval_summary):
        """Generate specific improvement recommendations"""
        recommendations = []
        
        if overall_score < 70:
            recommendations.append("Overall performance below target - implement comprehensive improvement plan")
        
        if assessment_summary['total_redirections'] and assessment_summary['total_redirections'] > 1:
            recommendations.append("Reduce redirections by improving initial context analysis")
            recommendations.append("Implement more thorough documentation review before task execution")
        
        if retrieval_summary['avg_completeness'] and retrieval_summary['avg_completeness'] < 80:
            recommendations.append("Improve information retrieval completeness through broader search strategies")
        
        if retrieval_summary['avg_relevance'] and retrieval_summary['avg_relevance'] < 80:
            recommendations.append("Enhance search query formulation for better relevance")
        
        return recommendations

class EnhancedKnowledgeDatabase:
    """Enhanced database interface with self-assessment capabilities"""
    
    def __init__(self):
        self.conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        self.assessment_engine = SelfAssessmentEngine(self)
    
    def get_connection(self):
        """Get database connection with dict row factory"""
        return psycopg.connect(self.conn_string, row_factory=dict_row)
    
    def get_performance_dashboard(self, days: int = 30):
        """Get AI performance dashboard data"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM ai_performance_dashboard 
                    WHERE start_time >= %s
                    ORDER BY start_time DESC
                """, (datetime.now() - timedelta(days=days),))
                return [dict(row) for row in cur.fetchall()]
    
    # Include all original methods from KnowledgeDatabase here...
    # (semantic_search, get_recent_knowledge, etc.)

# Create server instance
server = Server("enhanced-knowledge-persistence")
db = EnhancedKnowledgeDatabase()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for Claude Code"""
    return [
        Tool(
            name="start_session_tracking",
            description="Initialize AI performance tracking for new session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_identifier": {"type": "string", "description": "Unique session identifier"},
                    "project_context": {"type": "string", "description": "Project context for session"}
                },
                "required": ["session_identifier"]
            }
        ),
        Tool(
            name="track_redirection",
            description="Record when user has to redirect AI understanding",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_correction": {"type": "string", "description": "What the user had to correct"},
                    "ai_misunderstanding": {"type": "string", "description": "What AI misunderstood"}
                },
                "required": ["user_correction", "ai_misunderstanding"]
            }
        ),
        Tool(
            name="assess_context_comprehension",
            description="Assess AI comprehension quality for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Task description"},
                    "initial_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "final_score": {"type": "integer", "minimum": 0, "maximum": 100}
                },
                "required": ["task", "initial_score", "final_score"]
            }
        ),
        Tool(
            name="assess_information_retrieval",
            description="Assess quality of information retrieval performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query or information need"},
                    "documents": {"type": "array", "items": {"type": "string"}},
                    "relevance": {"type": "integer", "minimum": 0, "maximum": 100},
                    "completeness": {"type": "integer", "minimum": 0, "maximum": 100},
                    "quality": {"type": "integer", "minimum": 0, "maximum": 100}
                },
                "required": ["query", "documents", "relevance", "completeness", "quality"]
            }
        ),
        Tool(
            name="generate_session_reflection",
            description="Generate comprehensive session performance reflection",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_performance_dashboard",
            description="Get AI performance trends and analytics",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "minimum": 1, "maximum": 365, "default": 30}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for enhanced knowledge persistence"""
    
    try:
        if name == "start_session_tracking":
            session_id = db.assessment_engine.start_session_tracking(
                arguments["session_identifier"],
                arguments.get("project_context")
            )
            return [TextContent(
                type="text",
                text=f"Session tracking started. Session ID: {session_id}"
            )]
        
        elif name == "track_redirection":
            db.assessment_engine.track_redirection(
                arguments["user_correction"],
                arguments["ai_misunderstanding"]
            )
            return [TextContent(
                type="text",
                text=f"Redirection tracked. Total redirections: {db.assessment_engine.redirection_count}"
            )]
        
        elif name == "assess_context_comprehension":
            assessment = db.assessment_engine.assess_context_comprehension(
                arguments["task"],
                arguments["initial_score"],
                arguments["final_score"]
            )
            return [TextContent(
                type="text",
                text=f"Context comprehension assessment:\n{json.dumps(assessment, indent=2)}"
            )]
        
        elif name == "assess_information_retrieval":
            assessment = db.assessment_engine.assess_information_retrieval(
                arguments["query"],
                arguments["documents"],
                arguments["relevance"],
                arguments["completeness"],
                arguments["quality"]
            )
            return [TextContent(
                type="text",
                text=f"Information retrieval assessment:\n{json.dumps(assessment, indent=2)}"
            )]
        
        elif name == "generate_session_reflection":
            reflection = db.assessment_engine.generate_session_reflection()
            return [TextContent(
                type="text",
                text=f"Session reflection:\n{json.dumps(reflection, indent=2)}"
            )]
        
        elif name == "get_performance_dashboard":
            dashboard = db.get_performance_dashboard(arguments.get("days", 30))
            return [TextContent(
                type="text",
                text=f"Performance dashboard:\n{json.dumps(dashboard, indent=2, default=str)}"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def main():
    """Run the enhanced knowledge persistence MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())