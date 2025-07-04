#!/usr/bin/env python3
"""
Claude Code Hook: Knowledge Persistence System
==============================================
This hook captures knowledge from Claude Code sessions and stores it in the 
KnowledgePersistence-AI database for cross-session learning and continuity.

Captures:
- Technical discoveries from bash commands and errors
- Problem-solution patterns from code edits  
- Contextual knowledge from session interactions
- Relational knowledge about project components

Hook Events:
- PostToolUse: Captures successful operations and learnings
- Stop: Summarizes session insights and stores knowledge

Configuration for ~/.claude/settings.json:
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*", 
        "hooks": [
          {
            "type": "command",
            "command": "python3 /home/greg/KnowledgePersistence-AI/knowledge-persistence-hook.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command", 
            "command": "python3 /home/greg/KnowledgePersistence-AI/knowledge-persistence-hook.py --session-end"
          }
        ]
      }
    ]
  }
}
"""

import json
import sys
import argparse
import requests
import datetime
import os
import psycopg
from datetime import datetime
from typing import Dict, List, Any
import uuid

# API Configuration
API_BASE_URL = "http://192.168.10.90:8090"

# Debug logging
DEBUG_LOG = "/tmp/claude-hook-debug.log"

def debug_log(message):
    """Log debug messages to file"""
    with open(DEBUG_LOG, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
KNOWLEDGE_ENDPOINT = f"{API_BASE_URL}/knowledge_items"

# Database Configuration
DB_CONFIG = {
    "host": "192.168.10.90",
    "port": 5432,
    "database": "knowledge_persistence", 
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD", "")
}

class KnowledgeCapture:
    def __init__(self):
        self.session_context = {}
        
    def extract_knowledge_from_tool_use(self, tool_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract knowledge items from tool usage data"""
        knowledge_items = []
        
        tool_name = tool_data.get("tool_name", "")
        tool_input = tool_data.get("tool_input", {})
        tool_response = tool_data.get("tool_response", {})
        
        # Technical Discovery: Command failures and solutions
        if tool_name == "Bash" and tool_response.get("error"):
            command = tool_input.get("command", "")
            error = tool_response.get("error", "")
            
            knowledge_items.append({
                "knowledge_type": "technical_discovery",
                "category": "troubleshooting", 
                "title": f"Command Error: {command[:50]}...",
                "content": f"Command '{command}' failed with error: {error}. Context: Claude Code session troubleshooting.",
                "importance": 70,
                "context_metadata": {
                    "tool": tool_name,
                    "command": command,
                    "error_type": "bash_execution",
                    "session_date": datetime.now().isoformat()
                }
            })
            
        # Procedural Knowledge: Successful complex operations
        elif tool_name in ["Edit", "MultiEdit", "Write"]:
            file_path = tool_input.get("file_path", "")
            
            # Check if this is a successful operation (no error in response)
            has_error = tool_response.get("error") is not None
            
            if not has_error and file_path:
                # Capture configuration/important file changes
                if any(keyword in file_path.lower() for keyword in ["config", "hook", "mcp", "settings", "claude"]):
                    knowledge_items.append({
                        "knowledge_type": "procedural", 
                        "category": "configuration",
                        "title": f"File Modified: {os.path.basename(file_path)}",
                        "content": f"Successfully modified {file_path} during Claude Code session. Tool: {tool_name}",
                        "importance": 65,
                        "context_metadata": {
                            "tool": tool_name,
                            "file": file_path,
                            "operation": "file_modification",
                            "session_date": datetime.now().isoformat()
                        }
                    })
        
        # Contextual Knowledge: Research and discovery
        elif tool_name in ["WebFetch", "WebSearch"]:
            query = tool_input.get("query", "") or tool_input.get("url", "")
            
            knowledge_items.append({
                "knowledge_type": "contextual",
                "category": "research",
                "title": f"Research Discovery: {query[:50]}...",
                "content": f"Researched '{query}' during Claude Code session using {tool_name}.",
                "importance": 50,
                "context_metadata": {
                    "tool": tool_name,
                    "query": query,
                    "research_type": "web_discovery", 
                    "session_date": datetime.now().isoformat()
                }
            })
            
        return knowledge_items
    
    def store_knowledge_item(self, knowledge_item: Dict[str, Any]) -> bool:
        """Store knowledge item directly in PostgreSQL database"""
        try:
            # First try API approach (future compatibility)
            try:
                response = requests.post(
                    KNOWLEDGE_ENDPOINT, 
                    json=knowledge_item,
                    timeout=3
                )
                if response.status_code in [200, 201]:
                    print(f"[KNOWLEDGE] Stored via API: {knowledge_item['title']}", file=sys.stderr)
                    return True
            except requests.RequestException:
                pass  # Fall back to direct database
            
            # Direct database storage
            return self._store_direct_database(knowledge_item)
            
        except Exception as e:
            print(f"[KNOWLEDGE ERROR] Failed to store: {e}", file=sys.stderr)
            return False
    
    def _store_direct_database(self, knowledge_item: Dict[str, Any]) -> bool:
        """Store knowledge item directly in PostgreSQL"""
        try:
            # Generate UUID for the knowledge item
            item_id = str(uuid.uuid4())
            
            # Connect to database
            conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            
            with psycopg.connect(conn_string) as conn:
                with conn.cursor() as cur:
                    # Insert into knowledge_items table
                    insert_query = """
                    INSERT INTO knowledge_items (
                        id, knowledge_type, category, title, content, 
                        importance_score, context_data, created_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cur.execute(insert_query, (
                        item_id,
                        knowledge_item.get('knowledge_type', 'experiential'),
                        knowledge_item.get('category', 'general'),
                        knowledge_item.get('title', 'Untitled Knowledge'),
                        knowledge_item.get('content', ''),
                        knowledge_item.get('importance', 50),
                        json.dumps(knowledge_item.get('context_metadata', {})),
                        'claude-code-hooks'
                    ))
                    
                    conn.commit()
                    print(f"[KNOWLEDGE] Stored in database: {knowledge_item['title']}", file=sys.stderr)
                    return True
                    
        except Exception as e:
            print(f"[KNOWLEDGE ERROR] Database storage failed: {e}", file=sys.stderr)
            return False
    
    def process_session_end(self) -> None:
        """Process end of session and store session summary"""
        session_summary = {
            "knowledge_type": "experiential",
            "category": "session_management", 
            "title": f"Claude Code Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": f"Completed Claude Code session with knowledge persistence hook active. Session captured technical discoveries, procedural knowledge, and research context.",
            "importance": 60,
            "context_metadata": {
                "session_end": datetime.now().isoformat(),
                "knowledge_hook": "active",
                "persistence_system": "KnowledgePersistence-AI"
            }
        }
        
        self.store_knowledge_item(session_summary)

def main():
    debug_log("Hook called with args: " + str(sys.argv))
    
    parser = argparse.ArgumentParser(description='Claude Code Knowledge Persistence Hook')
    parser.add_argument('--session-end', action='store_true', help='Process session end')
    args = parser.parse_args()
    
    capture = KnowledgeCapture()
    
    if args.session_end:
        debug_log("Processing session end")
        capture.process_session_end()
        return
    
    try:
        debug_log("Reading stdin for tool data")
        input_data = json.load(sys.stdin)
        debug_log(f"Full JSON input: {json.dumps(input_data, indent=2)}")
    except json.JSONDecodeError as e:
        debug_log(f"JSON decode error: {e}")
        print(f"[KNOWLEDGE ERROR] Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block tool execution
    
    # Extract and store knowledge from tool usage
    debug_log("Extracting knowledge from tool use")
    knowledge_items = capture.extract_knowledge_from_tool_use(input_data)
    debug_log(f"Extracted {len(knowledge_items)} knowledge items")
    
    for item in knowledge_items:
        capture.store_knowledge_item(item)
    
    # Always allow tool execution to continue
    debug_log("Hook processing complete")
    sys.exit(0)

if __name__ == "__main__":
    main()