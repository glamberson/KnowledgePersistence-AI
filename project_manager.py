#!/usr/bin/env python3
"""
Project Manager for KnowledgePersistence-AI Multi-Project System
Handles creation, switching, and management of multiple projects
"""

import os
import sys
import json
import argparse
import psycopg
from datetime import datetime
from pathlib import Path
import uuid

class ProjectManager:
    def __init__(self):
        self.db_config = {
            'host': '192.168.10.90',
            'port': 5432,
            'dbname': 'knowledge_persistence',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD', '')
        }
        self.base_path = Path('/home/greg/KnowledgePersistence-AI')
        self.projects_path = self.base_path / 'projects'
        self.projects_path.mkdir(exist_ok=True)
    
    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg.connect(**self.db_config)
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def create_project(self, name, project_type='general', display_name=None, description=None, 
                      repository_url=None, local_path=None, settings=None):
        """Create a new project"""
        print(f"🚀 Creating project: {name}")
        
        # Set defaults
        if not display_name:
            display_name = name.replace('-', ' ').replace('_', ' ').title()
        if not description:
            description = f"{display_name} project"
        if not local_path:
            local_path = str(self.projects_path / name)
        if not settings:
            settings = {}
        
        # Create project in database
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO projects (name, display_name, description, project_type, 
                                            repository_url, local_path, settings)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (name, display_name, description, project_type, 
                         repository_url, local_path, json.dumps(settings)))
                    
                    project_id = cur.fetchone()[0]
                    conn.commit()
                    print(f"✅ Project created in database with ID: {project_id}")
                    
                except psycopg.IntegrityError:
                    print(f"❌ Project '{name}' already exists!")
                    return False
        
        # Create project directory structure
        project_path = Path(local_path)
        project_path.mkdir(exist_ok=True)
        (project_path / 'knowledge').mkdir(exist_ok=True)
        (project_path / 'sessions').mkdir(exist_ok=True)
        
        print(f"📁 Created project directories at: {project_path}")
        
        # Create PROJECT.md configuration file
        self.create_project_config(project_path, {
            'name': name,
            'display_name': display_name,
            'description': description,
            'project_type': project_type,
            'repository_url': repository_url,
            'local_path': local_path,
            'settings': settings
        })
        
        # Create project-specific MCP configuration
        self.setup_project_mcp_config(name, project_path)
        
        # Load applicable strategic insights from other projects
        self.load_cross_project_insights(project_id, project_type)
        
        # Create project switch shortcut
        self.create_project_shortcut(name, project_path)
        
        print(f"🎯 Project '{name}' created successfully!")
        print(f"📄 Configuration: {project_path}/PROJECT.md")
        print(f"🔧 MCP Config: {project_path}/claude-mcp-config.json")
        print(f"🔗 Switch shortcut: /home/greg/switch-{name}.sh")
        
        return True
    
    def create_project_config(self, project_path, config):
        """Create PROJECT.md configuration file"""
        config_content = f"""# {config['display_name']} Project Configuration

**Project Name**: {config['name']}  
**Project Type**: {config['project_type']}  
**Description**: {config['description']}  
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## Project Details
- **Local Path**: {config['local_path']}
- **Repository**: {config.get('repository_url', 'N/A')}
- **Project Type**: {config['project_type']}

## Project Context
{self.get_project_type_context(config['project_type'])}

## AI Assistance Preferences
- Focus on {config['project_type']} best practices
- Maintain project-specific knowledge isolation
- Leverage cross-project strategic insights
- Emphasize continuous learning and improvement

## Knowledge Domains
{self.get_project_type_domains(config['project_type'])}

## Cross-Project Learning
- Apply relevant patterns from other projects
- Share successful methodologies
- Transfer strategic insights
- Maintain project independence

## Usage Instructions
To switch to this project context:
```bash
python project_manager.py switch {config['name']}
```

To start a session with this project:
```bash
export CURRENT_PROJECT="{config['name']}"
# Use Claude Code or CCR with project context
```

---
*Generated by KnowledgePersistence-AI Multi-Project System*
"""
        
        config_file = project_path / 'PROJECT.md'
        config_file.write_text(config_content)
        print(f"📄 Created configuration: {config_file}")
    
    def get_project_type_context(self, project_type):
        """Get context description for project type"""
        contexts = {
            'software': 'Software development project with focus on code quality, testing, and documentation',
            'research': 'Research project with emphasis on data collection, analysis, and knowledge discovery',
            'genealogy': 'Genealogy and family history research with focus on historical records and family connections',
            'ai': 'Artificial intelligence project with focus on machine learning and intelligent systems',
            'general': 'General purpose project with flexible scope and objectives'
        }
        return contexts.get(project_type, 'General purpose project')
    
    def get_project_type_domains(self, project_type):
        """Get knowledge domains for project type"""
        domains = {
            'software': '- Software architecture and design\n- Programming languages and frameworks\n- Testing and quality assurance\n- DevOps and deployment',
            'research': '- Research methodologies\n- Data collection and analysis\n- Academic writing and documentation\n- Literature review and synthesis',
            'genealogy': '- Family history research\n- Historical records and archives\n- DNA analysis and interpretation\n- Genealogy software and tools',
            'ai': '- Machine learning algorithms\n- Neural networks and deep learning\n- Natural language processing\n- AI ethics and best practices',
            'general': '- Project management\n- Problem-solving approaches\n- Documentation and communication\n- Continuous improvement'
        }
        return domains.get(project_type, '- General knowledge and skills')
    
    def setup_project_mcp_config(self, project_name, project_path):
        """Create project-specific MCP configuration"""
        mcp_config = {
            "mcpServers": {
                "knowledge-persistence": {
                    "command": "python3",
                    "args": ["/home/greg/KnowledgePersistence-AI/mcp-integration/knowledge-mcp-server.py"],
                    "env": {
                        "PROJECT_NAME": project_name,
                        "PROJECT_PATH": str(project_path),
                        "PYTHONPATH": "/home/greg/KnowledgePersistence-AI"
                    }
                },
                "sequential-thinking": {
                    "command": "python3",
                    "args": ["/home/greg/KnowledgePersistence-AI/mcp-integration/python-sequential-thinking-mcp/sequential-thinking-mcp/main.py"],
                    "env": {
                        "PROJECT_CONTEXT": project_name,
                        "PYTHONPATH": "/home/greg/KnowledgePersistence-AI/mcp-integration/python-sequential-thinking-mcp"
                    }
                },
                "think-mcp": {
                    "command": "python3",
                    "args": ["-m", "think_mcp"],
                    "cwd": "/home/greg/KnowledgePersistence-AI/mcp-integration/think-mcp",
                    "env": {
                        "PROJECT_CONTEXT": project_name,
                        "PYTHONPATH": "/home/greg/KnowledgePersistence-AI/mcp-integration/think-mcp"
                    }
                },
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", str(project_path)]
                }
            }
        }
        
        config_file = project_path / 'claude-mcp-config.json'
        with open(config_file, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        print(f"🔧 Created MCP config: {config_file}")
    
    def load_cross_project_insights(self, project_id, project_type):
        """Load applicable strategic insights from other projects"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                # Find insights applicable to this project type
                cur.execute("""
                    SELECT COUNT(*) FROM strategic_insights 
                    WHERE %s = ANY(applicable_project_types)
                """, (project_type,))
                
                insight_count = cur.fetchone()[0]
                print(f"📚 Loaded {insight_count} strategic insights applicable to {project_type} projects")
    
    def create_project_shortcut(self, project_name, project_path):
        """Create a quick switch shortcut for the project"""
        shortcut_content = f"""#!/bin/bash
# Quick switch to {project_name} project
cd /home/greg/KnowledgePersistence-AI
python3 project_manager.py switch {project_name} > /dev/null
source switch_to_{project_name}.sh
cd {project_path}
echo "📁 Switched to {project_name} project"
echo "🚀 Ready to use: ccr code"
"""
        
        shortcut_file = Path(f"/home/greg/switch-{project_name}.sh")
        shortcut_file.write_text(shortcut_content)
        shortcut_file.chmod(0o755)
        print(f"🔗 Created shortcut: {shortcut_file}")
    
    def list_projects(self):
        """List all projects"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT name, display_name, project_type, description, active, created_at
                    FROM projects 
                    ORDER BY created_at DESC
                """)
                
                projects = cur.fetchall()
                
        print("\n🏗️  KnowledgePersistence-AI Projects")
        print("=" * 50)
        
        if not projects:
            print("No projects found.")
            return
        
        for name, display_name, project_type, description, active, created_at in projects:
            status = "🟢 Active" if active else "🔴 Inactive"
            print(f"\n📁 {display_name}")
            print(f"   Name: {name}")
            print(f"   Type: {project_type}")
            print(f"   Status: {status}")
            print(f"   Description: {description}")
            print(f"   Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def switch_project(self, project_name):
        """Switch to a project context"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, display_name, local_path, project_type 
                    FROM projects 
                    WHERE name = %s AND active = true
                """, (project_name,))
                
                project = cur.fetchone()
                
        if not project:
            print(f"❌ Project '{project_name}' not found or inactive")
            return False
        
        project_id, display_name, local_path, project_type = project
        
        print(f"🔄 Switching to project: {display_name}")
        print(f"📁 Project path: {local_path}")
        print(f"🏷️  Project type: {project_type}")
        
        # Create switch script
        switch_script = f"""#!/bin/bash
# Project Context Switch Script
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

export CURRENT_PROJECT="{project_name}"
export PROJECT_PATH="{local_path}"
export PROJECT_TYPE="{project_type}"
export MCP_CONFIG="{local_path}/claude-mcp-config.json"

echo "🎯 Switched to project: {display_name}"
echo "📁 Project path: {local_path}"
echo "🔧 MCP config: {local_path}/claude-mcp-config.json"
echo ""
echo "To use with Claude Code:"
echo "  cd {local_path}"
echo "  claude --mcp-config ./claude-mcp-config.json"
echo ""
echo "To use with CCR:"
echo "  cd {local_path}"
echo "  ccr code"
echo ""
"""
        
        switch_file = self.base_path / f"switch_to_{project_name}.sh"
        switch_file.write_text(switch_script)
        switch_file.chmod(0o755)
        
        print(f"✅ Project context switched!")
        print(f"📜 Switch script created: {switch_file}")
        print(f"\nTo activate this project context:")
        print(f"  source {switch_file}")
        print(f"\nOr manually:")
        print(f"  export CURRENT_PROJECT='{project_name}'")
        print(f"  cd {local_path}")
        
        return True
    
    def project_status(self, project_name):
        """Get project status and statistics"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get project info
                cur.execute("""
                    SELECT * FROM projects WHERE name = %s
                """, (project_name,))
                project = cur.fetchone()
                
                if not project:
                    print(f"❌ Project '{project_name}' not found")
                    return
                
                # Get project statistics
                cur.execute("SELECT * FROM get_project_stats(%s)", (project_name,))
                stats = cur.fetchone()
                
        print(f"\n📊 Project Status: {project[2]}")  # display_name
        print("=" * 50)
        print(f"Name: {project[1]}")
        print(f"Type: {project[4]}")
        print(f"Description: {project[3]}")
        print(f"Local Path: {project[6]}")
        print(f"Repository: {project[5] or 'N/A'}")
        print(f"Status: {'🟢 Active' if project[8] else '🔴 Inactive'}")
        print(f"Created: {project[7].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if stats:
            print(f"\n📈 Statistics:")
            print(f"Knowledge Items: {stats[0]}")
            print(f"AI Sessions: {stats[1]}")
            print(f"Strategic Insights: {stats[2]}")
            print(f"Last Activity: {stats[3].strftime('%Y-%m-%d %H:%M:%S') if stats[3] else 'Never'}")

def main():
    parser = argparse.ArgumentParser(description='KnowledgePersistence-AI Project Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create project
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('name', help='Project name (lowercase, no spaces)')
    create_parser.add_argument('--type', default='general', help='Project type (software, research, genealogy, ai, general)')
    create_parser.add_argument('--display-name', help='Display name for the project')
    create_parser.add_argument('--description', help='Project description')
    create_parser.add_argument('--repo', help='Repository URL')
    create_parser.add_argument('--path', help='Local path for project')
    
    # List projects
    list_parser = subparsers.add_parser('list', help='List all projects')
    
    # Switch project
    switch_parser = subparsers.add_parser('switch', help='Switch to a project')
    switch_parser.add_argument('name', help='Project name to switch to')
    
    # Project status
    status_parser = subparsers.add_parser('status', help='Show project status')
    status_parser.add_argument('name', help='Project name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    pm = ProjectManager()
    
    if args.command == 'create':
        pm.create_project(
            name=args.name,
            project_type=args.type,
            display_name=args.display_name,
            description=args.description,
            repository_url=args.repo,
            local_path=args.path
        )
    elif args.command == 'list':
        pm.list_projects()
    elif args.command == 'switch':
        pm.switch_project(args.name)
    elif args.command == 'status':
        pm.project_status(args.name)

if __name__ == '__main__':
    main()