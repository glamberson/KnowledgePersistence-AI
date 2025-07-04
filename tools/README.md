# Portable Tools for KnowledgePersistence-AI
**Purpose**: Tool-agnostic scripts for multi-AI and multi-user compatibility  
**No Dependencies**: Works with any AI assistant, user, or development environment  

---

## 🛠️ AVAILABLE TOOLS

### **portable_knowledge_tools.py**
Primary interface for knowledge database operations:

```bash
# Set environment variables first
export DB_PASSWORD="your_password"
export DB_HOST="localhost" 
export DB_PORT="5432"

# Get knowledge count and distribution
python3 tools/portable_knowledge_tools.py count

# Search knowledge items
python3 tools/portable_knowledge_tools.py search "configuration"

# Add new knowledge item
python3 tools/portable_knowledge_tools.py add "New Finding" "Content here" "experiential"

# Export all knowledge to JSON
python3 tools/portable_knowledge_tools.py export knowledge_backup.json

# Check system status
python3 tools/portable_knowledge_tools.py status
```

---

## 🔧 TOOL CHARACTERISTICS

### **Framework Independence**
- ✅ **No AI-specific dependencies**: Works with Claude, GPT, Gemini, local models
- ✅ **No tool-specific code**: Standard Python and PostgreSQL only
- ✅ **No hardcoded paths**: Environment variable configuration
- ✅ **No authentication dependencies**: Uses standard database connections

### **Multi-User Compatibility**  
- ✅ **Environment-based config**: Each user sets their own variables
- ✅ **Standard interfaces**: PostgreSQL, HTTP, JSON, SSH
- ✅ **Minimal requirements**: Python 3.7+, psycopg, standard libraries
- ✅ **Portable scripts**: Copy and run anywhere

### **Multi-Environment Support**
- ✅ **Local development**: Works on any machine with Python
- ✅ **Remote servers**: SSH-compatible operations
- ✅ **Docker containers**: Standard database connections
- ✅ **CI/CD pipelines**: Scriptable and automatable

---

## 📋 USAGE PATTERNS

### **For AI Assistants**
```python
# Import and use directly
from tools.portable_knowledge_tools import PortableKnowledgeAccess

kb = PortableKnowledgeAccess()
results = kb.search_knowledge("implementation patterns")
for item in results:
    print(f"{item['knowledge_type']}: {item['title']}")
kb.close()
```

### **For Human Users**
```bash
# Command line interface
./tools/portable_knowledge_tools.py status
./tools/portable_knowledge_tools.py count
./tools/portable_knowledge_tools.py search "documentation"
```

### **For Automation Scripts**
```bash
#!/bin/bash
# Source environment
source .env

# Check system status
if python3 tools/portable_knowledge_tools.py status | grep -q "healthy"; then
    echo "System operational"
else
    echo "System issues detected"
    exit 1
fi
```

---

## 🔍 ENVIRONMENT CONFIGURATION

### **Required Variables**
```bash
export DB_PASSWORD="your_database_password"
export DB_HOST="database_hostname"
export DB_PORT="5432"
export DB_NAME="knowledge_persistence"
export DB_USER="postgres"
```

### **Optional Variables**
```bash
export API_HOST="api_server_hostname"
export API_PORT="8090"
export SSH_HOST="ssh_hostname"
export SSH_USER="ssh_username"
export SSH_KEY="~/.ssh/keyfile"
```

### **Configuration Files**
Create `.env` file for local development:
```bash
# Copy example and modify
cp .env.example .env
# Edit .env with your settings
# Source before use
source .env
```

---

## 🚀 INTEGRATION EXAMPLES

### **Multi-AI Session Handoff**
```python
# Any AI can use this to access knowledge
kb = PortableKnowledgeAccess()

# Get current project status
status = kb.search_knowledge("current status", limit=5)
print("Project Status:")
for item in status:
    print(f"- {item['title']}")

# Get implementation notes
impl = kb.search_knowledge("implementation", ["procedural"], limit=10)
print("Implementation Knowledge:")
for item in impl:
    print(f"- {item['title']}: {item['content'][:100]}...")

kb.close()
```

### **Multi-User Project Access**
```bash
# User A environment
export DB_HOST="server1.example.com"
export DB_PASSWORD="userA_password"
python3 tools/portable_knowledge_tools.py count

# User B environment  
export DB_HOST="server2.example.com"
export DB_PASSWORD="userB_password"
python3 tools/portable_knowledge_tools.py count
```

### **Tool Migration**
```bash
# Export from current system
python3 tools/portable_knowledge_tools.py export knowledge_export.json

# Import to new system (implementation-specific)
# Standard JSON format ensures compatibility
```

---

## 📊 COMPATIBILITY MATRIX

| Component | Claude | GPT | Gemini | Local Models | Human Users |
|-----------|--------|-----|---------|--------------|-------------|
| Knowledge Access | ✅ | ✅ | ✅ | ✅ | ✅ |
| Database Queries | ✅ | ✅ | ✅ | ✅ | ✅ |
| Status Checking | ✅ | ✅ | ✅ | ✅ | ✅ |
| Knowledge Export | ✅ | ✅ | ✅ | ✅ | ✅ |
| Configuration | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🔮 FUTURE EXPANSION

### **Planned Tools**
- `portable_ssh_tools.py` - SSH operations without password exposure
- `portable_deployment_tools.py` - Infrastructure management
- `portable_testing_tools.py` - Validation and testing
- `portable_backup_tools.py` - Data backup and recovery

### **Integration Points**
- RESTful API wrappers
- Docker container management
- CI/CD pipeline integration
- Documentation generation

**Result**: Complete toolkit for AI-agnostic, user-agnostic, environment-agnostic knowledge persistence operations.