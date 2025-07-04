#!/usr/bin/env python3
"""
Configuration Management for KnowledgePersistence-AI
Centralized configuration with environment variable support
NO HARDCODED CREDENTIALS
"""

import os
from pathlib import Path

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'dbname': os.getenv('DB_NAME', 'knowledge_persistence'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')  # Must be set via environment
}

# SSH Configuration
SSH_CONFIG = {
    'hostname': os.getenv('SSH_HOST', '192.168.10.90'),
    'username': os.getenv('SSH_USER', 'greg'),
    'key_file': os.getenv('SSH_KEY', '~/.ssh/id_ed25519_pgdbsrv')
}

# API Configuration
API_CONFIG = {
    'host': os.getenv('API_HOST', '192.168.10.90'),
    'port': int(os.getenv('API_PORT', '8090')),
    'base_url': f"http://{os.getenv('API_HOST', '192.168.10.90')}:{os.getenv('API_PORT', '8090')}"
}

def validate_config():
    """Validate that required configuration is present"""
    missing = []
    
    if not DB_CONFIG['password']:
        missing.append('DB_PASSWORD environment variable')
    
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    return True

def get_db_connection_string():
    """Get database connection string without exposing password"""
    validate_config()
    return f"postgresql://{DB_CONFIG['user']}:***@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# Validate on import
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"⚠️ Configuration Warning: {e}")
        print("Set DB_PASSWORD environment variable for database access")