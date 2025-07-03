#!/usr/bin/env python3
"""
Pattern Recognition Prototype for Knowledge Persistence System
==============================================================

This prototype demonstrates intelligent pattern recognition capabilities
for transforming stored knowledge into proactive assistance.

Features:
- Vector similarity clustering of knowledge items
- Sequential pattern mining for knowledge creation
- Context-based knowledge recommendation
- Pattern effectiveness tracking
"""

import asyncio
import json
import psycopg
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KnowledgeItem:
    """Represents a knowledge item with metadata"""
    id: str
    knowledge_type: str
    category: str
    title: str
    content: str
    embedding: List[float]
    importance_score: int
    created_at: datetime
    context_data: Dict[str, Any]

@dataclass
class PatternMatch:
    """Represents a discovered pattern"""
    pattern_id: str
    pattern_type: str
    confidence_score: float
    related_knowledge: List[str]
    metadata: Dict[str, Any]

class KnowledgePatternAnalyzer:
    """Main pattern recognition engine for knowledge analysis"""
    
    def __init__(self, db_connection_string: str):
        self.db_connection = db_connection_string
        self.knowledge_cache = {}
        self.pattern_cache = {}
        
    async def connect_db(self):
        """Establish database connection"""
        self.conn = await psycopg.AsyncConnection.connect(self.db_connection)
        logger.info("Connected to knowledge persistence database")
    
    async def load_knowledge_items(self, limit: int = 1000) -> List[KnowledgeItem]:
        """Load knowledge items from database"""
        query = """
        SELECT id, knowledge_type, category, title, content, 
               content_embedding, importance_score, created_at, context_data
        FROM knowledge_items 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (limit,))
            rows = await cur.fetchall()
            
            knowledge_items = []
            for row in rows:
                # Convert embedding from pgvector format
                embedding = []
                if row[5] is not None:
                    try:
                        # Handle pgvector format: [1.0,2.0,3.0] -> list of floats
                        embedding_str = str(row[5])
                        if embedding_str.startswith('[') and embedding_str.endswith(']'):
                            # Remove brackets and split by comma
                            embedding_str = embedding_str[1:-1]
                            if embedding_str.strip():
                                embedding = [float(x.strip()) for x in embedding_str.split(',')]
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Failed to parse embedding for item {row[0]}: {e}")
                        embedding = []
                
                item = KnowledgeItem(
                    id=str(row[0]),
                    knowledge_type=row[1],
                    category=row[2],
                    title=row[3],
                    content=row[4],
                    embedding=embedding,
                    importance_score=row[6],
                    created_at=row[7],
                    context_data=row[8] or {}
                )
                knowledge_items.append(item)
                
            logger.info(f"Loaded {len(knowledge_items)} knowledge items")
            return knowledge_items
    
    def calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
            
        # Convert to numpy arrays
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)
    
    def discover_knowledge_clusters(self, knowledge_items: List[KnowledgeItem], 
                                  similarity_threshold: float = 0.7) -> Dict[str, List[KnowledgeItem]]:
        """Discover clusters of similar knowledge items"""
        logger.info(f"Discovering knowledge clusters with threshold {similarity_threshold}")
        
        clusters = defaultdict(list)
        cluster_id = 0
        processed = set()
        
        for i, item1 in enumerate(knowledge_items):
            if item1.id in processed or not item1.embedding:
                continue
                
            cluster_key = f"cluster_{cluster_id}"
            clusters[cluster_key].append(item1)
            processed.add(item1.id)
            
            # Find similar items
            for j, item2 in enumerate(knowledge_items[i+1:], i+1):
                if item2.id in processed or not item2.embedding:
                    continue
                    
                similarity = self.calculate_cosine_similarity(item1.embedding, item2.embedding)
                
                if similarity >= similarity_threshold:
                    clusters[cluster_key].append(item2)
                    processed.add(item2.id)
            
            # Only keep clusters with multiple items
            if len(clusters[cluster_key]) > 1:
                cluster_id += 1
            else:
                del clusters[cluster_key]
                processed.remove(item1.id)
        
        logger.info(f"Discovered {len(clusters)} knowledge clusters")
        return dict(clusters)
    
    def analyze_temporal_patterns(self, knowledge_items: List[KnowledgeItem]) -> Dict[str, Any]:
        """Analyze temporal patterns in knowledge creation"""
        logger.info("Analyzing temporal patterns")
        
        # Group by time periods
        daily_counts = defaultdict(int)
        category_timelines = defaultdict(list)
        
        for item in knowledge_items:
            day_key = item.created_at.date().isoformat()
            daily_counts[day_key] += 1
            category_timelines[item.category].append(item.created_at)
        
        # Find patterns
        patterns = {
            'daily_creation_counts': dict(daily_counts),
            'category_patterns': {},
            'peak_creation_periods': self._find_peak_periods(daily_counts),
            'knowledge_type_progression': self._analyze_type_progression(knowledge_items)
        }
        
        # Analyze category patterns
        for category, timestamps in category_timelines.items():
            if len(timestamps) > 1:
                patterns['category_patterns'][category] = {
                    'count': len(timestamps),
                    'first_created': min(timestamps).isoformat(),
                    'last_created': max(timestamps).isoformat(),
                    'creation_frequency': self._calculate_frequency(timestamps)
                }
        
        return patterns
    
    def _find_peak_periods(self, daily_counts: Dict[str, int]) -> List[str]:
        """Find periods of high knowledge creation activity"""
        if not daily_counts:
            return []
            
        avg_count = sum(daily_counts.values()) / len(daily_counts)
        peak_threshold = avg_count * 1.5  # 50% above average
        
        peaks = [date for date, count in daily_counts.items() if count > peak_threshold]
        return sorted(peaks)
    
    def _analyze_type_progression(self, knowledge_items: List[KnowledgeItem]) -> Dict[str, Any]:
        """Analyze how knowledge types evolve over time"""
        type_timeline = []
        
        for item in sorted(knowledge_items, key=lambda x: x.created_at):
            type_timeline.append({
                'timestamp': item.created_at.isoformat(),
                'knowledge_type': item.knowledge_type,
                'importance': item.importance_score
            })
        
        # Find common progressions
        progressions = []
        for i in range(len(type_timeline) - 1):
            current_type = type_timeline[i]['knowledge_type']
            next_type = type_timeline[i + 1]['knowledge_type']
            if current_type != next_type:
                progressions.append(f"{current_type} -> {next_type}")
        
        progression_counts = Counter(progressions)
        
        return {
            'timeline': type_timeline,
            'common_progressions': dict(progression_counts.most_common(5)),
            'total_progressions': len(progressions)
        }
    
    def _calculate_frequency(self, timestamps: List[datetime]) -> float:
        """Calculate average frequency between knowledge creation events"""
        if len(timestamps) < 2:
            return 0.0
            
        sorted_times = sorted(timestamps)
        intervals = []
        
        for i in range(1, len(sorted_times)):
            interval = (sorted_times[i] - sorted_times[i-1]).total_seconds() / 3600  # hours
            intervals.append(interval)
        
        return sum(intervals) / len(intervals) if intervals else 0.0
    
    def predict_knowledge_needs(self, current_context: str, 
                               knowledge_items: List[KnowledgeItem]) -> List[PatternMatch]:
        """Predict knowledge needs based on current context"""
        logger.info(f"Predicting knowledge needs for context: {current_context}")
        
        predictions = []
        
        # Simple keyword-based matching for prototype
        context_words = current_context.lower().split()
        
        for item in knowledge_items:
            # Calculate relevance score
            content_words = (item.title + " " + item.content).lower().split()
            common_words = set(context_words) & set(content_words)
            
            if common_words:
                relevance_score = len(common_words) / len(context_words)
                relevance_score *= (item.importance_score / 100.0)  # Weight by importance
                
                if relevance_score > 0.3:  # Threshold for relevance
                    prediction = PatternMatch(
                        pattern_id=f"context_match_{item.id}",
                        pattern_type="context_similarity",
                        confidence_score=relevance_score,
                        related_knowledge=[item.id],
                        metadata={
                            'title': item.title,
                            'category': item.category,
                            'importance': item.importance_score,
                            'common_keywords': list(common_words)
                        }
                    )
                    predictions.append(prediction)
        
        # Sort by confidence
        predictions.sort(key=lambda x: x.confidence_score, reverse=True)
        return predictions[:10]  # Return top 10
    
    async def store_pattern_discovery(self, patterns: Dict[str, Any]) -> bool:
        """Store discovered patterns for future reference"""
        try:
            # Store in knowledge_items as a special pattern discovery entry
            insert_query = """
            INSERT INTO knowledge_items 
            (knowledge_type, category, title, content, importance_score, context_data)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            content = json.dumps(patterns, indent=2)
            title = f"Pattern Discovery - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            async with self.conn.cursor() as cur:
                await cur.execute(insert_query, (
                    'technical_discovery',
                    'pattern_analysis',
                    title,
                    content,
                    85,  # High importance for pattern discoveries
                    {'pattern_type': 'automated_discovery', 'tool': 'pattern_recognition_prototype'}
                ))
                await self.conn.commit()
            
            logger.info("Stored pattern discovery in knowledge base")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store pattern discovery: {e}")
            return False

class PatternRecognitionDemo:
    """Demonstration of pattern recognition capabilities"""
    
    def __init__(self, db_connection_string: str):
        self.analyzer = KnowledgePatternAnalyzer(db_connection_string)
    
    async def run_full_analysis(self):
        """Run complete pattern recognition analysis"""
        logger.info("Starting comprehensive pattern recognition analysis")
        
        # Connect to database
        await self.analyzer.connect_db()
        
        # Load knowledge items
        knowledge_items = await self.analyzer.load_knowledge_items()
        
        if not knowledge_items:
            logger.warning("No knowledge items found in database")
            return
        
        # Discover clusters
        clusters = self.analyzer.discover_knowledge_clusters(knowledge_items)
        
        # Analyze temporal patterns
        temporal_patterns = self.analyzer.analyze_temporal_patterns(knowledge_items)
        
        # Test context prediction
        test_contexts = [
            "setting up MCP server configuration",
            "troubleshooting database connection issues", 
            "implementing knowledge persistence hooks",
            "optimizing vector similarity search"
        ]
        
        context_predictions = {}
        for context in test_contexts:
            predictions = self.analyzer.predict_knowledge_needs(context, knowledge_items)
            context_predictions[context] = predictions
        
        # Compile comprehensive analysis
        analysis_results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'knowledge_overview': {
                'total_items': len(knowledge_items),
                'knowledge_types': list(set(item.knowledge_type for item in knowledge_items)),
                'categories': list(set(item.category for item in knowledge_items)),
                'avg_importance': sum(item.importance_score for item in knowledge_items) / len(knowledge_items)
            },
            'cluster_analysis': {
                'cluster_count': len(clusters),
                'largest_cluster_size': max(len(items) for items in clusters.values()) if clusters else 0,
                'cluster_details': {
                    cluster_id: {
                        'size': len(items),
                        'categories': list(set(item.category for item in items)),
                        'avg_importance': sum(item.importance_score for item in items) / len(items),
                        'sample_titles': [item.title for item in items[:3]]
                    }
                    for cluster_id, items in clusters.items()
                }
            },
            'temporal_patterns': temporal_patterns,
            'context_predictions': {
                context: [
                    {
                        'confidence': pred.confidence_score,
                        'title': pred.metadata['title'],
                        'category': pred.metadata['category'],
                        'keywords': pred.metadata['common_keywords']
                    }
                    for pred in predictions[:3]  # Top 3 predictions
                ]
                for context, predictions in context_predictions.items()
            }
        }
        
        # Store analysis results
        await self.analyzer.store_pattern_discovery(analysis_results)
        
        # Display results
        self.display_analysis_results(analysis_results)
        
        return analysis_results
    
    def display_analysis_results(self, results: Dict[str, Any]):
        """Display analysis results in formatted output"""
        print("\n" + "="*80)
        print("KNOWLEDGE PATTERN RECOGNITION ANALYSIS RESULTS")
        print("="*80)
        
        # Overview
        overview = results['knowledge_overview']
        print(f"\n📊 KNOWLEDGE OVERVIEW:")
        print(f"   Total Items: {overview['total_items']}")
        print(f"   Knowledge Types: {', '.join(overview['knowledge_types'])}")
        print(f"   Categories: {', '.join(overview['categories'])}")
        print(f"   Average Importance: {overview['avg_importance']:.1f}")
        
        # Clusters
        cluster_analysis = results['cluster_analysis']
        print(f"\n🔍 CLUSTER ANALYSIS:")
        print(f"   Clusters Discovered: {cluster_analysis['cluster_count']}")
        print(f"   Largest Cluster Size: {cluster_analysis['largest_cluster_size']}")
        
        for cluster_id, details in cluster_analysis['cluster_details'].items():
            print(f"\n   {cluster_id.upper()}:")
            print(f"     Size: {details['size']} items")
            print(f"     Categories: {', '.join(details['categories'])}")
            print(f"     Avg Importance: {details['avg_importance']:.1f}")
            print(f"     Sample Titles: {', '.join(details['sample_titles'])}")
        
        # Temporal patterns
        temporal = results['temporal_patterns']
        print(f"\n⏰ TEMPORAL PATTERNS:")
        print(f"   Peak Creation Periods: {', '.join(temporal['peak_creation_periods'])}")
        print(f"   Common Knowledge Type Progressions:")
        for progression, count in temporal['knowledge_type_progression']['common_progressions'].items():
            print(f"     {progression}: {count} times")
        
        # Context predictions
        print(f"\n🎯 CONTEXT PREDICTIONS:")
        for context, predictions in results['context_predictions'].items():
            print(f"\n   Context: '{context}'")
            for i, pred in enumerate(predictions, 1):
                print(f"     {i}. {pred['title']} (confidence: {pred['confidence']:.2f})")
                print(f"        Category: {pred['category']}, Keywords: {', '.join(pred['keywords'])}")
        
        print("\n" + "="*80)

async def main():
    """Main demonstration function"""
    # Database connection string
    db_connection = "postgresql://postgres:SecureKnowledgePassword2025@192.168.10.90:5432/knowledge_persistence"
    
    # Run demonstration
    demo = PatternRecognitionDemo(db_connection)
    await demo.run_full_analysis()

if __name__ == "__main__":
    asyncio.run(main())