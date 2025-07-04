#!/bin/bash
# Simple Secure SSH Tools for KnowledgePersistence-AI
# Uses SSH key authentication with no password exposure
# Alternative to Python version when paramiko not available

# Configuration
SSH_HOST="pgdbsrv"
SSH_KEY="~/.ssh/id_ed25519_pgdbsrv"

# Check SSH key exists
if [ ! -f ~/.ssh/id_ed25519_pgdbsrv ]; then
    echo "❌ SSH key not found. Please run SSH setup first."
    exit 1
fi

# Function to execute remote command securely
ssh_exec() {
    ssh $SSH_HOST "$1"
}

# Function to execute remote sudo command
ssh_sudo() {
    ssh $SSH_HOST "sudo $1"
}

# Command functions
check_status() {
    echo "=== System Status Check ==="
    
    echo "📡 Database Status:"
    ssh_sudo "systemctl status postgresql | head -3"
    
    echo -e "\n🔗 API Status:"
    ssh_exec "curl -s http://localhost:8090/health"
    
    echo -e "\n🐳 Docker Status:"
    ssh_sudo "docker ps | head -3"
}

count_knowledge() {
    echo "=== Knowledge Items Count ==="
    ssh_exec 'cd KnowledgePersistence-AI && source venv/bin/activate && python3 -c "
import psycopg
import os
try:
    conn = psycopg.connect(
        host=\"localhost\", 
        dbname=\"knowledge_persistence\", 
        user=\"postgres\", 
        password=os.getenv(\"DB_PASSWORD\", \"\")
    )
    cur = conn.cursor()
    cur.execute(\"SELECT COUNT(*) FROM knowledge_items\")
    count = cur.fetchone()[0]
    cur.execute(\"SELECT knowledge_type, COUNT(*) FROM knowledge_items GROUP BY knowledge_type ORDER BY COUNT(*) DESC\")
    types = cur.fetchall()
    conn.close()
    
    print(f\"Total knowledge items: {count}\")
    print(\"Distribution:\")
    for ktype, kcount in types:
        print(f\"  {ktype}: {kcount}\")
except Exception as e:
    print(f\"Error: {e}\")
"'
}

test_cag() {
    echo "=== CAG Performance Test ==="
    ssh_exec 'cd KnowledgePersistence-AI && source venv/bin/activate && timeout 30s python3 -c "
from cag_mcp_integrated import CAGEngineMCP
import asyncio
import time

async def test():
    try:
        engine = CAGEngineMCP()
        start = time.time()
        result = await engine.process_query(\"Security test query\", \"security-test\", {\"keywords\": [\"test\"]})
        duration = time.time() - start
        
        print(f\"✅ SUCCESS: {duration:.3f}s response time\")
        
        cache_hit = result[\"performance\"][\"cache_hit\"]
        tokens = result[\"context_size_tokens\"]
        framework = result[\"mcp_integration\"][\"framework_used\"]
        
        print(f\"Cache hit: {cache_hit}\")
        print(f\"Context tokens: {tokens}\")
        print(f\"MCP integration: {framework}\")
        return True
    except Exception as e:
        print(f\"❌ ERROR: {e}\")
        return False

try:
    result = asyncio.run(test())
    exit(0 if result else 1)
except Exception as e:
    print(f\"❌ CRITICAL ERROR: {e}\")
    exit(1)
"'
}

interactive_shell() {
    echo "=== Interactive SSH Shell ==="
    echo "Connected to $SSH_HOST. Use 'exit' to return."
    ssh $SSH_HOST
}

show_logs() {
    echo "=== Recent PostgreSQL Logs ==="
    ssh_sudo "journalctl -u postgresql -n 20 --no-pager"
}

# Main command dispatcher
case "$1" in
    "status")
        check_status
        ;;
    "count")
        count_knowledge
        ;;
    "test-cag")
        test_cag
        ;;
    "shell")
        interactive_shell
        ;;
    "logs")
        show_logs
        ;;
    *)
        echo "Secure SSH Tools for KnowledgePersistence-AI"
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  status    - Check database, API, and Docker status"
        echo "  count     - Get knowledge items count and distribution"
        echo "  test-cag  - Test CAG performance"
        echo "  shell     - Interactive SSH shell"
        echo "  logs      - Show recent PostgreSQL logs"
        echo ""
        echo "✅ All operations use SSH key authentication (no password exposure)"
        ;;
esac