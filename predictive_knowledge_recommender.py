#!/usr/bin/env python3
"""
Predictive Knowledge Recommender for KnowledgePersistence-AI
Leverages 38 discovered patterns (59.2% confidence) for proactive recommendations
Revolutionary breakthrough prediction based on experiential → technical_discovery patterns
"""

import json
import psycopg
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PredictiveRecommendation:
    """Represents a predictive knowledge recommendation"""
    recommendation_id: str
    prediction_type: str  # breakthrough, learning_cycle, semantic, context
    confidence_score: float
    urgency_score: float  # How soon this should be acted upon
    triggered_by: List[str]
    recommended_action: str
    expected_outcome: str
    supporting_pattern: str
    metadata: Dict[str, Any]

class PredictiveKnowledgeRecommender:
    """Advanced predictive recommendation engine"""
    
    def __init__(self, db_connection_string: str, patterns_file: str):
        self.db_connection = db_connection_string
        self.patterns = self._load_patterns(patterns_file)
        self.recent_knowledge = []
        self.active_context = ""
        
    def _load_patterns(self, patterns_file: str) -> Dict[str, Any]:
        """Load discovered patterns from analysis file"""
        try:
            with open(patterns_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Patterns file not found: {patterns_file}")
            return {"patterns": []}
    
    async def connect_db(self):
        """Connect to knowledge database"""
        self.conn = psycopg.connect(self.db_connection)
        logger.info("Connected to knowledge persistence database")
    
    async def load_recent_activity(self, hours: int = 24) -> List[Dict]:
        """Load recent knowledge creation activity"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, knowledge_type, category, title, content, 
                       importance_score, created_at, context_data
                FROM knowledge_items 
                WHERE created_at >= %s
                ORDER BY created_at DESC
            """, (cutoff_time,))
            
            self.recent_knowledge = []
            for row in cur.fetchall():
                item = {
                    'id': str(row[0]),
                    'knowledge_type': row[1],
                    'category': row[2], 
                    'title': row[3],
                    'content': row[4],
                    'importance_score': row[5],
                    'created_at': row[6],
                    'context_data': row[7] or {}
                }
                self.recent_knowledge.append(item)
                
        logger.info(f"Loaded {len(self.recent_knowledge)} recent knowledge items")
        return self.recent_knowledge
    
    def predict_breakthrough_discovery(self) -> List[PredictiveRecommendation]:
        """Predict imminent breakthrough discoveries"""
        recommendations = []
        
        # Find the breakthrough pattern: experiential → technical_discovery
        breakthrough_pattern = None
        for pattern in self.patterns.get('patterns', []):
            if pattern['id'] == 'learning_cycle_experiential_to_technical_discovery':
                breakthrough_pattern = pattern
                break
        
        if not breakthrough_pattern:
            return recommendations
        
        # Look for recent experiential knowledge (trigger condition)
        recent_experiential = [
            item for item in self.recent_knowledge[-10:]  # Last 10 items
            if item['knowledge_type'] == 'experiential'
        ]
        
        for exp_item in recent_experiential:
            # Calculate time since creation
            created_at = exp_item['created_at']
            if created_at.tzinfo is not None:
                # Make timezone-aware comparison
                from datetime import timezone
                current_time = datetime.now(timezone.utc)
                time_since = (current_time - created_at).total_seconds() / 3600
            else:
                # Timezone-naive comparison
                time_since = (datetime.now() - created_at).total_seconds() / 3600
            optimal_window = breakthrough_pattern['metadata']['avg_time_gap_hours']  # ~0.055 hours = 3 minutes
            
            # If within optimal discovery window
            if time_since <= optimal_window * 2:  # 2x window for safety
                urgency = 1.0 - (time_since / (optimal_window * 2))  # Higher urgency closer to optimal time
                
                recommendation = PredictiveRecommendation(
                    recommendation_id=f"breakthrough_pred_{exp_item['id']}",
                    prediction_type="breakthrough",
                    confidence_score=breakthrough_pattern['confidence'] * 0.9,  # Conservative
                    urgency_score=urgency,
                    triggered_by=[f"Experiential knowledge: {exp_item['title']}"],
                    recommended_action="Create technical_discovery knowledge item",
                    expected_outcome=f"Technical breakthrough with ~21.6 importance boost",
                    supporting_pattern=breakthrough_pattern['id'],
                    metadata={
                        'trigger_item': exp_item,
                        'optimal_window_hours': optimal_window,
                        'time_since_trigger': time_since,
                        'expected_importance_delta': breakthrough_pattern['metadata']['avg_importance_delta'],
                        'learning_efficiency': breakthrough_pattern['metadata']['learning_efficiency']
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def predict_learning_cycle_optimization(self) -> List[PredictiveRecommendation]:
        """Predict optimal next knowledge creation based on learning cycles"""
        recommendations = []
        
        if not self.recent_knowledge:
            return recommendations
        
        # Get the most recent knowledge item
        latest_item = self.recent_knowledge[0]
        latest_type = latest_item['knowledge_type']
        
        # Find relevant learning cycle patterns
        learning_patterns = [
            p for p in self.patterns.get('patterns', [])
            if p['type'] == 'sequential' and p['metadata']['from_type'] == latest_type
        ]
        
        # Sort by significance (learning efficiency)
        learning_patterns.sort(key=lambda p: abs(p['significance']), reverse=True)
        
        for pattern in learning_patterns[:3]:  # Top 3 patterns
            to_type = pattern['metadata']['to_type']
            efficiency = pattern['metadata']['learning_efficiency']
            
            # Calculate recommendation strength
            confidence = pattern['confidence']
            significance = min(pattern['significance'] / 100.0, 1.0)  # Normalize
            
            # Higher urgency for more efficient patterns
            urgency = min(abs(efficiency) / 400.0, 1.0)  # Normalize based on max efficiency ~393
            
            recommendation = PredictiveRecommendation(
                recommendation_id=f"learning_cycle_{latest_type}_to_{to_type}",
                prediction_type="learning_cycle",
                confidence_score=confidence,
                urgency_score=urgency,
                triggered_by=[f"Recent {latest_type}: {latest_item['title']}"],
                recommended_action=f"Create {to_type} knowledge to optimize learning",
                expected_outcome=f"Learning efficiency: {efficiency:.1f}, Importance delta: {pattern['metadata']['avg_importance_delta']:.1f}",
                supporting_pattern=pattern['id'],
                metadata={
                    'trigger_item': latest_item,
                    'target_knowledge_type': to_type,
                    'learning_efficiency': efficiency,
                    'transition_count': pattern['metadata']['transition_count'],
                    'avg_time_gap_hours': pattern['metadata']['avg_time_gap_hours']
                }
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def predict_semantic_opportunities(self, context: str = "") -> List[PredictiveRecommendation]:
        """Predict knowledge needs based on semantic patterns and context"""
        recommendations = []
        
        # Get semantic cluster patterns
        semantic_patterns = [
            p for p in self.patterns.get('patterns', [])
            if p['type'] == 'semantic'
        ]
        
        # If context provided, find matching semantic clusters
        if context:
            context_words = set(context.lower().split())
            
            for pattern in semantic_patterns:
                # Check if context matches cluster themes
                themes = pattern['metadata'].get('themes', [])
                matching_themes = [theme for theme in themes if theme in context_words]
                
                if matching_themes:
                    # Calculate relevance score
                    relevance = len(matching_themes) / len(themes) if themes else 0
                    confidence = pattern['confidence'] * relevance
                    
                    dominant_type = pattern['metadata']['dominant_type']
                    dominant_category = pattern['metadata']['dominant_category']
                    
                    recommendation = PredictiveRecommendation(
                        recommendation_id=f"semantic_{pattern['id']}",
                        prediction_type="semantic",
                        confidence_score=confidence,
                        urgency_score=relevance * 0.7,  # Medium urgency for semantic matches
                        triggered_by=[f"Context match: {', '.join(matching_themes)}"],
                        recommended_action=f"Explore {dominant_type} knowledge in {dominant_category}",
                        expected_outcome=f"Access to {pattern['metadata']['cluster_size']} related knowledge items",
                        supporting_pattern=pattern['id'],
                        metadata={
                            'matching_themes': matching_themes,
                            'cluster_themes': themes,
                            'cluster_size': pattern['metadata']['cluster_size'],
                            'dominant_type': dominant_type,
                            'dominant_category': dominant_category,
                            'avg_importance': pattern['metadata']['avg_importance']
                        }
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def predict_innovation_catalysts(self) -> List[PredictiveRecommendation]:
        """Predict conditions that lead to innovation breakthroughs"""
        recommendations = []
        
        # Get innovation patterns
        innovation_patterns = [
            p for p in self.patterns.get('patterns', [])
            if p['type'] == 'innovation'
        ]
        
        for pattern in innovation_patterns:
            # Check if recent activity matches innovation prerequisites
            preceding_types = pattern['metadata'].get('preceding_types', [])
            preceding_categories = pattern['metadata'].get('preceding_categories', [])
            
            # Count recent matches
            recent_type_matches = sum(
                1 for item in self.recent_knowledge[-5:]  # Last 5 items
                if item['knowledge_type'] in preceding_types
            )
            
            recent_category_matches = sum(
                1 for item in self.recent_knowledge[-5:]
                if item['category'] in preceding_categories
            )
            
            # If we have sufficient matches, predict innovation opportunity
            if recent_type_matches >= 1 and recent_category_matches >= 1:
                match_strength = (recent_type_matches + recent_category_matches) / 4.0  # Normalize
                
                recommendation = PredictiveRecommendation(
                    recommendation_id=f"innovation_{pattern['id']}",
                    prediction_type="innovation",
                    confidence_score=pattern['confidence'] * match_strength,
                    urgency_score=min(match_strength, 0.9),  # High urgency for innovation
                    triggered_by=[f"Innovation pattern prerequisites met"],
                    recommended_action="Focus on breakthrough discovery - conditions are optimal",
                    expected_outcome=f"Potential breakthrough: {pattern['metadata']['discovery_title']}",
                    supporting_pattern=pattern['id'],
                    metadata={
                        'preceding_requirements': {
                            'types': preceding_types,
                            'categories': preceding_categories
                        },
                        'recent_matches': {
                            'type_matches': recent_type_matches,
                            'category_matches': recent_category_matches
                        },
                        'discovery_importance': pattern['metadata']['discovery_importance'],
                        'time_to_discovery_hours': pattern['metadata']['time_to_discovery_hours']
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    async def generate_comprehensive_recommendations(self, context: str = "") -> Dict[str, Any]:
        """Generate comprehensive predictive recommendations"""
        await self.connect_db()
        await self.load_recent_activity()
        
        self.active_context = context
        
        # Generate all recommendation types
        breakthrough_recs = self.predict_breakthrough_discovery()
        learning_cycle_recs = self.predict_learning_cycle_optimization()
        semantic_recs = self.predict_semantic_opportunities(context)
        innovation_recs = self.predict_innovation_catalysts()
        
        all_recommendations = breakthrough_recs + learning_cycle_recs + semantic_recs + innovation_recs
        
        # Sort by urgency and confidence
        all_recommendations.sort(
            key=lambda r: (r.urgency_score * r.confidence_score), 
            reverse=True
        )
        
        # Categorize recommendations
        categorized = {
            'breakthrough': breakthrough_recs,
            'learning_cycle': learning_cycle_recs,
            'semantic': semantic_recs,
            'innovation': innovation_recs
        }
        
        # Calculate recommendation metrics
        total_confidence = sum(r.confidence_score for r in all_recommendations)
        avg_confidence = total_confidence / len(all_recommendations) if all_recommendations else 0
        high_urgency_count = sum(1 for r in all_recommendations if r.urgency_score > 0.7)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'total_recommendations': len(all_recommendations),
            'recommendation_metrics': {
                'avg_confidence': avg_confidence,
                'high_urgency_count': high_urgency_count,
                'coverage_by_type': {rtype: len(recs) for rtype, recs in categorized.items()}
            },
            'top_recommendations': [
                {
                    'id': r.recommendation_id,
                    'type': r.prediction_type,
                    'confidence': r.confidence_score,
                    'urgency': r.urgency_score,
                    'triggered_by': r.triggered_by,
                    'action': r.recommended_action,
                    'outcome': r.expected_outcome,
                    'pattern': r.supporting_pattern,
                    'metadata': r.metadata
                }
                for r in all_recommendations[:10]  # Top 10
            ],
            'categorized_recommendations': {
                rtype: [
                    {
                        'id': r.recommendation_id,
                        'confidence': r.confidence_score,
                        'urgency': r.urgency_score,
                        'action': r.recommended_action,
                        'outcome': r.expected_outcome
                    }
                    for r in recs
                ]
                for rtype, recs in categorized.items()
            }
        }

async def main():
    """Run predictive knowledge recommendations"""
    db_connection = "postgresql://postgres:SecureKnowledgePassword2025@localhost:5432/knowledge_persistence"
    patterns_file = "/home/greg/KnowledgePersistence-AI/enhanced_pattern_analysis.json"
    
    recommender = PredictiveKnowledgeRecommender(db_connection, patterns_file)
    
    # Test different contexts
    test_contexts = [
        "implementing pattern recognition enhancement",
        "troubleshooting database connection issues", 
        "setting up MCP server configuration",
        "optimizing vector similarity search",
        ""  # No context
    ]
    
    for context in test_contexts:
        print(f"\n{'='*80}")
        print(f"PREDICTIVE RECOMMENDATIONS: {context or 'No Context'}")
        print('='*80)
        
        recommendations = await recommender.generate_comprehensive_recommendations(context)
        
        print(f"\n📊 RECOMMENDATION OVERVIEW:")
        print(f"   Total Recommendations: {recommendations['total_recommendations']}")
        print(f"   Average Confidence: {recommendations['recommendation_metrics']['avg_confidence']:.3f}")
        print(f"   High Urgency Items: {recommendations['recommendation_metrics']['high_urgency_count']}")
        
        print(f"\n🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations['top_recommendations'][:5], 1):
            print(f"   {i}. {rec['type'].upper()}: {rec['action']}")
            print(f"      Confidence: {rec['confidence']:.3f} | Urgency: {rec['urgency']:.3f}")
            print(f"      Triggered by: {', '.join(rec['triggered_by'])}")
            print(f"      Expected: {rec['outcome']}")
            print()
        
        # Save detailed recommendations for this context
        filename = f"predictive_recommendations_{context.replace(' ', '_') or 'no_context'}.json"
        with open(f"/home/greg/KnowledgePersistence-AI/{filename}", 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print(f"📁 Detailed recommendations saved: {filename}")
        print()

if __name__ == "__main__":
    asyncio.run(main())