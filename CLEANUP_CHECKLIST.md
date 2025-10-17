# 🧹 Cleanup Checklist - Secure Architecture Migration

After the migration is stable (recommend waiting 1 week), you can clean up old files.

---

## ✅ Immediate Actions (Done)

- [x] Install permanent snapshot fix
- [x] Migrate to independent capture system
- [x] Deploy read-only MCP server
- [x] Update Claude Desktop configuration
- [x] Create backups
- [x] Test new architecture

---

## 📦 Files to Archive (After 1 Week)

Move these to `/Users/yourox/AI-Workspace/archive/old_coupled_system/`:

### **Old MCP Server (Now Obsolete):**
```
mcp_servers/coding_history_summary_mcp.py
```
**Replaced by:** `mcp_servers/coding_history_readonly.py` (read-only)

### **Old Capture System (Now Obsolete):**
```
scripts/coding_history_summary.py
scripts/coding_history_hooks_minimal.sh
scripts/coding_history_hooks_simple.sh
```
**Replaced by:** `scripts/coding_history_hooks_independent.sh`

### **Shell Snapshot Tools (No Longer Needed):**
```
fix_shell_snapshots.py
fix_and_test_all.sh
auto_fix_shell_snapshots.sh
test_coding_history_complete.py
test_mcp_direct.py
```
**Why:** Independent capture bypasses Claude Desktop's shell snapshots entirely

### **Old Documentation:**
```
CODING_HISTORY_RESCUE.md
```
**Replaced by:** `SECURE_ARCHITECTURE.md` + `MIGRATION_COMPLETE.md`

---

## 🗑️ Files to Delete (After Testing)

### **Temporary Files:**
```
snapshot_watcher.py
snapshot_watcher.log
.coding_history_queue.txt (if empty)
```
**Why:** Snapshot watching no longer needed with independent capture

### **Old Test Scripts:**
```
enable_coding_history_mcp.py
test_api.js (if exists)
```

### **Shell Snapshot Backups:**
```
~/.claude/shell-snapshots/*.backup
```
**When:** After verifying no more snapshot errors occur

---

## 📁 What to Keep

### **Active System:**
```
✅ scripts/coding_history_hooks_independent.sh
✅ scripts/process_history_queue.py
✅ mcp_servers/coding_history_readonly.py
✅ .coding_history.db (database)
```

### **Configuration:**
```
✅ docs/SECURE_ARCHITECTURE.md
✅ MIGRATION_COMPLETE.md
✅ migrate_to_secure_architecture.sh
```

### **Backups:**
```
✅ backups/20251016_205937/ (keep indefinitely)
```

### **Other Active MCPs:**
```
✅ mcp_servers/claude_memory_server.py
✅ mcp_servers/business-intelligence/ (if used)
```

---

## 🧪 Before Cleanup: Verification Tests

Run these tests before archiving old files:

### **1. Independent Capture Works**
```bash
# In regular terminal (not Claude Desktop)
ch_status
# Should show: ✅ ENABLED with background processor running
```

### **2. Database Growing**
```bash
# Run some commands, wait 10 seconds
ls
pwd
date

# Check database
python3 -c "
import sqlite3
conn = sqlite3.connect('$HOME/AI-Workspace/.coding_history.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM sessions WHERE timestamp > datetime(\"now\", \"-1 hour\")')
print(f'Recent sessions: {cursor.fetchone()[0]}')
"
# Should show > 0
```

### **3. Claude Desktop Read-Only Access**
Ask Claude Desktop these questions:
- "Show my recent coding history"
- "What commands did I run today?"
- "Search my history for 'python'"

All should work and show data.

### **4. No Shell Errors**
Run bash commands in Claude Desktop - should work without snapshot errors.

### **5. Capture Works Everywhere**
Test in:
- [ ] iTerm
- [ ] Terminal.app
- [ ] Cursor
- [ ] VS Code terminal
- [ ] Claude Desktop (optional)

---

## 🔄 Cleanup Script

After verification, run this to archive old files:

```bash
#!/bin/bash
# Archive old system files

ARCHIVE_DIR="$HOME/AI-Workspace/archive/old_coupled_system_$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"

echo "Archiving old files to: $ARCHIVE_DIR"

# Archive old MCP
mv ~/AI-Workspace/mcp_servers/coding_history_summary_mcp.py "$ARCHIVE_DIR/" 2>/dev/null

# Archive old capture
mv ~/AI-Workspace/scripts/coding_history_summary.py "$ARCHIVE_DIR/" 2>/dev/null
mv ~/AI-Workspace/scripts/coding_history_hooks_minimal.sh "$ARCHIVE_DIR/" 2>/dev/null
mv ~/AI-Workspace/scripts/coding_history_hooks_simple.sh "$ARCHIVE_DIR/" 2>/dev/null

# Archive shell tools
mv ~/AI-Workspace/fix_shell_snapshots.py "$ARCHIVE_DIR/" 2>/dev/null
mv ~/AI-Workspace/fix_and_test_all.sh "$ARCHIVE_DIR/" 2>/dev/null
mv ~/AI-Workspace/auto_fix_shell_snapshots.sh "$ARCHIVE_DIR/" 2>/dev/null
mv ~/AI-Workspace/test_coding_history_complete.py "$ARCHIVE_DIR/" 2>/dev/null

# Archive old docs
mv ~/AI-Workspace/CODING_HISTORY_RESCUE.md "$ARCHIVE_DIR/" 2>/dev/null

echo "✅ Cleanup complete! Old files archived to: $ARCHIVE_DIR"
echo "You can delete the archive directory if no longer needed."
```

Save as: `/Users/yourox/AI-Workspace/cleanup_old_files.sh`

---

## ⚠️ Warning

**DO NOT** delete these files - they are still active:
- `.zshrc` (updated with new hooks)
- `claude_desktop_config.json` (updated for read-only MCP)
- `.coding_history.db` (active database)
- Anything in `scripts/` that is NOT in the archive list

---

## 📊 Space Saved

After cleanup, you'll save approximately:
- **Old Python files:** ~50 KB
- **Old shell scripts:** ~20 KB
- **Test files:** ~30 KB
- **Shell snapshot backups:** ~500 KB
- **Total:** ~600 KB

Not much, but cleaner codebase!

---

## 🎯 Final State

After cleanup:
```
/Users/yourox/AI-Workspace/
├── scripts/
│   ├── coding_history_hooks_independent.sh  ✅ Active
│   └── process_history_queue.py             ✅ Active
├── mcp_servers/
│   ├── coding_history_readonly.py           ✅ Active
│   └── claude_memory_server.py              ✅ Active
├── docs/
│   └── SECURE_ARCHITECTURE.md               ✅ Active
├── archive/
│   └── old_coupled_system_20251016/         📦 Archived
├── backups/
│   └── 20251016_205937/                     💾 Backup
└── .coding_history.db                       ✅ Active
```

Clean, minimal, secure! 🎉