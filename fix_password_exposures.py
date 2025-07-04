#!/usr/bin/env python3
"""
Fix Password Exposures in KnowledgePersistence-AI
Systematically replace hardcoded passwords with environment variables
"""

import os
import re
import glob

def fix_file(filepath):
    """Fix password exposures in a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Replace database password
        patterns = [
            (r"password=os.getenv('DB_PASSWORD', '')", "password=os.getenv('DB_PASSWORD', '')"),
            (r'password=os.getenv("DB_PASSWORD", "")', 'password=os.getenv("DB_PASSWORD", "")'),
            (r"os.getenv('DB_PASSWORD', '')", "os.getenv('DB_PASSWORD', '')"),
            (r'os.getenv("DB_PASSWORD", "")', 'os.getenv("DB_PASSWORD", "")'),
            (r"password=os.getenv('SSH_PASSWORD', '')", "password=os.getenv('SSH_PASSWORD', '')"),
            (r'password=os.getenv("SSH_PASSWORD", "")', 'password=os.getenv("SSH_PASSWORD", "")'),
        ]
        
        changes_made = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made = True
        
        # Add import os if needed and changes were made
        if changes_made and 'import os' not in content and 'os.getenv' in content:
            # Find appropriate place to add import
            lines = content.split('\n')
            import_index = 0
            
            # Find last import or first non-comment line
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_index = i + 1
                elif line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                    if import_index == 0:
                        import_index = i
                    break
            
            lines.insert(import_index, 'import os')
            content = '\n'.join(lines)
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all password exposures in the project"""
    print("=== Fixing Password Exposures ===")
    
    # Find all Python files
    python_files = glob.glob("**/*.py", recursive=True)
    
    fixed_count = 0
    for filepath in python_files:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Files scanned: {len(python_files)}")
    print(f"Files fixed: {fixed_count}")
    
    # Create environment setup script
    env_script = """#!/bin/bash
# Environment Variables for KnowledgePersistence-AI
# Set these before running any scripts

export DB_PASSWORD=os.getenv("DB_PASSWORD", "")
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="knowledge_persistence"
export DB_USER="postgres"

export SSH_HOST="192.168.10.90"
export SSH_USER="greg"
export SSH_KEY="~/.ssh/id_ed25519_pgdbsrv"

export API_HOST="192.168.10.90"
export API_PORT="8090"

echo "✅ KnowledgePersistence-AI environment variables set"
echo "⚠️ Remember: These are for development only. Use secure methods in production."
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_script)
    
    print("✅ Created .env.example with environment variable template")
    print("\n📋 Next Steps:")
    print("1. Copy .env.example to .env and set appropriate values")
    print("2. Run 'source .env' before using any scripts")
    print("3. Add .env to .gitignore to prevent credential leakage")

if __name__ == "__main__":
    main()