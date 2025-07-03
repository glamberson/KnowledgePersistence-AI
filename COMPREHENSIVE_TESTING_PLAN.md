# Comprehensive Knowledge Persistence Testing Plan
**Date**: 2025-07-03  
**System Status**: Fully operational (4 items captured)  
**Objective**: Complete validation of operational knowledge persistence system  

---

## 🎯 TESTING STRATEGY

### Phase 1: Knowledge Capture Validation (30 minutes)
**Objective**: Verify all 6 knowledge types capture correctly

#### Test Scenarios:
1. **Technical Discovery** - Command failures, error resolution
2. **Procedural** - File operations, configuration changes  
3. **Contextual** - Research activities, information gathering
4. **Relational** - Code relationships, dependency mapping
5. **Experiential** - Session summaries, learning insights
6. **Factual** - Information discovery, fact recording

### Phase 2: Retrieval and Context Testing (20 minutes)  
**Objective**: Validate knowledge retrieval and contextual relevance

#### Test Scenarios:
1. **Similarity Search** - Find related knowledge items
2. **Contextual Retrieval** - Get knowledge for current situation
3. **Technical Gotchas** - Problem-solution pattern matching
4. **Session Continuity** - Cross-session knowledge access

### Phase 3: Performance and Edge Cases (15 minutes)
**Objective**: Stress test and validate robustness

#### Test Scenarios:
1. **High Volume** - Multiple rapid tool executions
2. **Error Handling** - Database failures, network issues
3. **Large Content** - Files, complex operations
4. **Edge Cases** - Unusual tool combinations

---

## 🧪 DETAILED TEST CASES

### Test Case 1: Technical Discovery Capture
```bash
# Execute invalid command to trigger error capture
invalid-command-test --nonexistent-flag
```
**Expected**: technical_discovery item with error details and context

### Test Case 2: Procedural Knowledge - File Operations
```bash
# Create and modify configuration file
echo '{"database": "postgresql", "version": "17.5"}' > test-db-config.json
# Edit the file to add connection details
```
**Expected**: procedural item capturing configuration management

### Test Case 3: Contextual Research Activity
```bash
# Perform web search for technical information
# Search for "PostgreSQL pgvector performance optimization 2025"
```
**Expected**: contextual item with research findings and source information

### Test Case 4: Relational Code Analysis
```bash
# Analyze code relationships in project
grep -r "knowledge_items" --include="*.py" .
# Read database schema file
```
**Expected**: relational item mapping code dependencies

### Test Case 5: Complex Multi-Tool Workflow
```bash
# Combined operation: research -> implementation -> testing
# 1. Web research on best practices
# 2. Code modification based on findings  
# 3. Test execution to validate changes
```
**Expected**: Multiple knowledge items showing workflow progression

### Test Case 6: Session End Knowledge Capture
```bash
# Exit Claude Code session
exit
```
**Expected**: experiential item with session summary and insights

---

## 🔍 VERIFICATION PROCEDURES

### After Each Test Group:
```bash
# Check total items captured
ssh greg@192.168.10.90 "PGPASSWORD=SecureKnowledgePassword2025 psql -h localhost -U postgres -d knowledge_persistence -c \"SELECT COUNT(*) FROM knowledge_items WHERE created_by = 'claude-code-hooks';\""

# View latest captures by type
ssh greg@192.168.10.90 "PGPASSWORD=SecureKnowledgePassword2025 psql -h localhost -U postgres -d knowledge_persistence -c \"SELECT knowledge_type, COUNT(*) FROM knowledge_items WHERE created_by = 'claude-code-hooks' GROUP BY knowledge_type;\""

# Review recent items
ssh greg@192.168.10.90 "PGPASSWORD=SecureKnowledgePassword2025 psql -h localhost -U postgres -d knowledge_persistence -c \"SELECT title, knowledge_type, category, LENGTH(content) as content_length, created_at FROM knowledge_items WHERE created_by = 'claude-code-hooks' ORDER BY created_at DESC LIMIT 5;\""
```

### Knowledge Retrieval Tests:
```bash
# Test similarity search
curl -X POST http://192.168.10.90:8090/search_similar \
  -H "Content-Type: application/json" \
  -d '{"query": "PostgreSQL configuration", "knowledge_type": "procedural", "max_results": 3}'

# Test contextual knowledge retrieval
curl -X POST http://192.168.10.90:8090/contextual_knowledge \
  -H "Content-Type: application/json" \
  -d '{"situation": "database performance optimization", "max_results": 5}'

# Test technical gotchas lookup
curl -X POST http://192.168.10.90:8090/technical_gotchas \
  -H "Content-Type: application/json" \
  -d '{"problem_signature": "PostgreSQL connection issues", "max_results": 3}'
```

---

## 📊 SUCCESS CRITERIA

### Knowledge Capture (Target: 15-20 items)
- ✅ All 6 knowledge types represented  
- ✅ Accurate categorization and classification
- ✅ Complete content capture with context
- ✅ Proper metadata and timestamps

### Knowledge Retrieval (Target: <500ms response)
- ✅ Similarity search returns relevant results
- ✅ Contextual queries provide useful information
- ✅ Technical gotchas match problem patterns
- ✅ Results ranked by relevance

### System Performance (Target: No degradation)
- ✅ Claude Code responsiveness maintained
- ✅ Hook execution under 100ms per tool
- ✅ Database operations complete successfully
- ✅ No errors or system disruption

### Data Quality (Target: 95% useful knowledge)
- ✅ Knowledge items contain actionable information
- ✅ Context data enables future retrieval
- ✅ Categories align with content type
- ✅ No duplicate or redundant captures

---

## 🚨 VALIDATION CHECKLIST

### Pre-Test Setup
- [ ] Database server accessible (192.168.10.90)
- [ ] API server responding (port 8090)
- [ ] Hook script executable and configured
- [ ] Claude Code settings.json contains hooks
- [ ] Baseline knowledge count recorded

### During Testing
- [ ] Hook executions complete without errors
- [ ] Claude Code performance remains normal
- [ ] Database writes succeed for each test
- [ ] Content captured matches expectations
- [ ] Knowledge types classified correctly

### Post-Test Validation
- [ ] All test scenarios executed successfully  
- [ ] Knowledge count increased appropriately
- [ ] Retrieval APIs return expected results
- [ ] No system errors or degradation observed
- [ ] Data quality meets success criteria

---

## 🔄 RECOVERY PROCEDURES

### If Hook Failures Occur:
```bash
# Check hook script functionality
python3 /home/greg/KnowledgePersistence-AI/knowledge-persistence-hook.py --session-end

# Verify Claude Code configuration
cat /home/greg/.claude/settings.json | jq .hooks

# Test database connectivity
curl -s http://192.168.10.90:8090/health
```

### If Database Issues:
```bash
# Check PostgreSQL status
ssh greg@192.168.10.90 "sudo systemctl status postgresql"

# Verify API server
ssh greg@192.168.10.90 "cd KnowledgePersistence-AI && source venv/bin/activate && python test_api.py &"

# Test database connection
ssh greg@192.168.10.90 "PGPASSWORD=SecureKnowledgePassword2025 psql -h localhost -U postgres -d knowledge_persistence -c 'SELECT 1;'"
```

---

## 🎉 EXPECTED OUTCOMES

### Immediate Results (Post-Testing)
- **20+ knowledge items** captured across all types
- **Sub-second retrieval** for contextual queries  
- **Zero system degradation** in Claude Code performance
- **Complete workflow validation** from capture to retrieval

### Strategic Validation
- **Proof of automatic knowledge accumulation** during normal usage
- **Cross-session knowledge continuity** demonstrated
- **Production-ready robustness** confirmed
- **Revolutionary AI persistence capability** validated

---

**READY TO EXECUTE**: Complete testing framework for operational knowledge persistence system
**ESTIMATED TIME**: 65 minutes total
**CONFIDENCE LEVEL**: Very high - comprehensive validation approach