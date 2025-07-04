#!/bin/bash
# Sync CAG and session files to database server
# Addresses file synchronization gaps identified in session analysis

echo "=== KnowledgePersistence-AI File Sync ==="

# Core CAG files
echo "Syncing CAG implementation files..."
scp cag_*.py greg@192.168.10.90:/home/greg/KnowledgePersistence-AI/

# Session management files  
echo "Syncing session management files..."
scp complete_session_storage.py greg@192.168.10.90:/home/greg/KnowledgePersistence-AI/
scp redirection_analysis_tools.py greg@192.168.10.90:/home/greg/KnowledgePersistence-AI/

# Test files
echo "Syncing test files..."
scp test_*.py greg@192.168.10.90:/home/greg/KnowledgePersistence-AI/

# Updated documentation
echo "Syncing updated documentation..."
scp CLAUDE.md greg@192.168.10.90:/home/greg/KnowledgePersistence-AI/

echo "Sync complete. Testing CAG availability on server..."
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python3 -c 'from cag_mcp_integrated import CAGEngineMCP; print(\"CAG import successful\")'"

echo "=== Sync and Test Complete ==="