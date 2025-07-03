# 🚨 RECOVERY CHEAT SHEET

**Emergency Recovery Commands for KnowledgePersistence-AI + Router**

---

## ⚡ INSTANT RECOVERY (Choose One)

### Option 1: Regular Claude Code (100% Reliable)
```bash
claude
```
**Use when**: Router broken, any technical issues  
**Gets you**: Standard Claude Code functionality immediately

### Option 2: Restart Router  
```bash
npx ccr stop
npx ccr start
ccr code
```
**Use when**: Router seems stuck or unresponsive

### Option 3: Complete Router Reset
```bash
npx ccr stop
pkill -f "ccr"
rm -f /home/greg/.claude-code-router/.claude-code-router.pid
source ~/.bashrc
npx ccr start
```
**Use when**: Router completely broken

---

## 🔍 QUICK DIAGNOSTICS

### Check Knowledge System (Priority 1)
```bash
curl -s http://192.168.10.90:8090/health
# Must return: {"status": "healthy", "database": "connected"}
```

### Check Router Status
```bash
npx ccr status
# Should show: ✅ Status: Running
```

### Check API Keys
```bash
echo "ANTHROPIC: ${ANTHROPIC_API_KEY:+SET}"
echo "OPENAI: ${OPENAI_API_KEY:+SET}"
# Both should show "SET"
```

---

## 🚨 NUCLEAR OPTION (Last Resort)

If everything is completely broken:

```bash
# 1. Stop everything
npx ccr stop
pkill -f "ccr"

# 2. Fall back to basic Claude
claude

# 3. Knowledge still accessible via API
curl -s http://192.168.10.90:8090/knowledge_items | head -20
```

---

## 📋 RECOVERY PRIORITIES

1. **First**: Get Claude working (`claude` command)
2. **Second**: Verify knowledge system (curl health check)
3. **Third**: Fix router if needed (restart/reset)
4. **Last**: Multi-model testing (`ccr code`)

---

## 🛡️ GUARANTEED WORKING CONFIGURATIONS

| Config | Command | Reliability | Capabilities |
|--------|---------|-------------|--------------|
| Basic Claude | `claude` | 100% | Standard Claude |
| Claude + API | `claude` + curl | 95% | Claude + Knowledge |
| Full Router | `ccr code` | 85% | Multi-model + Knowledge |

---

## 📞 EMERGENCY NUMBERS

- **Knowledge Database**: pgdbsrv (192.168.10.90)
- **API Health**: http://192.168.10.90:8090/health
- **Router Port**: 3456
- **Router Logs**: /tmp/ccr.log

---

**Remember**: The knowledge system is the most valuable part. Router is just the interface. Knowledge persists even if router fails!