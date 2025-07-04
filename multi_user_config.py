#!/usr/bin/env python3
"""
Multi-User Configuration Framework for KnowledgePersistence-AI
Handles user-specific database access, SSH keys, and credentials
"""

import os
import getpass
import json
from pathlib import Path
from typing import Dict, Any, Optional

class MultiUserConfig:
    """User-specific configuration management"""
    
    def __init__(self, user: str = None):
        self.user = user or getpass.getuser()
        self.base_path = Path('/home/greg/KnowledgePersistence-AI')
        self.user_config_path = self.base_path / f'configs/user_{self.user}.json'
        
    def get_db_config(self) -> Dict[str, Any]:
        """Get user-specific database configuration"""
        return {
            'host': os.getenv('DB_HOST', '192.168.10.90'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'dbname': os.getenv('DB_NAME', 'knowledge_persistence'),
            'user': f'user_{self.user}',  # User-specific DB role
            'password': os.getenv(f'DB_PASSWORD_{self.user.upper()}', os.getenv('DB_PASSWORD', ''))
        }
    
    def get_ssh_config(self) -> Dict[str, str]:
        """Get user-specific SSH configuration"""
        return {
            'hostname': os.getenv('SSH_HOST', '192.168.10.90'),
            'username': self.user,
            'key_file': f'~/.ssh/id_ed25519_{self.user}_pgdbsrv',
            'alias': f'pgdbsrv-{self.user}'
        }
    
    def create_user_config(self) -> bool:
        """Create user-specific configuration file"""
        config = {
            'user': self.user,
            'created': str(Path.ctime(Path.now())),
            'database': self.get_db_config(),
            'ssh': self.get_ssh_config(),
            'permissions': {
                'read_knowledge': True,
                'write_knowledge': True,
                'admin_access': self.user == 'greg'
            }
        }
        
        self.user_config_path.parent.mkdir(exist_ok=True)
        with open(self.user_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    
    def setup_user_environment(self) -> Dict[str, str]:
        """Generate user-specific environment variables"""
        env_vars = {
            f'DB_USER_{self.user.upper()}': f'user_{self.user}',
            f'SSH_HOST_{self.user.upper()}': f'pgdbsrv-{self.user}',
            f'MCP_USER': self.user
        }
        return env_vars

def main():
    """Setup multi-user configuration for current user"""
    config = MultiUserConfig()
    print(f"Setting up configuration for user: {config.user}")
    
    if config.create_user_config():
        print(f"✅ User configuration created: {config.user_config_path}")
    
    env_vars = config.setup_user_environment()
    print("\n📋 Add these to your environment:")
    for key, value in env_vars.items():
        print(f"export {key}='{value}'")

if __name__ == "__main__":
    main()