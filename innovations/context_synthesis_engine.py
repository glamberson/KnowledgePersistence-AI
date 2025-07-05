"""
Context Synthesis Engine - Proof of Concept
===========================================

This module implements the active context synthesis system that creates
hierarchical summaries and context digests for efficient session initialization.
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeItem:
    """Represents a knowledge item from the database"""
    id: str
    knowledge_type: str
    content: str
    importance_score: int
    created_at: datetime
    embedding: Optional[np.ndarray] = None
    access_count: int = 0
    context_data: Dict[str, Any] = None


@dataclass
class ContextDigest:
    """Represents a synthesized context digest"""
    digest_level: int  # 1=minute, 2=hourly, 3=daily, 4=weekly
    time_range: Tuple[datetime, datetime]
    content: str
    source_items: List[str]  # knowledge item IDs
    digest_type: str  # 'summary', 'key_insights', 'patterns'
    embedding: Optional[np.ndarray] = None
    quality_score: float = 0.0


class ContextSynthesizer:
    """Creates hierarchical summaries of knowledge items"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client  # For actual summarization
        self.compression_ratios = {
            1: 0.8,   # Minute-level: 80% of original
            2: 0.5,   # Hourly: 50% of original  
            3: 0.2,   # Daily: 20% of original
            4: 0.05   # Weekly: 5% of original
        }
    
    async def synthesize(self, 
                        knowledge_items: List[KnowledgeItem], 
                        digest_level: int,
                        digest_type: str = 'summary') -> ContextDigest:
        """Synthesize knowledge items into a digest"""
        
        # Sort by importance and recency
        sorted_items = sorted(
            knowledge_items,
            key=lambda x: (x.importance_score * 0.7 + 
                          (100 - (datetime.now() - x.created_at).days) * 0.3),
            reverse=True
        )
        
        # Calculate target size
        total_content_size = sum(len(item.content) for item in sorted_items)
        target_size = int(total_content_size * self.compression_ratios[digest_level])
        
        if digest_type == 'summary':
            content = await self._create_summary(sorted_items, target_size)
        elif digest_type == 'key_insights':
            content = await self._extract_insights(sorted_items, target_size)
        elif digest_type == 'patterns':
            content = await self._identify_patterns(sorted_items, target_size)
        else:
            raise ValueError(f"Unknown digest type: {digest_type}")
        
        # Calculate time range
        if sorted_items:
            time_range = (
                min(item.created_at for item in sorted_items),
                max(item.created_at for item in sorted_items)
            )
        else:
            time_range = (datetime.now(), datetime.now())
        
        return ContextDigest(
            digest_level=digest_level,
            time_range=time_range,
            content=content,
            source_items=[item.id for item in sorted_items],
            digest_type=digest_type,
            quality_score=self._calculate_quality_score(sorted_items, content)
        )
    
    async def _create_summary(self, items: List[KnowledgeItem], target_size: int) -> str:
        """Create a coherent summary of knowledge items"""
        if self.llm_client:
            # Use LLM for intelligent summarization
            prompt = self._build_summary_prompt(items, target_size)
            return await self.llm_client.complete(prompt)
        else:
            # Fallback: Simple concatenation with truncation
            summary_parts = []
            current_size = 0
            
            for item in items:
                if current_size >= target_size:
                    break
                    
                # Take proportional amount from each item
                item_allocation = int(target_size * (item.importance_score / 100))
                item_summary = item.content[:item_allocation]
                summary_parts.append(f"[{item.knowledge_type}] {item_summary}")
                current_size += len(item_summary)
            
            return "\n\n".join(summary_parts)
    
    async def _extract_insights(self, items: List[KnowledgeItem], target_size: int) -> str:
        """Extract key insights from knowledge items"""
        insights = []
        
        # Group by knowledge type
        type_groups = {}
        for item in items:
            if item.knowledge_type not in type_groups:
                type_groups[item.knowledge_type] = []
            type_groups[item.knowledge_type].append(item)
        
        # Extract insights per type
        for knowledge_type, type_items in type_groups.items():
            if knowledge_type == 'experiential':
                # Focus on learned lessons
                for item in type_items[:3]:  # Top 3
                    insights.append(f"LEARNED: {item.content[:100]}...")
                    
            elif knowledge_type == 'technical_discovery':
                # Focus on solutions
                for item in type_items[:3]:
                    insights.append(f"SOLUTION: {item.content[:100]}...")
                    
            elif knowledge_type == 'relational':
                # Focus on patterns
                for item in type_items[:2]:
                    insights.append(f"PATTERN: {item.content[:100]}...")
        
        return "\n".join(insights)[:target_size]
    
    async def _identify_patterns(self, items: List[KnowledgeItem], target_size: int) -> str:
        """Identify patterns across knowledge items"""
        patterns = []
        
        # Temporal patterns
        time_clusters = self._cluster_by_time(items)
        for cluster_time, cluster_items in time_clusters.items():
            if len(cluster_items) > 3:
                patterns.append(
                    f"TEMPORAL CLUSTER ({cluster_time}): "
                    f"{len(cluster_items)} related items"
                )
        
        # Type transition patterns
        transitions = self._analyze_type_transitions(items)
        for transition, count in transitions.most_common(3):
            patterns.append(
                f"TRANSITION PATTERN: {transition[0]} → {transition[1]} "
                f"(occurred {count} times)"
            )
        
        # Importance spikes
        importance_spikes = [
            item for item in items 
            if item.importance_score > 85
        ]
        if importance_spikes:
            patterns.append(
                f"HIGH IMPORTANCE: {len(importance_spikes)} critical items identified"
            )
        
        return "\n".join(patterns)[:target_size]
    
    def _cluster_by_time(self, items: List[KnowledgeItem], 
                        window_minutes: int = 30) -> Dict[str, List[KnowledgeItem]]:
        """Cluster items by temporal proximity"""
        clusters = {}
        
        for item in sorted(items, key=lambda x: x.created_at):
            cluster_found = False
            
            for cluster_time, cluster_items in clusters.items():
                cluster_dt = datetime.fromisoformat(cluster_time)
                if abs((item.created_at - cluster_dt).total_seconds()) < window_minutes * 60:
                    cluster_items.append(item)
                    cluster_found = True
                    break
            
            if not cluster_found:
                clusters[item.created_at.isoformat()] = [item]
        
        return clusters
    
    def _analyze_type_transitions(self, items: List[KnowledgeItem]) -> Dict[Tuple[str, str], int]:
        """Analyze transitions between knowledge types"""
        from collections import Counter
        
        transitions = Counter()
        sorted_items = sorted(items, key=lambda x: x.created_at)
        
        for i in range(len(sorted_items) - 1):
            current_type = sorted_items[i].knowledge_type
            next_type = sorted_items[i + 1].knowledge_type
            transitions[(current_type, next_type)] += 1
        
        return transitions
    
    def _calculate_quality_score(self, items: List[KnowledgeItem], digest: str) -> float:
        """Calculate quality score for a digest"""
        if not items:
            return 0.0
        
        # Factors:
        # 1. Coverage: How many high-importance items are represented
        # 2. Compression: How well we compressed while maintaining information
        # 3. Recency: Bias toward recent information
        
        high_importance_items = [i for i in items if i.importance_score > 70]
        coverage_score = len(high_importance_items) / max(len(items), 1)
        
        original_size = sum(len(i.content) for i in items)
        compression_score = 1.0 - (len(digest) / max(original_size, 1))
        
        recency_scores = []
        now = datetime.now()
        for item in items:
            age_days = (now - item.created_at).days
            recency_scores.append(1.0 / (1.0 + age_days * 0.1))
        recency_score = np.mean(recency_scores) if recency_scores else 0.0
        
        return (coverage_score * 0.4 + compression_score * 0.3 + recency_score * 0.3)
    
    def _build_summary_prompt(self, items: List[KnowledgeItem], target_size: int) -> str:
        """Build prompt for LLM summarization"""
        prompt = f"""Synthesize the following {len(items)} knowledge items into a coherent summary.
Target size: approximately {target_size} characters.
Preserve the most important insights while maintaining narrative flow.

Knowledge items:
"""
        for item in items:
            prompt += f"\n[{item.knowledge_type}] (importance: {item.importance_score}): {item.content}\n"
        
        prompt += "\nSynthesized summary:"
        return prompt


class HierarchicalDigestManager:
    """Manages the creation and maintenance of hierarchical digests"""
    
    def __init__(self, db_connection, synthesizer: ContextSynthesizer):
        self.db = db_connection
        self.synthesizer = synthesizer
        self.digest_intervals = {
            1: timedelta(minutes=5),
            2: timedelta(hours=1),
            3: timedelta(days=1),
            4: timedelta(weeks=1)
        }
    
    async def process_digest_level(self, level: int, project_id: str):
        """Process digests for a specific level"""
        interval = self.digest_intervals[level]
        now = datetime.now()
        
        # Find unprocessed time windows
        last_digest_time = await self._get_last_digest_time(level, project_id)
        if not last_digest_time:
            last_digest_time = now - timedelta(days=30)  # Start from 30 days ago
        
        current_window_start = last_digest_time
        
        while current_window_start + interval < now:
            window_end = current_window_start + interval
            
            # Get knowledge items in this window
            if level == 1:
                # For minute-level, use raw knowledge items
                items = await self._get_knowledge_items_in_range(
                    project_id, current_window_start, window_end
                )
            else:
                # For higher levels, use lower-level digests
                items = await self._get_lower_level_digests(
                    project_id, level - 1, current_window_start, window_end
                )
            
            if items:
                # Create digests for each type
                for digest_type in ['summary', 'key_insights', 'patterns']:
                    digest = await self.synthesizer.synthesize(
                        items, level, digest_type
                    )
                    await self._store_digest(digest, project_id)
            
            current_window_start = window_end
    
    async def _get_last_digest_time(self, level: int, project_id: str) -> Optional[datetime]:
        """Get the timestamp of the last digest at this level"""
        # Implementation depends on database
        pass
    
    async def _get_knowledge_items_in_range(self, project_id: str, 
                                           start: datetime, 
                                           end: datetime) -> List[KnowledgeItem]:
        """Get knowledge items within a time range"""
        # Implementation depends on database
        pass
    
    async def _get_lower_level_digests(self, project_id: str, 
                                      level: int,
                                      start: datetime, 
                                      end: datetime) -> List[KnowledgeItem]:
        """Get digests from lower level to synthesize"""
        # Implementation depends on database
        pass
    
    async def _store_digest(self, digest: ContextDigest, project_id: str):
        """Store a digest in the database"""
        # Implementation depends on database
        pass


class ContextInitOptimizer:
    """Optimizes context initialization for new sessions"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.token_overhead = 100  # Reserved for system prompts
    
    async def prepare_optimal_context(self, 
                                    session_type: str,
                                    project_id: str,
                                    token_budget: int = 4000) -> str:
        """Prepare optimal context for session initialization"""
        available_tokens = token_budget - self.token_overhead
        
        # Get relevant digests
        digests = await self._get_relevant_digests(session_type, project_id)
        
        # Score and rank digests
        scored_digests = await self._score_digests(digests, session_type)
        
        # Pack digests into token budget
        packed_context = await self._pack_into_budget(scored_digests, available_tokens)
        
        return packed_context
    
    async def _get_relevant_digests(self, session_type: str, 
                                   project_id: str) -> List[ContextDigest]:
        """Get digests relevant to session type"""
        # Implementation: Query database for relevant digests
        pass
    
    async def _score_digests(self, digests: List[ContextDigest], 
                           session_type: str) -> List[Tuple[ContextDigest, float]]:
        """Score digests for relevance to session type"""
        scored = []
        
        for digest in digests:
            score = 0.0
            
            # Recency score
            age_hours = (datetime.now() - digest.time_range[1]).total_seconds() / 3600
            recency_score = 1.0 / (1.0 + age_hours * 0.01)
            score += recency_score * 0.3
            
            # Quality score
            score += digest.quality_score * 0.3
            
            # Type relevance score
            if session_type == 'technical' and digest.digest_type == 'patterns':
                score += 0.4
            elif session_type == 'planning' and digest.digest_type == 'key_insights':
                score += 0.4
            else:
                score += 0.2
            
            scored.append((digest, score))
        
        return sorted(scored, key=lambda x: x[1], reverse=True)
    
    async def _pack_into_budget(self, scored_digests: List[Tuple[ContextDigest, float]], 
                              token_budget: int) -> str:
        """Pack highest-scoring digests into token budget"""
        packed_parts = []
        used_tokens = 0
        
        for digest, score in scored_digests:
            # Estimate tokens (rough: 1 token ≈ 4 characters)
            digest_tokens = len(digest.content) // 4
            
            if used_tokens + digest_tokens <= token_budget:
                packed_parts.append(f"[{digest.digest_type.upper()}]\n{digest.content}")
                used_tokens += digest_tokens
            else:
                # Try to fit partial digest
                remaining_tokens = token_budget - used_tokens
                if remaining_tokens > 50:  # Minimum useful size
                    partial_content = digest.content[:remaining_tokens * 4]
                    packed_parts.append(
                        f"[{digest.digest_type.upper()} - PARTIAL]\n{partial_content}..."
                    )
                break
        
        return "\n\n---\n\n".join(packed_parts)


# Example usage
async def main():
    """Example of using the Context Synthesis Engine"""
    
    # Create sample knowledge items
    items = [
        KnowledgeItem(
            id="1",
            knowledge_type="experiential",
            content="Discovered that MCP servers require absolute paths in Node.js",
            importance_score=85,
            created_at=datetime.now() - timedelta(hours=2)
        ),
        KnowledgeItem(
            id="2", 
            knowledge_type="technical_discovery",
            content="Solution: Use path.resolve() for all file operations in MCP",
            importance_score=90,
            created_at=datetime.now() - timedelta(hours=1)
        ),
        KnowledgeItem(
            id="3",
            knowledge_type="procedural", 
            content="Always validate environment variables before MCP server start",
            importance_score=75,
            created_at=datetime.now() - timedelta(minutes=30)
        )
    ]
    
    # Create synthesizer and generate digest
    synthesizer = ContextSynthesizer()
    
    # Create hourly summary
    summary_digest = await synthesizer.synthesize(items, digest_level=2, digest_type='summary')
    print(f"Summary Digest:\n{summary_digest.content}\n")
    
    # Extract insights
    insights_digest = await synthesizer.synthesize(items, digest_level=2, digest_type='key_insights')
    print(f"Insights:\n{insights_digest.content}\n")
    
    # Identify patterns
    patterns_digest = await synthesizer.synthesize(items, digest_level=2, digest_type='patterns')
    print(f"Patterns:\n{patterns_digest.content}\n")


if __name__ == "__main__":
    asyncio.run(main())
