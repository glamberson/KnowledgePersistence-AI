#!/usr/bin/env python3
"""
import os
Enhanced Redirection Analysis with Semantic Assessment
Implements comprehensive redirection analysis framework from audit findings
Addresses inadequate methodology that only counted frequency
"""

import asyncio
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row

class SemanticRedirectionAnalyzer:
    """Semantic analysis of redirection content and intent"""
    
    def __init__(self):
        self.redirection_categories = {
            'comprehension_gap': {
                'keywords': ['unclear', 'confused', 'don\'t understand', 'not clear', 'ambiguous'],
                'severity_base': 0.7,
                'description': 'AI failed to understand initial instruction'
            },
            'context_missing': {
                'keywords': ['need more context', 'missing information', 'more details', 'incomplete'],
                'severity_base': 0.6,
                'description': 'Insufficient context provided in initial request'
            },
            'scope_misalignment': {
                'keywords': ['not what I meant', 'different direction', 'wrong approach', 'misunderstood'],
                'severity_base': 0.8,
                'description': 'AI interpreted scope incorrectly'
            },
            'requirement_clarification': {
                'keywords': ['clarify', 'specify', 'more detail', 'elaborate', 'explain'],
                'severity_base': 0.4,
                'description': 'Need additional specification of requirements'
            },
            'error_correction': {
                'keywords': ['wrong', 'incorrect', 'mistake', 'error', 'fix'],
                'severity_base': 0.9,
                'description': 'AI made an actual error requiring correction'
            },
            'priority_shift': {
                'keywords': ['actually', 'instead', 'change priority', 'different focus'],
                'severity_base': 0.5,
                'description': 'User changed priority or focus mid-task'
            },
            'instruction_ambiguity': {
                'keywords': ['instructions not clear', 'ambiguous instructions', 'unclear guidance'],
                'severity_base': 0.7,
                'description': 'Initial instructions were ambiguous or unclear'
            }
        }
        
        self.severity_indicators = {
            'critical': ['completely wrong', 'major misunderstanding', 'total miss', 'way off'],
            'significant': ['not quite right', 'missing key aspect', 'important clarification'],
            'moderate': ['small adjustment', 'minor clarification', 'slight modification'],
            'minor': ['just to clarify', 'small detail', 'minor point', 'quick note']
        }
        
    def analyze_redirection_semantics(self, redirection_text: str, context: Dict = None) -> Dict:
        """Comprehensive semantic analysis of redirection"""
        
        analysis = {
            'original_text': redirection_text,
            'primary_category': self._categorize_redirection(redirection_text),
            'severity_assessment': self._assess_severity(redirection_text, context or {}),
            'emotional_tone': self._assess_emotional_tone(redirection_text),
            'specificity_level': self._measure_specificity(redirection_text),
            'root_cause_signals': self._identify_root_causes(redirection_text),
            'urgency_indicators': self._detect_urgency(redirection_text),
            'improvement_suggestions': []
        }
        
        # Generate specific improvement suggestions
        analysis['improvement_suggestions'] = self._generate_improvement_suggestions(analysis)
        
        return analysis
    
    def _categorize_redirection(self, text: str) -> Dict:
        """Categorize redirection by primary intent"""
        text_lower = text.lower()
        category_scores = {}
        
        for category, data in self.redirection_categories.items():
            score = 0
            matches = []
            
            for keyword in data['keywords']:
                if keyword in text_lower:
                    score += 1
                    matches.append(keyword)
            
            if score > 0:
                category_scores[category] = {
                    'score': score,
                    'matches': matches,
                    'severity_base': data['severity_base'],
                    'description': data['description']
                }
        
        if not category_scores:
            return {
                'primary': 'uncategorized',
                'confidence': 0.0,
                'matches': [],
                'description': 'Could not categorize redirection'
            }
        
        # Get highest scoring category
        primary_category = max(category_scores.items(), key=lambda x: x[1]['score'])
        
        return {
            'primary': primary_category[0],
            'confidence': min(1.0, primary_category[1]['score'] / 3),  # Normalize
            'matches': primary_category[1]['matches'],
            'description': primary_category[1]['description'],
            'all_categories': category_scores
        }
    
    def _assess_severity(self, text: str, context: Dict) -> Dict:
        """Assess severity of redirection"""
        text_lower = text.lower()
        severity_score = 0.2  # Base severity
        severity_level = 'minor'
        
        # Check for severity indicators
        for level, indicators in self.severity_indicators.items():
            matches = [ind for ind in indicators if ind in text_lower]
            if matches:
                severity_levels = {'minor': 0.2, 'moderate': 0.4, 'significant': 0.7, 'critical': 1.0}
                severity_score = max(severity_score, severity_levels[level])
                severity_level = level
                break
        
        # Context factors that increase severity
        if context.get('task_progress', 0) > 0.5:  # Mid-task redirections more severe
            severity_score *= 1.3
            
        if context.get('session_redirections', 0) > 2:  # Multiple redirections
            severity_score *= 1.2
            
        if context.get('time_invested', 0) > 300:  # More than 5 minutes invested
            severity_score *= 1.4
        
        # Length and complexity indicators
        if len(text) > 200:  # Long explanations indicate complexity
            severity_score *= 1.1
        
        return {
            'severity_score': min(1.0, severity_score),
            'severity_level': severity_level,
            'context_multipliers': {
                'task_progress': context.get('task_progress', 0),
                'session_redirections': context.get('session_redirections', 0),
                'time_invested': context.get('time_invested', 0)
            }
        }
    
    def _assess_emotional_tone(self, text: str) -> Dict:
        """Assess emotional tone of redirection"""
        text_lower = text.lower()
        
        frustration_indicators = ['frustrated', 'annoying', 'wrong again', 'keep missing']
        patience_indicators = ['let me clarify', 'just to be clear', 'small adjustment']
        urgency_indicators = ['urgent', 'asap', 'immediately', 'right away']
        
        tone_scores = {
            'frustration': sum(1 for ind in frustration_indicators if ind in text_lower),
            'patience': sum(1 for ind in patience_indicators if ind in text_lower),
            'urgency': sum(1 for ind in urgency_indicators if ind in text_lower)
        }
        
        dominant_tone = max(tone_scores.items(), key=lambda x: x[1])
        
        return {
            'dominant_tone': dominant_tone[0] if dominant_tone[1] > 0 else 'neutral',
            'tone_scores': tone_scores,
            'emotional_intensity': min(1.0, dominant_tone[1] / 3)
        }
    
    def _measure_specificity(self, text: str) -> Dict:
        """Measure how specific the redirection is"""
        
        specificity_indicators = {
            'specific_technical_terms': len(re.findall(r'\b[A-Z]{2,}\b', text)),  # Acronyms
            'specific_numbers': len(re.findall(r'\d+', text)),  # Numbers
            'specific_examples': text.lower().count('example') + text.lower().count('instance'),
            'specific_references': text.count('this') + text.count('that') + text.count('these')
        }
        
        total_indicators = sum(specificity_indicators.values())
        specificity_score = min(1.0, total_indicators / 5)  # Normalize
        
        return {
            'specificity_score': specificity_score,
            'specificity_level': 'high' if specificity_score > 0.7 else 'medium' if specificity_score > 0.3 else 'low',
            'indicators': specificity_indicators
        }
    
    def _identify_root_causes(self, text: str) -> List[str]:
        """Identify potential root causes from redirection text"""
        text_lower = text.lower()
        root_causes = []
        
        root_cause_patterns = {
            'insufficient_initial_detail': ['need more detail', 'not enough information', 'incomplete'],
            'assumption_mismatch': ['assumed', 'thought you meant', 'expected'],
            'communication_gap': ['miscommunication', 'misunderstood', 'unclear'],
            'scope_creep': ['also need', 'forgot to mention', 'additional'],
            'technical_mismatch': ['wrong tool', 'different framework', 'not suitable'],
            'timing_issue': ['too early', 'not ready', 'premature']
        }
        
        for cause, patterns in root_cause_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                root_causes.append(cause)
        
        return root_causes
    
    def _detect_urgency(self, text: str) -> Dict:
        """Detect urgency indicators in redirection"""
        text_lower = text.lower()
        
        urgency_keywords = ['urgent', 'asap', 'immediately', 'right away', 'critical', 'emergency']
        temporal_indicators = ['now', 'today', 'quickly', 'fast']
        
        urgency_score = (
            sum(2 for keyword in urgency_keywords if keyword in text_lower) +
            sum(1 for indicator in temporal_indicators if indicator in text_lower)
        )
        
        return {
            'urgency_score': min(1.0, urgency_score / 5),
            'urgency_level': 'high' if urgency_score >= 3 else 'medium' if urgency_score >= 1 else 'low',
            'detected_indicators': [kw for kw in urgency_keywords + temporal_indicators if kw in text_lower]
        }
    
    def _generate_improvement_suggestions(self, analysis: Dict) -> List[str]:
        """Generate specific improvement suggestions based on analysis"""
        suggestions = []
        
        primary_category = analysis['primary_category']['primary']
        severity = analysis['severity_assessment']['severity_level']
        
        # Category-specific suggestions
        if primary_category == 'comprehension_gap':
            suggestions.append("Implement proactive comprehension validation before task execution")
            suggestions.append("Add confirmation step: 'Before I proceed, let me confirm my understanding...'")
            
        elif primary_category == 'context_missing':
            suggestions.append("Establish context gathering protocol at task initiation")
            suggestions.append("Ask clarifying questions upfront rather than making assumptions")
            
        elif primary_category == 'scope_misalignment':
            suggestions.append("Implement scope confirmation before beginning work")
            suggestions.append("Break down complex requests into smaller, confirmable steps")
            
        elif primary_category == 'instruction_ambiguity':
            suggestions.append("Request specific examples when instructions are abstract")
            suggestions.append("Paraphrase understanding back to user for confirmation")
        
        # Severity-specific suggestions
        if severity in ['critical', 'significant']:
            suggestions.append("Implement mandatory pause-and-confirm for complex tasks")
            suggestions.append("Add progress checkpoints to catch misalignment early")
        
        # Emotional tone considerations
        if analysis['emotional_tone']['dominant_tone'] == 'frustration':
            suggestions.append("Acknowledge the redirection gracefully and apologize for misunderstanding")
            suggestions.append("Provide explicit confirmation of corrected understanding")
        
        return suggestions

class ResolutionEffectivenessTracker:
    """Track how effectively redirections are resolved"""
    
    def __init__(self):
        self.resolution_metrics = {
            'follow_up_redirections': 'Additional redirections after resolution',
            'task_completion_rate': 'Successful task completion post-resolution',
            'user_satisfaction_indicators': 'Positive language in subsequent exchanges',
            'session_productivity': 'Productive exchanges vs total exchanges'
        }
    
    def track_resolution_effectiveness(self, redirection_id: str, 
                                     post_resolution_exchanges: List[Dict]) -> Dict:
        """Track effectiveness of redirection resolution"""
        
        if len(post_resolution_exchanges) < 2:
            return {
                'effectiveness_score': 0.5,
                'resolution_quality': 'insufficient_data',
                'data_available': False
            }
        
        effectiveness_score = 1.0
        
        # Metric 1: No additional redirections (good)
        additional_redirections = sum(1 for ex in post_resolution_exchanges 
                                    if ex.get('type') == 'redirection')
        effectiveness_score -= (additional_redirections * 0.3)
        
        # Metric 2: Positive feedback indicators
        positive_indicators = ['good', 'perfect', 'exactly', 'that works', 'yes', 'correct']
        negative_indicators = ['no', 'wrong', 'still not', 'missing']
        
        positive_score = 0
        negative_score = 0
        
        for exchange in post_resolution_exchanges:
            content = exchange.get('content', '').lower()
            positive_score += sum(1 for indicator in positive_indicators if indicator in content)
            negative_score += sum(1 for indicator in negative_indicators if indicator in content)
        
        feedback_score = (positive_score - negative_score) / max(1, len(post_resolution_exchanges))
        effectiveness_score += (feedback_score * 0.2)
        
        # Metric 3: Task progression indicators
        progression_keywords = ['next', 'continue', 'proceed', 'now let\'s', 'moving on']
        progression_score = sum(1 for ex in post_resolution_exchanges
                              for keyword in progression_keywords
                              if keyword in ex.get('content', '').lower())
        
        effectiveness_score += min(0.2, progression_score * 0.1)
        
        # Metric 4: Session productivity
        productive_types = ['ai_response', 'user_prompt']
        productive_exchanges = sum(1 for ex in post_resolution_exchanges
                                 if ex.get('type') in productive_types)
        
        productivity_ratio = productive_exchanges / len(post_resolution_exchanges)
        effectiveness_score *= productivity_ratio
        
        # Determine resolution quality
        quality_thresholds = {
            'excellent': 0.8,
            'good': 0.6,
            'fair': 0.4,
            'poor': 0.2
        }
        
        resolution_quality = 'very_poor'
        for quality, threshold in quality_thresholds.items():
            if effectiveness_score >= threshold:
                resolution_quality = quality
                break
        
        return {
            'effectiveness_score': max(0, min(1.0, effectiveness_score)),
            'resolution_quality': resolution_quality,
            'metrics': {
                'additional_redirections': additional_redirections,
                'positive_feedback': positive_score,
                'negative_feedback': negative_score,
                'progression_indicators': progression_score,
                'productivity_ratio': productivity_ratio
            },
            'data_available': True,
            'improvement_areas': self._identify_improvement_areas(
                additional_redirections, positive_score, negative_score, progression_score
            )
        }
    
    def _identify_improvement_areas(self, additional_redirections: int, 
                                  positive_score: int, negative_score: int,
                                  progression_score: int) -> List[str]:
        """Identify specific areas for improvement"""
        areas = []
        
        if additional_redirections > 0:
            areas.append("Resolution incomplete - still requiring clarification")
            
        if negative_score > positive_score:
            areas.append("User dissatisfaction with resolution approach")
            
        if progression_score == 0:
            areas.append("No clear task progression after resolution")
            
        return areas

class ComprehensiveRedirectionAnalyzer:
    """Complete redirection analysis system"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.semantic_analyzer = SemanticRedirectionAnalyzer()
        self.effectiveness_tracker = ResolutionEffectivenessTracker()
        
    async def connect_db(self):
        """Connect to database"""
        return await psycopg.AsyncConnection.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            row_factory=dict_row
        )
    
    async def analyze_session_redirections(self, session_id: str) -> Dict:
        """Comprehensive analysis of session redirections"""
        
        # Load session data
        session_data = await self._load_session_data(session_id)
        if not session_data:
            return {
                'session_id': session_id,
                'error': 'Session not found',
                'analysis_completed': False
            }
        
        exchanges = session_data.get('complete_chat_history', [])
        redirections = [ex for ex in exchanges if ex.get('type') == 'redirection']
        
        if not redirections:
            return {
                'session_id': session_id,
                'redirections_found': 0,
                'analysis_completed': True,
                'summary': 'No redirections found in session'
            }
        
        analysis_results = {
            'session_id': session_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'total_redirections': len(redirections),
            'total_exchanges': len(exchanges),
            'redirection_rate': len(redirections) / len(exchanges),
            'redirection_analyses': [],
            'session_patterns': {},
            'overall_assessment': {},
            'actionable_insights': [],
            'methodology': 'enhanced_semantic_analysis'
        }
        
        # Analyze each redirection
        for i, redirection in enumerate(redirections):
            redirection_analysis = await self._analyze_single_redirection(
                redirection, i, exchanges, session_data
            )
            analysis_results['redirection_analyses'].append(redirection_analysis)
        
        # Generate overall assessment
        analysis_results['overall_assessment'] = self._generate_overall_assessment(
            analysis_results['redirection_analyses']
        )
        
        # Generate actionable insights
        analysis_results['actionable_insights'] = self._generate_actionable_insights(
            analysis_results
        )
        
        return analysis_results
    
    async def _load_session_data(self, session_id: str) -> Optional[Dict]:
        """Load complete session data"""
        try:
            conn = await self.connect_db()
            async with conn.cursor() as cur:
                await cur.execute('''
                    SELECT full_conversation_data 
                    FROM session_complete_data 
                    WHERE session_id = %s
                ''', (session_id,))
                result = await cur.fetchone()
            await conn.close()
            
            return result['full_conversation_data'] if result else None
            
        except Exception as e:
            print(f"Error loading session data: {e}")
            return None
    
    async def _analyze_single_redirection(self, redirection: Dict, index: int, 
                                        exchanges: List[Dict], session_data: Dict) -> Dict:
        """Analyze a single redirection comprehensively"""
        
        context = {
            'task_progress': index / len(exchanges),
            'session_redirections': len([ex for ex in exchanges[:index] if ex.get('type') == 'redirection']),
            'time_invested': index * 30,  # Rough estimate
            'exchange_position': index,
            'total_exchanges': len(exchanges)
        }
        
        # Get redirection content
        redirection_content = redirection.get('content', '') or redirection.get('user_correction', '')
        
        # Semantic analysis
        semantic_analysis = self.semantic_analyzer.analyze_redirection_semantics(
            redirection_content, context
        )
        
        # Resolution effectiveness tracking
        post_exchanges = exchanges[index + 1:index + 6]  # Next 5 exchanges
        resolution_effectiveness = self.effectiveness_tracker.track_resolution_effectiveness(
            f"{session_data.get('session_id', 'unknown')}-{index}",
            post_exchanges
        )
        
        return {
            'redirection_id': f"{session_data.get('session_id', 'unknown')}-{index}",
            'index': index,
            'content': redirection_content,
            'timestamp': redirection.get('timestamp', datetime.now().isoformat()),
            'semantic_analysis': semantic_analysis,
            'resolution_effectiveness': resolution_effectiveness,
            'context': context,
            'post_exchanges_analyzed': len(post_exchanges)
        }
    
    def _generate_overall_assessment(self, redirection_analyses: List[Dict]) -> Dict:
        """Generate overall session assessment"""
        
        if not redirection_analyses:
            return {'assessment': 'no_redirections'}
        
        # Aggregate severity scores
        severity_scores = [analysis['semantic_analysis']['severity_assessment']['severity_score'] 
                          for analysis in redirection_analyses]
        avg_severity = sum(severity_scores) / len(severity_scores)
        
        # Count categories
        categories = [analysis['semantic_analysis']['primary_category']['primary'] 
                     for analysis in redirection_analyses]
        category_distribution = {cat: categories.count(cat) for cat in set(categories)}
        
        # Effectiveness scores
        effectiveness_scores = [analysis['resolution_effectiveness']['effectiveness_score'] 
                              for analysis in redirection_analyses
                              if analysis['resolution_effectiveness']['data_available']]
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.5
        
        # Overall session quality
        session_quality = 'excellent'
        if avg_severity > 0.7 or avg_effectiveness < 0.4:
            session_quality = 'poor'
        elif avg_severity > 0.5 or avg_effectiveness < 0.6:
            session_quality = 'fair'
        elif avg_severity > 0.3 or avg_effectiveness < 0.8:
            session_quality = 'good'
        
        return {
            'average_severity': avg_severity,
            'average_effectiveness': avg_effectiveness,
            'category_distribution': category_distribution,
            'dominant_category': max(category_distribution.items(), key=lambda x: x[1])[0],
            'session_quality': session_quality,
            'total_redirections': len(redirection_analyses)
        }
    
    def _generate_actionable_insights(self, analysis_results: Dict) -> List[Dict]:
        """Generate specific actionable insights"""
        insights = []
        
        overall = analysis_results['overall_assessment']
        dominant_category = overall.get('dominant_category', 'unknown')
        avg_severity = overall.get('average_severity', 0)
        
        # Category-specific insights
        if dominant_category == 'comprehension_gap':
            insights.append({
                'type': 'process_improvement',
                'priority': 'high',
                'insight': 'Implement mandatory comprehension confirmation before task execution',
                'implementation': 'Add step: "Let me confirm my understanding before proceeding..."'
            })
        
        if dominant_category == 'instruction_ambiguity':
            insights.append({
                'type': 'communication_enhancement',
                'priority': 'high',
                'insight': 'Users need clearer instruction templates',
                'implementation': 'Provide instruction clarity guidelines and examples'
            })
        
        # Severity-based insights
        if avg_severity > 0.6:
            insights.append({
                'type': 'critical_improvement',
                'priority': 'critical',
                'insight': 'High-severity redirections indicate systematic comprehension issues',
                'implementation': 'Implement progressive confirmation protocol for complex tasks'
            })
        
        # Pattern-based insights
        redirection_rate = analysis_results.get('redirection_rate', 0)
        if redirection_rate > 0.3:  # More than 30% redirection rate
            insights.append({
                'type': 'process_overhaul',
                'priority': 'high',
                'insight': 'High redirection rate indicates need for fundamental process improvement',
                'implementation': 'Redesign initial instruction processing and confirmation workflow'
            })
        
        return insights

# Database configuration
DB_CONFIG = {
    'host': '192.168.10.90',
    'port': 5432,
    'dbname': 'knowledge_persistence',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD', '')
}

async def test_enhanced_redirection_analysis():
    """Test enhanced redirection analysis system"""
    print("=== ENHANCED REDIRECTION ANALYSIS TEST ===")
    
    analyzer = ComprehensiveRedirectionAnalyzer(DB_CONFIG)
    
    # Test with known session
    test_session = "0daffdc5-b8f5-4243-bc7a-c6e0fdf4995a"
    
    print(f"Analyzing session: {test_session}")
    analysis = await analyzer.analyze_session_redirections(test_session)
    
    print(f"\n=== ANALYSIS RESULTS ===")
    print(f"Session ID: {analysis['session_id']}")
    print(f"Total redirections: {analysis['total_redirections']}")
    print(f"Redirection rate: {analysis['redirection_rate']:.1%}")
    print(f"Overall quality: {analysis['overall_assessment'].get('session_quality', 'unknown')}")
    
    if analysis['redirection_analyses']:
        print(f"\n=== DETAILED REDIRECTION ANALYSIS ===")
        for redir in analysis['redirection_analyses']:
            semantic = redir['semantic_analysis']
            print(f"\nRedirection {redir['index']}:")
            print(f"  Content: {redir['content'][:100]}...")
            print(f"  Category: {semantic['primary_category']['primary']}")
            print(f"  Severity: {semantic['severity_assessment']['severity_level']}")
            print(f"  Effectiveness: {redir['resolution_effectiveness']['resolution_quality']}")
    
    print(f"\n=== ACTIONABLE INSIGHTS ===")
    for insight in analysis['actionable_insights']:
        print(f"- [{insight['priority']}] {insight['insight']}")
        print(f"  Implementation: {insight['implementation']}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_redirection_analysis())