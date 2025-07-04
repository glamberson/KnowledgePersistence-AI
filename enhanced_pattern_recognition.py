#!/usr/bin/env python3
"""
Enhanced Pattern Recognition for KnowledgePersistence-AI
Advanced algorithms leveraging 439+ knowledge items for strategic intelligence
"""

import asyncio
import json
import psycopg
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging
from sklearn.cluster import KMeans, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedPattern:
    """Enhanced pattern representation with confidence scoring"""
    pattern_id: str
    pattern_type: str  # temporal, semantic, sequential, predictive
    confidence_score: float
    significance_score: float  # Impact on strategic partnership
    related_knowledge: List[str]
    triggers: List[str]  # What contexts trigger this pattern
    outcomes: List[str]  # What this pattern predicts
    metadata: Dict[str, Any]

class AdvancedPatternRecognition:
    """Enhanced pattern recognition leveraging 439+ knowledge items"""
    
    def __init__(self, db_connection_string: str):
        self.db_connection = db_connection_string
        self.knowledge_items = []
        self.patterns = []
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    async def connect_and_load(self):
        """Connect to database and load all knowledge items"""
        self.conn = psycopg.connect(self.db_connection)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, knowledge_type, category, title, content, 
                       importance_score, created_at, context_data, retrieval_triggers
                FROM knowledge_items 
                ORDER BY created_at DESC
            """)
            
            self.knowledge_items = []
            for row in cur.fetchall():
                item = {
                    'id': str(row[0]),
                    'knowledge_type': row[1],
                    'category': row[2],
                    'title': row[3],
                    'content': row[4],
                    'importance_score': row[5],
                    'created_at': row[6],
                    'context_data': row[7] or {},
                    'retrieval_triggers': row[8] or [],
                    'combined_text': f"{row[3]} {row[4]}"  # For TF-IDF analysis
                }
                self.knowledge_items.append(item)
                
        logger.info(f"Loaded {len(self.knowledge_items)} knowledge items")
        
    def discover_semantic_clusters(self, n_clusters: int = 8) -> List[EnhancedPattern]:
        """Advanced semantic clustering using TF-IDF + K-means"""
        if len(self.knowledge_items) < 2:
            return []
            
        # Create TF-IDF matrix from combined text
        texts = [item['combined_text'] for item in self.knowledge_items]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=min(n_clusters, len(self.knowledge_items)), random_state=42)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        # Create semantic cluster patterns
        cluster_patterns = []
        for cluster_id in range(max(cluster_labels) + 1):
            cluster_items = [item for i, item in enumerate(self.knowledge_items) 
                           if cluster_labels[i] == cluster_id]
            
            if len(cluster_items) < 2:
                continue
                
            # Analyze cluster characteristics
            knowledge_types = Counter(item['knowledge_type'] for item in cluster_items)
            categories = Counter(item['category'] for item in cluster_items)
            avg_importance = np.mean([item['importance_score'] for item in cluster_items])
            
            # Calculate cluster coherence (semantic similarity)
            cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
            if len(cluster_indices) > 1:
                cluster_tfidf = tfidf_matrix[cluster_indices]
                similarity_matrix = cosine_similarity(cluster_tfidf)
                coherence_score = np.mean(similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)])
            else:
                coherence_score = 0.0
            
            # Identify cluster themes using top TF-IDF features
            cluster_center = kmeans.cluster_centers_[cluster_id]
            top_features_idx = np.argsort(cluster_center)[-10:][::-1]
            feature_names = self.vectorizer.get_feature_names_out()
            cluster_themes = [feature_names[idx] for idx in top_features_idx]
            
            pattern = EnhancedPattern(
                pattern_id=f"semantic_cluster_{cluster_id}",
                pattern_type="semantic",
                confidence_score=coherence_score,
                significance_score=avg_importance / 100.0,
                related_knowledge=[item['id'] for item in cluster_items],
                triggers=cluster_themes[:5],
                outcomes=[f"Related {ktype} knowledge" for ktype in knowledge_types.keys()],
                metadata={
                    'cluster_size': len(cluster_items),
                    'dominant_type': knowledge_types.most_common(1)[0][0],
                    'dominant_category': categories.most_common(1)[0][0],
                    'avg_importance': avg_importance,
                    'themes': cluster_themes,
                    'knowledge_types': dict(knowledge_types),
                    'categories': dict(categories)
                }
            )
            cluster_patterns.append(pattern)
            
        return cluster_patterns
    
    def discover_learning_cycles(self) -> List[EnhancedPattern]:
        """Discover learning progression patterns in knowledge creation"""
        # Sort items by creation time
        sorted_items = sorted(self.knowledge_items, key=lambda x: x['created_at'])
        
        # Track knowledge type transitions
        transitions = []
        for i in range(len(sorted_items) - 1):
            current_type = sorted_items[i]['knowledge_type']
            next_type = sorted_items[i + 1]['knowledge_type']
            time_gap = (sorted_items[i + 1]['created_at'] - sorted_items[i]['created_at']).total_seconds()
            
            transitions.append({
                'from': current_type,
                'to': next_type,
                'time_gap': time_gap,
                'from_importance': sorted_items[i]['importance_score'],
                'to_importance': sorted_items[i + 1]['importance_score'],
                'importance_delta': sorted_items[i + 1]['importance_score'] - sorted_items[i]['importance_score']
            })
        
        # Identify significant learning cycle patterns
        transition_counter = Counter((t['from'], t['to']) for t in transitions)
        
        learning_patterns = []
        for (from_type, to_type), count in transition_counter.most_common(10):
            if count >= 3:  # Minimum occurrences for significance
                pattern_transitions = [t for t in transitions if t['from'] == from_type and t['to'] == to_type]
                
                avg_time_gap = np.mean([t['time_gap'] for t in pattern_transitions])
                avg_importance_delta = np.mean([t['importance_delta'] for t in pattern_transitions])
                
                # Calculate learning efficiency (importance gain per time)
                efficiency = avg_importance_delta / (avg_time_gap / 3600) if avg_time_gap > 0 else 0
                
                pattern = EnhancedPattern(
                    pattern_id=f"learning_cycle_{from_type}_to_{to_type}",
                    pattern_type="sequential",
                    confidence_score=min(count / len(transitions), 1.0),
                    significance_score=abs(efficiency) / 10.0,  # Normalize efficiency
                    related_knowledge=[],
                    triggers=[f"Recent {from_type} knowledge creation"],
                    outcomes=[f"High probability of {to_type} knowledge creation"],
                    metadata={
                        'transition_count': count,
                        'avg_time_gap_hours': avg_time_gap / 3600,
                        'avg_importance_delta': avg_importance_delta,
                        'learning_efficiency': efficiency,
                        'from_type': from_type,
                        'to_type': to_type
                    }
                )
                learning_patterns.append(pattern)
                
        return learning_patterns
    
    def discover_predictive_triggers(self) -> List[EnhancedPattern]:
        """Discover context triggers that predict knowledge creation"""
        # Analyze retrieval triggers and their effectiveness
        trigger_outcomes = defaultdict(list)
        
        for item in self.knowledge_items:
            triggers = item.get('retrieval_triggers', [])
            for trigger in triggers:
                trigger_outcomes[trigger].append({
                    'knowledge_type': item['knowledge_type'],
                    'category': item['category'],
                    'importance': item['importance_score'],
                    'created_at': item['created_at']
                })
        
        predictive_patterns = []
        for trigger, outcomes in trigger_outcomes.items():
            if len(outcomes) >= 2:  # Minimum for pattern
                outcome_types = Counter(o['knowledge_type'] for o in outcomes)
                outcome_categories = Counter(o['category'] for o in outcomes)
                avg_importance = np.mean([o['importance'] for o in outcomes])
                
                # Calculate predictive strength
                most_common_type = outcome_types.most_common(1)[0]
                type_probability = most_common_type[1] / len(outcomes)
                
                pattern = EnhancedPattern(
                    pattern_id=f"predictive_trigger_{trigger.replace(' ', '_')}",
                    pattern_type="predictive",
                    confidence_score=type_probability,
                    significance_score=avg_importance / 100.0,
                    related_knowledge=[],
                    triggers=[trigger],
                    outcomes=[f"Creates {most_common_type[0]} knowledge"],
                    metadata={
                        'trigger': trigger,
                        'occurrences': len(outcomes),
                        'most_likely_type': most_common_type[0],
                        'type_probability': type_probability,
                        'avg_importance': avg_importance,
                        'outcome_types': dict(outcome_types),
                        'outcome_categories': dict(outcome_categories)
                    }
                )
                predictive_patterns.append(pattern)
                
        return predictive_patterns
    
    def discover_innovation_patterns(self) -> List[EnhancedPattern]:
        """Discover patterns that lead to breakthrough innovations"""
        # Find high-importance technical discoveries
        technical_discoveries = [
            item for item in self.knowledge_items 
            if item['knowledge_type'] == 'technical_discovery' and item['importance_score'] >= 70
        ]
        
        innovation_patterns = []
        for discovery in technical_discoveries:
            # Look at knowledge created in the 24 hours before this discovery
            discovery_time = discovery['created_at']
            context_window = discovery_time - timedelta(hours=24)
            
            preceding_knowledge = [
                item for item in self.knowledge_items
                if context_window <= item['created_at'] < discovery_time
            ]
            
            if len(preceding_knowledge) >= 2:
                # Analyze the pattern leading to this discovery
                preceding_types = [item['knowledge_type'] for item in preceding_knowledge]
                preceding_categories = [item['category'] for item in preceding_knowledge]
                
                pattern = EnhancedPattern(
                    pattern_id=f"innovation_pattern_{discovery['id']}",
                    pattern_type="innovation",
                    confidence_score=discovery['importance_score'] / 100.0,
                    significance_score=1.0,  # All innovations are significant
                    related_knowledge=[item['id'] for item in preceding_knowledge],
                    triggers=list(set(preceding_categories)),
                    outcomes=[f"Technical breakthrough: {discovery['title']}"],
                    metadata={
                        'discovery_title': discovery['title'],
                        'discovery_importance': discovery['importance_score'],
                        'preceding_knowledge_count': len(preceding_knowledge),
                        'preceding_types': preceding_types,
                        'preceding_categories': preceding_categories,
                        'time_to_discovery_hours': 24
                    }
                )
                innovation_patterns.append(pattern)
                
        return innovation_patterns
    
    async def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive pattern analysis report"""
        await self.connect_and_load()
        
        # Discover all pattern types
        semantic_patterns = self.discover_semantic_clusters()
        learning_patterns = self.discover_learning_cycles()
        predictive_patterns = self.discover_predictive_triggers()
        innovation_patterns = self.discover_innovation_patterns()
        
        all_patterns = semantic_patterns + learning_patterns + predictive_patterns + innovation_patterns
        
        # Calculate overall intelligence metrics
        total_knowledge = len(self.knowledge_items)
        pattern_coverage = sum(len(p.related_knowledge) for p in all_patterns) / total_knowledge if total_knowledge > 0 else 0
        avg_pattern_confidence = np.mean([p.confidence_score for p in all_patterns]) if all_patterns else 0
        strategic_value = np.mean([p.significance_score for p in all_patterns]) if all_patterns else 0
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'knowledge_base_size': total_knowledge,
            'patterns_discovered': len(all_patterns),
            'pattern_types': {
                'semantic': len(semantic_patterns),
                'learning_cycles': len(learning_patterns),
                'predictive': len(predictive_patterns),
                'innovation': len(innovation_patterns)
            },
            'intelligence_metrics': {
                'pattern_coverage': pattern_coverage,
                'avg_confidence': avg_pattern_confidence,
                'strategic_value': strategic_value,
                'pattern_density': len(all_patterns) / total_knowledge if total_knowledge > 0 else 0
            },
            'patterns': [
                {
                    'id': p.pattern_id,
                    'type': p.pattern_type,
                    'confidence': p.confidence_score,
                    'significance': p.significance_score,
                    'triggers': p.triggers,
                    'outcomes': p.outcomes,
                    'metadata': p.metadata
                }
                for p in sorted(all_patterns, key=lambda x: x.significance_score, reverse=True)
            ]
        }
        
        return analysis

async def main():
    """Run enhanced pattern recognition analysis"""
    db_connection = "postgresql://postgres:SecureKnowledgePassword2025@localhost:5432/knowledge_persistence"
    
    analyzer = AdvancedPatternRecognition(db_connection)
    analysis = await analyzer.generate_comprehensive_analysis()
    
    print("=" * 80)
    print("ENHANCED PATTERN RECOGNITION ANALYSIS")
    print("=" * 80)
    
    print(f"\n📊 KNOWLEDGE BASE INTELLIGENCE:")
    print(f"   Total Knowledge Items: {analysis['knowledge_base_size']}")
    print(f"   Patterns Discovered: {analysis['patterns_discovered']}")
    print(f"   Pattern Coverage: {analysis['intelligence_metrics']['pattern_coverage']:.2%}")
    print(f"   Average Confidence: {analysis['intelligence_metrics']['avg_confidence']:.3f}")
    print(f"   Strategic Value Score: {analysis['intelligence_metrics']['strategic_value']:.3f}")
    
    print(f"\n🔍 PATTERN DISTRIBUTION:")
    for ptype, count in analysis['pattern_types'].items():
        print(f"   {ptype.title()}: {count} patterns")
    
    print(f"\n🎯 TOP STRATEGIC PATTERNS:")
    for i, pattern in enumerate(analysis['patterns'][:5], 1):
        print(f"   {i}. {pattern['type'].title()}: {pattern['id']}")
        print(f"      Confidence: {pattern['confidence']:.3f} | Significance: {pattern['significance']:.3f}")
        print(f"      Triggers: {', '.join(pattern['triggers'][:3])}")
        print(f"      Outcomes: {', '.join(pattern['outcomes'][:2])}")
        print()
    
    # Save detailed analysis
    with open('/home/greg/KnowledgePersistence-AI/enhanced_pattern_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"📁 Detailed analysis saved to: enhanced_pattern_analysis.json")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())