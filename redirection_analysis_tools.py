#!/usr/bin/env python3
"""
Redirection Analysis Tools
Analyze conversation patterns from complete session history
Date: 2025-07-04
"""

import asyncio
import json
from typing import Dict, List, Tuple
import psycopg
from psycopg.rows import dict_row
from datetime import datetime

class RedirectionAnalysisTools:
    def __init__(self, db_config):
        self.db_config = db_config
        
    async def connect_db(self):
        return await psycopg.AsyncConnection.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            row_factory=dict_row
        )
    
    async def analyze_session_redirections(self, session_id: str) -> Dict:
        """Analyze redirection patterns in a specific session"""
        
        conn = await self.connect_db()
        async with conn.cursor() as cur:
            await cur.execute('''
                SELECT full_conversation_data 
                FROM session_complete_data 
                WHERE session_id = %s
            ''', (session_id,))
            
            result = await cur.fetchone()
            
        await conn.close()
        
        if not result or 'complete_chat_history' not in result['full_conversation_data']:
            return {'error': 'No conversation history found'}
        
        chat_history = result['full_conversation_data']['complete_chat_history']
        
        # Extract redirections
        redirections = [entry for entry in chat_history if entry.get('type') == 'redirection']
        
        # Analyze patterns
        analysis = {
            'session_id': session_id,
            'total_redirections': len(redirections),
            'redirection_types': {},
            'redirection_details': [],
            'patterns_identified': []
        }
        
        # Count by type
        for redirection in redirections:
            correction_type = redirection.get('correction_type', 'unknown')
            if correction_type not in analysis['redirection_types']:
                analysis['redirection_types'][correction_type] = 0
            analysis['redirection_types'][correction_type] += 1
            
            # Detailed analysis
            analysis['redirection_details'].append({
                'exchange_number': redirection.get('exchange_number'),
                'correction_type': correction_type,
                'user_correction': redirection.get('user_correction', ''),
                'ai_understanding': redirection.get('ai_understanding', ''),
                'timestamp': redirection.get('timestamp')
            })
        
        # Identify patterns
        analysis['patterns_identified'] = self.identify_redirection_patterns(redirections)
        
        return analysis
    
    def identify_redirection_patterns(self, redirections: List[Dict]) -> List[str]:
        """Identify patterns in redirection data"""
        patterns = []
        
        # Check for repeated corrections
        correction_topics = {}
        for redirection in redirections:
            user_correction = redirection.get('user_correction', '').lower()
            
            # Simple keyword extraction for topic identification
            if 'qwen' in user_correction and 'cag' in user_correction:
                topic = 'qwen_cag_association'
            elif 'session' in user_correction and 'storage' in user_correction:
                topic = 'session_storage'
            elif 'implementation' in user_correction:
                topic = 'implementation_focus'
            else:
                topic = 'general'
            
            if topic not in correction_topics:
                correction_topics[topic] = 0
            correction_topics[topic] += 1
        
        # Identify repeated patterns
        for topic, count in correction_topics.items():
            if count > 1:
                patterns.append(f'Repeated corrections on {topic} ({count} times)')
        
        # Check for escalating correction types
        correction_types = [r.get('correction_type') for r in redirections]
        type_severity = {'minor': 1, 'complementary': 2, 'clarifying': 3, 'fundamental': 4}
        
        if len(correction_types) > 1:
            severity_progression = [type_severity.get(ct, 0) for ct in correction_types]
            if any(severity_progression[i] < severity_progression[i+1] for i in range(len(severity_progression)-1)):
                patterns.append('Escalating correction severity detected')
        
        return patterns
    
    async def analyze_all_sessions(self) -> Dict:
        """Analyze redirection patterns across all sessions"""
        
        conn = await self.connect_db()
        async with conn.cursor() as cur:
            await cur.execute('''
                SELECT session_id, full_conversation_data, created_at
                FROM session_complete_data 
                WHERE full_conversation_data IS NOT NULL
                ORDER BY created_at DESC
            ''')
            
            sessions = await cur.fetchall()
            
        await conn.close()
        
        overall_analysis = {
            'total_sessions_analyzed': len(sessions),
            'sessions_with_redirections': 0,
            'total_redirections': 0,
            'redirection_type_distribution': {},
            'common_patterns': [],
            'session_summaries': []
        }
        
        all_patterns = []
        
        for session in sessions:
            session_id = str(session['session_id'])
            session_analysis = await self.analyze_session_redirections(session_id)
            
            if session_analysis.get('total_redirections', 0) > 0:
                overall_analysis['sessions_with_redirections'] += 1
                overall_analysis['total_redirections'] += session_analysis['total_redirections']
                
                # Aggregate redirection types
                for rtype, count in session_analysis.get('redirection_types', {}).items():
                    if rtype not in overall_analysis['redirection_type_distribution']:
                        overall_analysis['redirection_type_distribution'][rtype] = 0
                    overall_analysis['redirection_type_distribution'][rtype] += count
                
                # Collect patterns
                all_patterns.extend(session_analysis.get('patterns_identified', []))
                
                # Session summary
                overall_analysis['session_summaries'].append({
                    'session_id': session_id,
                    'redirections': session_analysis['total_redirections'],
                    'types': session_analysis['redirection_types'],
                    'created_at': session['created_at'].isoformat() if session['created_at'] else None
                })
        
        # Identify common patterns
        pattern_counts = {}
        for pattern in all_patterns:
            if pattern not in pattern_counts:
                pattern_counts[pattern] = 0
            pattern_counts[pattern] += 1
        
        overall_analysis['common_patterns'] = [
            {'pattern': pattern, 'frequency': count} 
            for pattern, count in pattern_counts.items()
            if count > 1
        ]
        
        return overall_analysis
    
    async def generate_improvement_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on redirection analysis"""
        
        recommendations = []
        
        # Check for repeated patterns
        if analysis.get('common_patterns'):
            for pattern_info in analysis['common_patterns']:
                pattern = pattern_info['pattern']
                if 'qwen_cag_association' in pattern:
                    recommendations.append(
                        'Implement knowledge categorization training to prevent tool-concept confusion'
                    )
                elif 'session_storage' in pattern:
                    recommendations.append(
                        'Enhance session storage validation to ensure complete data capture'
                    )
                elif 'Escalating correction severity' in pattern:
                    recommendations.append(
                        'Implement early pattern detection to prevent fundamental misunderstandings'
                    )
        
        # Check redirection frequency
        total_sessions = analysis.get('total_sessions_analyzed', 0)
        sessions_with_redirections = analysis.get('sessions_with_redirections', 0)
        
        if total_sessions > 0:
            redirection_rate = sessions_with_redirections / total_sessions
            if redirection_rate > 0.5:
                recommendations.append(
                    f'High redirection rate ({redirection_rate:.1%}) - implement proactive comprehension validation'
                )
        
        # Check for fundamental vs minor redirection balance
        type_dist = analysis.get('redirection_type_distribution', {})
        fundamental_count = type_dist.get('fundamental', 0)
        total_redirections = analysis.get('total_redirections', 0)
        
        if total_redirections > 0 and fundamental_count / total_redirections > 0.3:
            recommendations.append(
                'High fundamental correction rate - enhance initial understanding protocols'
            )
        
        return recommendations

# Database configuration
DB_CONFIG = {
    'host': '192.168.10.90',
    'port': 5432,
    'dbname': 'knowledge_persistence',
    'user': 'postgres',
    'password': 'SecureKnowledgePassword2025'
}

async def main():
    analyzer = RedirectionAnalysisTools(DB_CONFIG)
    
    # Analyze current session
    current_session = '0daffdc5-b8f5-4243-bc7a-c6e0fdf4995a'
    print(f"Analyzing session: {current_session}")
    
    session_analysis = await analyzer.analyze_session_redirections(current_session)
    print(f"Session Analysis:")
    print(f"- Total redirections: {session_analysis.get('total_redirections', 0)}")
    print(f"- Redirection types: {session_analysis.get('redirection_types', {})}")
    print(f"- Patterns identified: {session_analysis.get('patterns_identified', [])}")
    
    # Analyze all sessions
    print("\\nAnalyzing all sessions...")
    overall_analysis = await analyzer.analyze_all_sessions()
    print(f"Overall Analysis:")
    print(f"- Sessions analyzed: {overall_analysis['total_sessions_analyzed']}")
    print(f"- Sessions with redirections: {overall_analysis['sessions_with_redirections']}")
    print(f"- Total redirections: {overall_analysis['total_redirections']}")
    print(f"- Type distribution: {overall_analysis['redirection_type_distribution']}")
    
    # Generate recommendations
    recommendations = await analyzer.generate_improvement_recommendations(overall_analysis)
    print(f"\\nImprovement Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

if __name__ == "__main__":
    asyncio.run(main())