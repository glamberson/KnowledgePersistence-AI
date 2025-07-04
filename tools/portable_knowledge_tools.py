#!/usr/bin/env python3
"""
Portable Knowledge Tools for KnowledgePersistence-AI
Tool-agnostic scripts for multi-AI and multi-user compatibility
NO dependencies on specific AI assistants or tools
"""

import os
import sys
import json
import psycopg
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class PortableKnowledgeAccess:
    """Tool-agnostic knowledge access interface"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.connection = None
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        config = {
            'db_host': os.getenv('DB_HOST', 'localhost'),
            'db_port': int(os.getenv('DB_PORT', '5432')),
            'db_name': os.getenv('DB_NAME', 'knowledge_persistence'),
            'db_user': os.getenv('DB_USER', 'postgres'),
            'db_password': os.getenv('DB_PASSWORD', ''),
        }
        
        # Try to load from config file if provided
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        
        return config
    
    def connect(self) -> bool:
        """Connect to knowledge database"""
        try:
            self.connection = psycopg.connect(
                host=self.config['db_host'],
                port=self.config['db_port'],
                dbname=self.config['db_name'],
                user=self.config['db_user'],
                password=self.config['db_password']
            )
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def get_knowledge_count(self) -> Dict[str, int]:
        """Get count of knowledge items by type"""
        if not self.connection:
            if not self.connect():
                return {}
        
        try:
            with self.connection.cursor() as cur:
                # Total count
                cur.execute("SELECT COUNT(*) FROM knowledge_items")
                total = cur.fetchone()[0]
                
                # Count by type
                cur.execute("""
                    SELECT knowledge_type, COUNT(*) 
                    FROM knowledge_items 
                    GROUP BY knowledge_type 
                    ORDER BY COUNT(*) DESC
                """)
                by_type = dict(cur.fetchall())
                
                return {
                    'total': total,
                    'by_type': by_type
                }
        except Exception as e:
            print(f"Query failed: {e}")
            return {}
    
    def search_knowledge(self, query: str, knowledge_types: Optional[List[str]] = None, 
                        limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge items"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            with self.connection.cursor() as cur:
                where_clause = "WHERE (title ILIKE %s OR content ILIKE %s)"
                params = [f"%{query}%", f"%{query}%"]
                
                if knowledge_types:
                    where_clause += " AND knowledge_type = ANY(%s)"
                    params.append(knowledge_types)
                
                cur.execute(f"""
                    SELECT id, title, content, knowledge_type, category, 
                           importance_score, created_at
                    FROM knowledge_items 
                    {where_clause}
                    ORDER BY importance_score DESC, created_at DESC
                    LIMIT %s
                """, params + [limit])
                
                columns = ['id', 'title', 'content', 'knowledge_type', 
                          'category', 'importance_score', 'created_at']
                return [dict(zip(columns, row)) for row in cur.fetchall()]
                
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def add_knowledge(self, title: str, content: str, knowledge_type: str,
                     category: str = 'general', importance_score: int = 50) -> Optional[str]:
        """Add new knowledge item"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO knowledge_items 
                    (title, content, knowledge_type, category, importance_score, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (title, content, knowledge_type, category, importance_score, datetime.now()))
                
                item_id = cur.fetchone()[0]
                self.connection.commit()
                return str(item_id)
                
        except Exception as e:
            print(f"Add knowledge failed: {e}")
            return None
    
    def export_knowledge(self, output_path: str, format: str = 'json') -> bool:
        """Export all knowledge to file"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    SELECT id, title, content, knowledge_type, category,
                           importance_score, created_at, updated_at
                    FROM knowledge_items
                    ORDER BY created_at DESC
                """)
                
                columns = ['id', 'title', 'content', 'knowledge_type', 
                          'category', 'importance_score', 'created_at', 'updated_at']
                items = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Convert datetime objects to strings
                for item in items:
                    for key, value in item.items():
                        if hasattr(value, 'isoformat'):
                            item[key] = value.isoformat()
                
                if format.lower() == 'json':
                    with open(output_path, 'w') as f:
                        json.dump(items, f, indent=2)
                else:
                    raise ValueError(f"Unsupported format: {format}")
                
                return True
                
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

class PortableSystemStatus:
    """Tool-agnostic system status interface"""
    
    @staticmethod
    def check_database(config: Dict[str, Any]) -> Dict[str, Any]:
        """Check database connectivity and status"""
        try:
            conn = psycopg.connect(
                host=config['db_host'],
                port=config['db_port'],
                dbname=config['db_name'],
                user=config['db_user'],
                password=config['db_password']
            )
            
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM knowledge_items")
                count = cur.fetchone()[0]
            
            conn.close()
            
            return {
                'status': 'healthy',
                'version': version,
                'knowledge_items': count
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @staticmethod
    def check_api(host: str, port: int) -> Dict[str, Any]:
        """Check API server status"""
        import urllib.request
        import urllib.error
        
        try:
            url = f"http://{host}:{port}/health"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                return {'status': 'healthy', 'response': data}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

def main():
    """Command line interface for portable knowledge tools"""
    if len(sys.argv) < 2:
        print("Portable Knowledge Tools for KnowledgePersistence-AI")
        print("Usage: python3 portable_knowledge_tools.py <command> [args]")
        print("")
        print("Commands:")
        print("  count          - Get knowledge items count")
        print("  search <query> - Search knowledge items")
        print("  add <title> <content> <type> - Add knowledge item")
        print("  export <path>  - Export all knowledge to JSON")
        print("  status         - Check system status")
        print("")
        print("Environment Variables:")
        print("  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        return
    
    command = sys.argv[1]
    
    if command == "count":
        kb = PortableKnowledgeAccess()
        result = kb.get_knowledge_count()
        if result:
            print(f"Total knowledge items: {result['total']}")
            print("Distribution:")
            for ktype, count in result['by_type'].items():
                print(f"  {ktype}: {count}")
        kb.close()
        
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: search <query>")
            return
        
        query = sys.argv[2]
        kb = PortableKnowledgeAccess()
        results = kb.search_knowledge(query)
        
        print(f"Found {len(results)} items for '{query}':")
        for item in results:
            print(f"  [{item['knowledge_type']}] {item['title']}")
            print(f"    {item['content'][:100]}...")
            print()
        kb.close()
        
    elif command == "add":
        if len(sys.argv) < 5:
            print("Usage: add <title> <content> <type>")
            return
        
        title, content, ktype = sys.argv[2], sys.argv[3], sys.argv[4]
        kb = PortableKnowledgeAccess()
        item_id = kb.add_knowledge(title, content, ktype)
        
        if item_id:
            print(f"Added knowledge item: {item_id}")
        else:
            print("Failed to add knowledge item")
        kb.close()
        
    elif command == "export":
        if len(sys.argv) < 3:
            print("Usage: export <path>")
            return
        
        output_path = sys.argv[2]
        kb = PortableKnowledgeAccess()
        if kb.export_knowledge(output_path):
            print(f"Knowledge exported to: {output_path}")
        else:
            print("Export failed")
        kb.close()
        
    elif command == "status":
        config = {
            'db_host': os.getenv('DB_HOST', 'localhost'),
            'db_port': int(os.getenv('DB_PORT', '5432')),
            'db_name': os.getenv('DB_NAME', 'knowledge_persistence'),
            'db_user': os.getenv('DB_USER', 'postgres'),
            'db_password': os.getenv('DB_PASSWORD', ''),
        }
        
        print("=== System Status ===")
        
        # Database status
        db_status = PortableSystemStatus.check_database(config)
        print(f"Database: {db_status['status']}")
        if db_status['status'] == 'healthy':
            print(f"  Knowledge items: {db_status['knowledge_items']}")
        else:
            print(f"  Error: {db_status['error']}")
        
        # API status
        api_status = PortableSystemStatus.check_api(
            os.getenv('API_HOST', '192.168.10.90'),
            int(os.getenv('API_PORT', '8090'))
        )
        print(f"API: {api_status['status']}")
        if api_status['status'] == 'error':
            print(f"  Error: {api_status['error']}")
        
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()