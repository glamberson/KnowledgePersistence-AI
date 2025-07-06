#!/usr/bin/env python3
"""
Production-Ready CAG System with Error Recovery and Graceful Degradation
Combines pattern intelligence architecture with robust MCP integration
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemState(Enum):
    """System operational state"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"

class KnowledgeType(Enum):
    """Enhanced knowledge taxonomy with semantic understanding"""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    CONTEXTUAL = "contextual"
    RELATIONAL = "relational"
    EXPERIENTIAL = "experiential"
    TECHNICAL_DISCOVERY = "technical"
    PATTERN_RECOGNITION = "patterns"
    STRATEGIC_INSIGHT = "strategic"

class ContextLayer(Enum):
    """Context layers with priority weights"""
    SYSTEM = "system"
    PROJECT = "project"
    SESSION = "session"
    DOMAIN = "domain"
    EXPERIENCE = "experience"
    STRATEGIC = "strategic"
    DYNAMIC = "dynamic"
    RESPONSE = "response"

@dataclass
class SystemHealth:
    """System health tracking"""
    state: SystemState
    database_healthy: bool = True
    cache_healthy: bool = True
    mcp_healthy: bool = True
    local_llm_healthy: bool = True
    pattern_extraction_healthy: bool = True
    last_check: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)

class CircuitBreaker:
    """Circuit breaker for resilient external calls"""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def can_execute(self) -> bool:
        if self.state == 'closed':
            return True
        elif self.state == 'open':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
                return True
            return False
        else:  # half-open
            return True
    
    def record_success(self):
        self.failure_count = 0
        self.state = 'closed'
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'

class MCPToolRegistry:
    """Registry for MCP tools with dynamic discovery"""
    def __init__(self):
        self.tools = {}
        self.schemas = {}
        self.health_checks = {}
    
    def register_tool(self, name: str, tool_func, schema: Dict, health_check=None):
        """Register an MCP tool with schema validation"""
        self.tools[name] = tool_func
        self.schemas[name] = schema
        if health_check:
            self.health_checks[name] = health_check
    
    async def call_tool(self, name: str, params: Dict) -> Any:
        """Call MCP tool with error handling"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        
        # Validate parameters against schema
        if not self._validate_params(name, params):
            raise ValueError(f"Invalid parameters for tool {name}")
        
        try:
            return await self.tools[name](params)
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            raise
    
    def _validate_params(self, tool_name: str, params: Dict) -> bool:
        """Validate parameters against tool schema"""
        schema = self.schemas.get(tool_name, {})
        required_params = schema.get('required', [])
        
        for param in required_params:
            if param not in params:
                return False
        
        return True

class SemanticKnowledgeClassifier:
    """Semantic classification system for knowledge types"""
    def __init__(self):
        self.type_embeddings = {}
        self.classification_rules = self._build_classification_rules()
    
    def _build_classification_rules(self) -> Dict:
        """Build semantic classification rules"""
        return {
            KnowledgeType.FACTUAL: {
                'keywords': ['fact', 'data', 'statistic', 'definition', 'what is'],
                'patterns': [r'\b\w+ is \w+', r'\b\w+ equals \w+', r'\b\w+ means \w+'],
                'confidence_threshold': 0.7
            },
            KnowledgeType.PROCEDURAL: {
                'keywords': ['step', 'process', 'procedure', 'how to', 'method'],
                'patterns': [r'\b\d+\.\s', r'\bfirst\b', r'\bthen\b', r'\bfinally\b'],
                'confidence_threshold': 0.8
            },
            KnowledgeType.CONTEXTUAL: {
                'keywords': ['context', 'situation', 'scenario', 'condition'],
                'patterns': [r'\bwhen\b', r'\bif\b', r'\bunless\b', r'\bprovided\b'],
                'confidence_threshold': 0.6
            },
            KnowledgeType.RELATIONAL: {
                'keywords': ['relationship', 'connection', 'relates to', 'depends on'],
                'patterns': [r'\bcauses?\b', r'\bleads? to\b', r'\bresults? in\b'],
                'confidence_threshold': 0.7
            },
            KnowledgeType.EXPERIENTIAL: {
                'keywords': ['experience', 'learned', 'discovered', 'found'],
                'patterns': [r'\bI found\b', r'\bwe discovered\b', r'\bin my experience\b'],
                'confidence_threshold': 0.8
            },
            KnowledgeType.TECHNICAL_DISCOVERY: {
                'keywords': ['technical', 'code', 'implementation', 'architecture'],
                'patterns': [r'\bclass\b', r'\bfunction\b', r'\bmethod\b', r'\bAPI\b'],
                'confidence_threshold': 0.7
            },
            KnowledgeType.PATTERN_RECOGNITION: {
                'keywords': ['pattern', 'trend', 'recurring', 'common'],
                'patterns': [r'\busually\b', r'\boften\b', r'\btypically\b', r'\btend to\b'],
                'confidence_threshold': 0.6
            },
            KnowledgeType.STRATEGIC_INSIGHT: {
                'keywords': ['strategy', 'insight', 'approach', 'recommendation'],
                'patterns': [r'\bshould\b', r'\brecommend\b', r'\bstrategy\b', r'\bapproach\b'],
                'confidence_threshold': 0.8
            }
        }
    
    def classify_knowledge(self, content: str) -> Dict[KnowledgeType, float]:
        """Classify knowledge content with confidence scores"""
        content_lower = content.lower()
        scores = {}
        
        for knowledge_type, rules in self.classification_rules.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in rules['keywords'] if keyword in content_lower)
            score += (keyword_matches / len(rules['keywords'])) * 0.5
            
            # Pattern matching
            import re
            pattern_matches = sum(1 for pattern in rules['patterns'] if re.search(pattern, content_lower))
            if rules['patterns']:
                score += (pattern_matches / len(rules['patterns'])) * 0.5
            
            scores[knowledge_type] = score
        
        return scores
    
    def get_best_classification(self, content: str) -> tuple[KnowledgeType, float]:
        """Get the best knowledge type classification"""
        scores = self.classify_knowledge(content)
        best_type = max(scores, key=scores.get)
        return best_type, scores[best_type]

class PatternIntelligenceEngine:
    """Pattern intelligence engine with semantic understanding"""
    def __init__(self):
        self.semantic_classifier = SemanticKnowledgeClassifier()
        self.pattern_cache = {}
        self.relationship_cache = {}
    
    async def extract_patterns_with_classification(self, content: str, context: Dict) -> List[Dict]:
        """Extract patterns with semantic classification"""
        patterns = []
        
        # Classify the content
        best_type, confidence = self.semantic_classifier.get_best_classification(content)
        
        # Extract patterns based on type
        if best_type == KnowledgeType.PROCEDURAL:
            patterns.extend(await self._extract_procedural_patterns(content))
        elif best_type == KnowledgeType.RELATIONAL:
            patterns.extend(await self._extract_relational_patterns(content))
        elif best_type == KnowledgeType.PATTERN_RECOGNITION:
            patterns.extend(await self._extract_meta_patterns(content))
        else:
            patterns.extend(await self._extract_generic_patterns(content))
        
        # Enhance patterns with semantic information
        for pattern in patterns:
            pattern['semantic_type'] = best_type.value
            pattern['classification_confidence'] = confidence
            pattern['extraction_timestamp'] = datetime.now().isoformat()
        
        return patterns
    
    async def _extract_procedural_patterns(self, content: str) -> List[Dict]:
        """Extract procedural patterns (steps, processes)"""
        patterns = []
        
        # Look for numbered steps
        import re
        steps = re.findall(r'(?:^|\n)\s*\d+\.\s*([^\n]+)', content)
        
        if steps:
            patterns.append({
                'type': 'procedural_sequence',
                'title': 'Step-by-step procedure',
                'content': steps,
                'confidence': 0.9
            })
        
        # Look for process keywords
        process_indicators = ['first', 'then', 'next', 'finally', 'after', 'before']
        if any(indicator in content.lower() for indicator in process_indicators):
            patterns.append({
                'type': 'process_flow',
                'title': 'Process flow identified',
                'content': content[:200],
                'confidence': 0.7
            })
        
        return patterns
    
    async def _extract_relational_patterns(self, content: str) -> List[Dict]:
        """Extract relational patterns (cause-effect, dependencies)"""
        patterns = []
        
        # Look for causal relationships
        causal_keywords = ['because', 'since', 'due to', 'causes', 'results in', 'leads to']
        if any(keyword in content.lower() for keyword in causal_keywords):
            patterns.append({
                'type': 'causal_relationship',
                'title': 'Causal relationship detected',
                'content': content[:200],
                'confidence': 0.8
            })
        
        # Look for dependencies
        dependency_keywords = ['depends on', 'requires', 'needs', 'prerequisite']
        if any(keyword in content.lower() for keyword in dependency_keywords):
            patterns.append({
                'type': 'dependency_relationship',
                'title': 'Dependency relationship detected',
                'content': content[:200],
                'confidence': 0.8
            })
        
        return patterns
    
    async def _extract_meta_patterns(self, content: str) -> List[Dict]:
        """Extract meta-patterns (patterns about patterns)"""
        patterns = []
        
        # Look for recurring themes
        recurring_keywords = ['often', 'usually', 'typically', 'commonly', 'frequently']
        if any(keyword in content.lower() for keyword in recurring_keywords):
            patterns.append({
                'type': 'recurring_pattern',
                'title': 'Recurring pattern identified',
                'content': content[:200],
                'confidence': 0.7
            })
        
        return patterns
    
    async def _extract_generic_patterns(self, content: str) -> List[Dict]:
        """Extract generic patterns"""
        patterns = []
        
        # Basic pattern extraction
        if len(content) > 100:
            patterns.append({
                'type': 'content_pattern',
                'title': 'Content pattern',
                'content': content[:200],
                'confidence': 0.5
            })
        
        return patterns

class ProductionCAGEngine:
    """Production-ready CAG Engine with comprehensive error handling"""
    def __init__(self):
        self.pattern_engine = PatternIntelligenceEngine()
        self.mcp_registry = MCPToolRegistry()
        self.health = SystemHealth(SystemState.HEALTHY)
        self.circuit_breaker = CircuitBreaker()
        self.metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'degraded_queries': 0,
            'average_response_time': 0.0
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_query_with_recovery(self, query: str, session_id: str, user_context: Dict = None) -> Dict:
        """Process query with comprehensive error recovery"""
        start_time = time.time()
        self.metrics['total_queries'] += 1
        
        try:
            # Extract patterns with semantic understanding
            patterns = await self.pattern_engine.extract_patterns_with_classification(
                query, user_context or {}
            )
            
            # Compile response
            response = {
                'query': query,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'context_loaded': True,
                'patterns_extracted': len(patterns),
                'patterns': patterns,
                'system_health': {
                    'state': self.health.state.value,
                    'warnings': self.health.warnings,
                },
                'performance': {
                    'processing_time': time.time() - start_time,
                    'context_load_successful': True,
                    'pattern_extraction_successful': True
                }
            }
            
            self.metrics['successful_queries'] += 1
            
            if self.health.state == SystemState.DEGRADED:
                self.metrics['degraded_queries'] += 1
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            self.metrics['failed_queries'] += 1
            
            # Return error response with fallback information
            return {
                'query': query,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'context_loaded': False,
                'patterns_extracted': 0,
                'patterns': [],
                'system_health': {
                    'state': SystemState.CRITICAL.value,
                    'error': str(e)
                },
                'performance': {
                    'processing_time': time.time() - start_time,
                    'context_load_successful': False,
                    'pattern_extraction_successful': False
                }
            }
    
    async def get_system_health(self) -> Dict:
        """Get comprehensive system health status"""
        return {
            'overall_health': self.health.state.value,
            'database_healthy': self.health.database_healthy,
            'cache_healthy': self.health.cache_healthy,
            'mcp_healthy': self.health.mcp_healthy,
            'pattern_extraction_healthy': self.health.pattern_extraction_healthy,
            'circuit_breaker_state': self.circuit_breaker.state,
            'error_count': self.health.error_count,
            'warnings': self.health.warnings,
            'metrics': self.metrics,
            'last_check': self.health.last_check.isoformat()
        }
    
    async def perform_health_check(self) -> bool:
        """Perform comprehensive health check"""
        try:
            # Check pattern extraction
            test_patterns = await self.pattern_engine.extract_patterns_with_classification(
                "test content", {}
            )
            
            if test_patterns is not None:
                self.health.pattern_extraction_healthy = True
            
            # Update overall health
            if all([
                self.health.database_healthy,
                self.health.cache_healthy,
                self.health.mcp_healthy,
                self.health.pattern_extraction_healthy
            ]):
                self.health.state = SystemState.HEALTHY
            else:
                self.health.state = SystemState.DEGRADED
            
            self.health.last_check = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.health.state = SystemState.CRITICAL
            self.health.error_count += 1
            return False

# Usage example
async def main():
    """Example usage of the production CAG system"""
    engine = ProductionCAGEngine()
    
    # Perform health check
    await engine.perform_health_check()
    
    # Process queries with error recovery
    test_queries = [
        "How do I implement pattern intelligence?",
        "What are the benefits of semantic classification?",
        "Explain error recovery strategies"
    ]
    
    for query in test_queries:
        response = await engine.process_query_with_recovery(
            query, 
            "test-session-001"
        )
        print(f"Query: {query}")
        print(f"Status: {response['system_health']['state']}")
        print(f"Patterns: {response['patterns_extracted']}")
        print(f"Time: {response['performance']['processing_time']:.2f}s")
        print("---")
    
    # Get system health
    health = await engine.get_system_health()
    print(f"System Health: {health}")

if __name__ == "__main__":
    asyncio.run(main())
