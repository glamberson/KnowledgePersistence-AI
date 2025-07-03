# Live Hook Test - Knowledge Capture Validation

## Test Commands for New Claude Code Session

Copy these commands one by one into a fresh Claude Code session to test all knowledge capture types:

### 1. Technical Discovery Test (Bash Error)
```
Can you run this command: nonexistent-command --help
```
*Expected: Hook captures technical_discovery/troubleshooting*

### 2. Configuration Change Test (File Edit)
```
Create a test file called test-config.json with this content:
{"test": "hook integration", "status": "testing"}
```
*Expected: Hook captures procedural/configuration*

### 3. Research Test (Web Search)
```
Search for "psycopg3 connection pooling best practices"
```
*Expected: Hook captures contextual/research*

### 4. File Operation Test (Multiple Edits)
```
Read the SESSION_HANDOFF_20250703_034400.md file and tell me the session duration
```
*Expected: Hook captures procedural/general*

### 5. Session End Test
```
Exit Claude Code session (Ctrl+D or type 'exit')
```
*Expected: Hook captures experiential/session_management*

## Expected Results

**Before Test**: 3 hook-generated knowledge items
**After Test**: 7-8 hook-generated knowledge items

**Knowledge Types to Verify**:
- technical_discovery (command error)
- procedural (file operations)
- contextual (research activity)  
- experiential (session summary)

## Verification Commands

After the test, run these to verify:

```bash
# Check total hook items
ssh greg@192.168.10.90 "PGPASSWORD=SecureKnowledgePassword2025 psql -h localhost -U postgres -d knowledge_persistence -c \"SELECT COUNT(*) FROM knowledge_items WHERE created_by = 'claude-code-hooks';\""

# View recent captures
ssh greg@192.168.10.90 "PGPASSWORD=SecureKnowledgePassword2025 psql -h localhost -U postgres -d knowledge_persistence -c \"SELECT title, knowledge_type, category, created_at FROM knowledge_items WHERE created_by = 'claude-code-hooks' ORDER BY created_at DESC;\""
```