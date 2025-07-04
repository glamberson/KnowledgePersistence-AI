#!/bin/bash
# Secure File Sync for KnowledgePersistence-AI
# Uses SSH key authentication - NO password exposure
# Addresses file synchronization gaps identified in session analysis

echo "=== KnowledgePersistence-AI Secure File Sync ==="

# Check SSH key exists
if [ ! -f ~/.ssh/id_ed25519_pgdbsrv ]; then
    echo "❌ SSH key not found. Please run SSH setup first."
    exit 1
fi

# Use SSH config alias for secure connection (no password exposure)
SSH_CMD="ssh pgdbsrv"
SCP_CMD="scp -i ~/.ssh/id_ed25519_pgdbsrv"

# Core CAG files using secure SCP
echo "Syncing CAG implementation files..."
$SCP_CMD cag_*.py pgdbsrv:/home/greg/KnowledgePersistence-AI/

# Session management files  
echo "Syncing session management files..."
$SCP_CMD complete_session_storage.py redirection_analysis_tools.py pgdbsrv:/home/greg/KnowledgePersistence-AI/

# Test files
echo "Syncing test files..."
$SCP_CMD test_*.py pgdbsrv:/home/greg/KnowledgePersistence-AI/

# Secure SSH tools
echo "Syncing secure SSH tools..."
$SCP_CMD secure_ssh_tools.py pgdbsrv:/home/greg/KnowledgePersistence-AI/

# Updated documentation
echo "Syncing updated documentation..."
$SCP_CMD CLAUDE.md SESSION_HANDOFF_*.md pgdbsrv:/home/greg/KnowledgePersistence-AI/

echo "Sync complete. Testing CAG availability on server..."
$SSH_CMD "cd KnowledgePersistence-AI && source venv/bin/activate && python3 -c 'from cag_mcp_integrated import CAGEngineMCP; print(\"✅ CAG import successful\")'"

echo "Testing secure SSH tools..."
$SSH_CMD "cd KnowledgePersistence-AI && chmod +x secure_ssh_tools.py && python3 secure_ssh_tools.py status"

echo "=== Secure Sync and Test Complete ==="