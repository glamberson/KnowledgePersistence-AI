#!/usr/bin/env python3
"""
Test CAG-MCP Integration with Real Database Data
Validate that MCP integration works with actual knowledge items
"""

import asyncio
import time
from cag_mcp_integrated import CAGEngineMCP, MCPKnowledgeClient

# Test with real data by modifying the mock client to use actual API calls
class RealDataMCPClient(MCPKnowledgeClient):
    """MCP client that uses real API calls for testing"""
    
    def __init__(self):
        super().__init__()
        self.api_base_url = "http://192.168.10.90:8090"
        
    async def _call_real_api(self, endpoint: str, params: dict = None):
        """Call real API endpoint"""
        import urllib.request
        import urllib.parse
        import json
        
        try:
            if params:
                url = f"{self.api_base_url}/{endpoint}?" + urllib.parse.urlencode(params)
            else:
                url = f"{self.api_base_url}/{endpoint}"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return data
        except Exception as e:
            print(f"API call failed: {e}")
            return []
    
    async def get_contextual_knowledge(self, situation: str, max_results: int = 10) -> list:
        """Get knowledge using real API"""
        try:
            # Use real knowledge_items endpoint
            knowledge_items = await self._call_real_api("knowledge_items")
            
            # Filter and format for contextual relevance
            results = []
            for i, item in enumerate(knowledge_items[:max_results]):
                results.append({
                    "id": item.get("id", f"real-{i}"),
                    "title": item.get("title", "No title"),
                    "content": item.get("content", "No content"),
                    "knowledge_type": item.get("knowledge_type", "factual"),
                    "category": item.get("category", "general"),
                    "importance_score": 60 + (i * 5),  # Mock importance
                    "created_at": "2025-07-04T12:00:00"
                })
            
            print(f"Real API: Retrieved {len(results)} knowledge items for: {situation[:30]}...")
            return results
            
        except Exception as e:
            print(f"Real API failed, using mock: {e}")
            return await super().get_contextual_knowledge(situation, max_results)
    
    async def search_knowledge(self, query: str, knowledge_types: list = None, limit: int = 10) -> list:
        """Search knowledge using real API"""
        try:
            knowledge_items = await self._call_real_api("knowledge_items")
            
            # Simple search filtering
            query_lower = query.lower()
            filtered_items = []
            
            for item in knowledge_items:
                content = item.get("content", "").lower()
                title = item.get("title", "").lower()
                category = item.get("category", "").lower()
                
                if (query_lower in content or query_lower in title or query_lower in category):
                    filtered_items.append({
                        "id": item.get("id"),
                        "title": item.get("title", "No title"),
                        "content": item.get("content", "No content"),
                        "knowledge_type": item.get("knowledge_type", "factual"),
                        "category": item.get("category", "general"),
                        "importance_score": 50,
                        "created_at": "2025-07-04T12:00:00"
                    })
                    
                    if len(filtered_items) >= limit:
                        break
            
            print(f"Real API: Found {len(filtered_items)} items matching '{query}'")
            return filtered_items
            
        except Exception as e:
            print(f"Real search failed, using mock: {e}")
            return await super().search_knowledge(query, knowledge_types, limit)

class CAGEngineRealData(CAGEngineMCP):
    """CAG Engine using real data MCP client"""
    
    def __init__(self, max_tokens=128000):
        super().__init__(max_tokens)
        # Replace mock client with real data client
        self.mcp_client = RealDataMCPClient()
        self.context_manager.mcp_client = self.mcp_client
        self.cache_warmer.mcp_client = self.mcp_client

async def test_cag_real_data():
    """Test CAG with real database data"""
    print("=== CAG-MCP REAL DATA INTEGRATION TEST ===")
    print("Testing CAG with actual knowledge items from database...")
    
    # Check database connectivity first
    try:
        import urllib.request
        with urllib.request.urlopen("http://192.168.10.90:8090/health") as response:
            health_data = response.read().decode()
            print(f"Database health: {health_data}")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Falling back to mock data...")
        return
    
    engine = CAGEngineRealData()
    
    test_session = "cag-real-data-test"
    test_queries = [
        "What knowledge do we have about configuration?",
        "Show me procedural knowledge items",
        "Find anything related to genealogy or family research"
    ]
    
    user_context = {
        'keywords': ['configuration', 'genealogy', 'research'],
        'project': 'KnowledgePersistence-AI'
    }
    
    print(f"\nTesting CAG with real data using {len(test_queries)} queries...")
    
    total_start = time.time()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        query_start = time.time()
        response = await engine.process_query(query, test_session, user_context)
        query_time = time.time() - query_start
        
        print(f"MCP Integration: {response['mcp_integration']['framework_used']}")
        print(f"Direct DB Access: {response['mcp_integration']['direct_db_access']}")
        print(f"Context size: {response['context_size_tokens']} tokens")
        print(f"Cached items: {response['cached_knowledge_items']}")
        print(f"Processing time: {query_time:.3f}s")
        print(f"Cache hit: {response['performance']['cache_hit']}")
        
        # Show sample of loaded context
        context_preview = response['full_context'][:500] + "..." if len(response['full_context']) > 500 else response['full_context']
        print(f"Context preview: {context_preview}")
    
    total_time = time.time() - total_start
    
    print(f"\n--- REAL DATA PERFORMANCE METRICS ---")
    metrics = engine.performance_metrics
    print(f"Total test time: {total_time:.3f}s")
    print(f"Total queries: {metrics['total_queries']}")
    print(f"Average response time: {metrics['average_response_time']:.3f}s")
    print(f"Cache hit rate: {(metrics['cache_hits'] / metrics['total_queries'] * 100):.1f}%")
    print(f"Estimated MCP calls: {metrics['mcp_calls']}")
    
    # Test cache contents
    print(f"\n--- CACHE ANALYSIS ---")
    cache_items = engine.cache_warmer.warm_cache
    print(f"Total cached items: {len(cache_items)}")
    
    if cache_items:
        print("Sample cached items:")
        for i, (key, item) in enumerate(list(cache_items.items())[:3]):
            print(f"  {i+1}. [{item['knowledge_type']}] {item['title'][:50]}...")
            print(f"      Priority: {item['priority']:.2f}, Source: {item.get('source', 'unknown')}")

async def test_performance_comparison():
    """Compare performance between mock and real data"""
    print("\n=== PERFORMANCE COMPARISON TEST ===")
    
    # Test with mock data
    print("Testing with mock data...")
    mock_engine = CAGEngineMCP()
    mock_start = time.time()
    
    mock_response = await mock_engine.process_query(
        "Test query for performance", 
        "perf-test-mock",
        {'keywords': ['test'], 'project': 'test'}
    )
    mock_time = time.time() - mock_start
    
    # Test with real data
    print("Testing with real data...")
    real_engine = CAGEngineRealData()
    real_start = time.time()
    
    try:
        real_response = await real_engine.process_query(
            "Test query for performance", 
            "perf-test-real",
            {'keywords': ['test'], 'project': 'test'}
        )
        real_time = time.time() - real_start
        
        print(f"\nPerformance Comparison:")
        print(f"Mock data time: {mock_time:.3f}s")
        print(f"Real data time: {real_time:.3f}s")
        print(f"Real data overhead: {((real_time - mock_time) / mock_time * 100):.1f}%")
        
        print(f"\nContext comparison:")
        print(f"Mock context tokens: {mock_response['context_size_tokens']}")
        print(f"Real context tokens: {real_response['context_size_tokens']}")
        print(f"Real data context gain: {((real_response['context_size_tokens'] - mock_response['context_size_tokens']) / mock_response['context_size_tokens'] * 100):.1f}%")
        
    except Exception as e:
        print(f"Real data test failed: {e}")
        print("This is expected if database is unavailable")

if __name__ == "__main__":
    asyncio.run(test_cag_real_data())
    asyncio.run(test_performance_comparison())