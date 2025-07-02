# Technical Gotchas and Discoveries
**NavyCMMS Project - Hard-Learned Technical Lessons**

**Created**: 2025-07-02  
**Purpose**: Preserve technical discoveries made through trial and error  
**Context**: Prevent re-learning of technical patterns and command failures  

---

## GitHub API Patterns (Trial and Error Learning)

### **Branch Specification Requirements**
- **Critical Discovery**: NavyCMMS repository requires `?ref=develop` for current implementation state
- **Problem**: API calls without branch specification default to main branch (outdated)
- **Impact**: Getting outdated project information when checking current development status
- **Solution Pattern**: Always specify develop branch for NavyCMMS repository operations
- **Working Examples**:
  ```bash
  gh api repos/lamco-admin/NavyCMMS/contents/requirements.txt?ref=develop
  gh api graphql --field query='{ repository(owner: "lamco-admin", name: "NavyCMMS") { 
    develop: ref(qualifiedName: "refs/heads/develop") { ... } } }'
  ```

### **Command Syntax Failures and Solutions**
- **Failed Pattern**: `gh api repos/lamco-admin/NavyCMMS/issues | jq '.[] | "\(.number): \(.title)"'`
- **Error**: jq syntax issues with repository names containing hyphens in some contexts
- **Root Cause**: Complex jq expressions with certain repository name patterns
- **Working Solution**: Use GraphQL API with proper field specifications
- **Reliable Pattern**:
  ```bash
  gh api graphql --field query='{ repository(owner: "lamco-admin", name: "NavyCMMS") { 
    issues(first: 50) { nodes { number title state } } } }'
  ```

### **Multi-Repository Operations**
- **Discovery**: Cannot use `cd` to change to parent directories outside initial working directory
- **Limitation**: Claude Code restrictions on directory navigation
- **Solution**: Use `git -C /path/to/repo` for multi-repository operations
- **Working Pattern**:
  ```bash
  git -C /home/greg/NavyCMMS status
  git -C /home/greg/NavyCMMS add .
  git -C /home/greg/NavyCMMS commit -m "message"
  git -C /home/greg/NavyCMMS push origin develop
  ```

### **Issue Listing and Filtering**
- **Problem**: Large API responses can cause session failures due to response length limits
- **Solution**: Always use `--limit` flag to control response size
- **Working Pattern**: `gh issue list --repo lamco-admin/NavyCMMS --limit 10`
- **Failed Pattern**: `gh issue list --repo lamco-admin/NavyCMMS` (no limit, could be too large)

---

## Document Organization Discovery Patterns

### **Document Reorganization Impact**
- **Discovery**: Large DJANGO_PATTERNS.md was split into multiple focused documents
- **Problem**: Issue references became outdated when reorganization occurred
- **Impact**: GitHub issues contained references to non-existent document structure
- **Lesson**: Document reorganization requires systematic issue reference updates

### **Document Existence Verification**
- **Critical Pattern**: Always verify document existence before referencing in GitHub issues
- **Method**: Use `ls -la` to check file system state before making claims about documents
- **Example Discovery**: 
  - DJANGO_MODEL_STANDARDS.md exists (10KB) - don't need to create
  - DJANGO_INFRASTRUCTURE_PATTERNS.md exists (34KB) - verify completeness instead
- **Verification Command**: `ls -la /home/greg/NavyCMMS-ProjectMgt/standards/`

### **Issue Update Strategy**
- **Pattern**: When updating issue references, check current file system state first
- **Method**: Verify which documents exist vs which are referenced in issues
- **Discovery Process**: Found 6 issues with outdated document references due to reorganization
- **Systematic Approach**: Update all references in batch after verifying current state

---

## GitHub CLI and API Limitations

### **Response Length Limits**
- **Problem**: GitHub CLI may have response length limits that cause session failures
- **Symptoms**: Session suddenly stops responding after large API calls
- **Prevention**: Use pagination and limits on all list operations
- **Recovery**: Restart session and use smaller, more specific queries

### **Authentication and Organization Context**
- **Discovery**: Repository owner is organization `lamco-admin`, not user
- **Impact**: Initial API calls failed when using user context instead of organization
- **Solution**: Use organization context for Projects V2 operations
- **Working Pattern**: `gh api graphql` with organization references

### **GraphQL vs REST API Requirements**
- **Discovery**: Projects V2 only supports GraphQL API, not REST
- **Limitation**: Cannot use simple REST endpoints for project operations
- **Required Approach**: Use GraphQL queries for all project management operations
- **Learning Curve**: GraphQL syntax requires different patterns than REST

---

## Django and Repository Structure Discoveries

### **Branch Strategy Understanding**
- **Main Branch**: Used for releases and stable code
- **Develop Branch**: Used for active development and current implementation
- **Critical Insight**: Always check develop branch for current project state
- **Impact**: Checking main branch gives outdated view of current work

### **Docker and Development Environment**
- **Working Directory**: `/home/greg/NavyCMMS` for implementation repository
- **Service Architecture**: Docker Compose with web, db, redis, celery services
- **Access Patterns**: Use `docker compose exec web` for Django management commands
- **Environment Verification**: Always check both repositories are accessible before starting

### **File System Navigation Limitations**
- **Restriction**: Cannot navigate to parent directories of initial working directory
- **Workaround**: Use absolute paths with file system tools
- **Pattern**: `ls -la /home/greg/NavyCMMS` instead of `cd ../NavyCMMS && ls -la`
- **Git Operations**: Use `-C` flag for operations in other repositories

---

## Session Management Technical Patterns

### **Handoff Document Timing**
- **Discovery**: Archive previous documents BEFORE creating new ones per procedure
- **Requirement**: Move old HANDOVER_*.md to archive/ directory
- **Pattern**: Keep only current session documents in root directory
- **Quality Gate**: Complete handoff procedure includes mandatory archival step

### **Commit Message Patterns**
- **Format**: Include 🤖 Generated with [Claude Code] attribution
- **Co-Author**: Add Co-Authored-By: Claude <noreply@anthropic.com>
- **Context**: Reference issue numbers and purpose clearly
- **Example**:
  ```
  feat: Implement enhanced knowledge preservation system
  
  - Create PROJECT_MANAGEMENT_PHILOSOPHY.md with critical thinking patterns
  - Enhance SESSION_HANDOFF_PROCEDURE.md with philosophical learning sections
  
  🤖 Generated with [Claude Code](https://claude.ai/code)
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

### **Repository State Verification**
- **Always Check**: Git status for both repositories before making assumptions
- **Pattern**: `git status` and `git -C /home/greg/NavyCMMS status`
- **Verification**: Both repositories should be clean and up-to-date
- **Action**: Commit and push any uncommitted changes before session end

---

## Troubleshooting Patterns That Work

### **API Call Failures**
1. **Check Authentication**: Verify `gh` CLI is authenticated
2. **Verify Repository Access**: Test simple API calls first
3. **Use Limits**: Add `--limit` flags to prevent large responses
4. **Try GraphQL**: Switch to GraphQL for complex queries
5. **Check Branch Context**: Ensure develop branch specified for NavyCMMS

### **Command Execution Issues**
1. **Check Working Directory**: Verify correct starting location
2. **Use Absolute Paths**: Don't rely on relative navigation
3. **Test File Existence**: Use `ls -la` to verify paths before operations
4. **Use Git -C Flag**: For multi-repository operations
5. **Check Permissions**: Ensure file system access rights

### **Session Recovery Strategies**
1. **Read START_HERE.md**: Always start with current session pointer
2. **Verify Repository Access**: Test both repositories are accessible
3. **Check Git Status**: Ensure clean state before proceeding
4. **Load Context Documents**: Read handoff and philosophy documents
5. **Test Understanding**: Apply devil's advocate thinking to verify capability

---

## Prevention Strategies

### **Before Making API Calls**
- [ ] Verify authentication status
- [ ] Check if branch specification needed (NavyCMMS requires develop)
- [ ] Add appropriate limits to prevent large responses
- [ ] Test simple calls before complex operations

### **Before Updating Issues**
- [ ] Verify current document existence in file system
- [ ] Check current project state with git status
- [ ] Confirm issue content accuracy against current reality
- [ ] Use project data to verify claims before making them

### **Before Session End**
- [ ] Complete handoff procedure including archival step
- [ ] Commit and push all changes
- [ ] Verify clean repository state
- [ ] Test that knowledge preservation documents are accessible

---

**STATUS**: Technical discoveries documented to prevent re-learning. New sessions should automatically apply these patterns without trial-and-error rediscovery.