# 📚 CODING HISTORY SYSTEM - RESCUE & ARCHITECTURE GUIDE

## 📅 Last Updated: 2025-01-17

## 🏗️ System Architecture

### Overview
Two separate but complementary systems for knowledge management:

1. **Memory Server** (`claude_memory_server.py`)
   - Stores high-level decisions and learnings
   - Manual trigger via `save_memory()` tool
   - Dual-layer: JSON + Mem0 vector DB
   - Location: `/data/claude_memory_json/` and `/data/claude_memory_qdrant/`

2. **Coding History** (`coding_history_summary_mcp.py`)
   - Captures session summaries (NOT raw terminal output)
   - Automatic async capture with <1ms overhead
   - Stores: intent → actions → outcome
   - Location: `/data/coding_history/`

### Data Flow
```
User Action → AI Assistant → Terminal Commands
                ↓
         Async Hook (<1ms)
                ↓
         Background Processor
                ↓
         Smart Summary
                ↓
    Coding History Database
                ↓
         MCP Server → All AI Systems
```

## 🔧 Shell Environment Fix

### Problem
Claude Desktop incorrectly escapes colons in PATH exports:
- Converts: `/usr/bin:/bin`
- To: `/usr/bin\:/bin`
- Result: Shell parse errors

### Solution

#### Quick Fix (From Terminal)
```bash
# 1. Fix existing snapshots
cd ~/AI-Workspace
python3 fix_shell_snapshots.py

# 2. Verify fix
grep "export PATH" ~/.claude/shell-snapshots/*.sh | head -2
# Should show clean colons, no backslashes

# 3. Restart Claude Desktop
```

#### Manual Fix (If script fails)
```bash
# Remove escaped colons from all snapshots
for file in ~/.claude/shell-snapshots/snapshot-zsh-*.sh; do
  sed -i.backup 's/\\:/:/g' "$file"
done

# Or delete all and start fresh
rm ~/.claude/shell-snapshots/snapshot-zsh-*.sh
```

## 🚀 Enable/Disable Features

### Enable Coding History Capture
```bash
# Add to ~/.zshrc
source ~/AI-Workspace/scripts/coding_history_hooks_minimal.sh

# Or use the enable script
bash ~/AI-Workspace/enable_coding_history.sh
```

### Disable Coding History
```bash
# In terminal
ch_off

# Or remove from ~/.zshrc
# Comment out: source ~/AI-Workspace/scripts/coding_history_hooks_minimal.sh
```

### Add to Claude Desktop
```json
// Add to ~/Library/Application Support/Claude/claude_desktop_config.json
"coding-history": {
  "command": "/usr/local/bin/python3.11",
  "args": ["/Users/yourox/AI-Workspace/mcp_servers/coding_history_summary_mcp.py"]
}
```

## 🔍 Troubleshooting

### Issue: Shell commands fail with "parse error"
```bash
# Cause: Escaped colons in PATH
# Fix:
python3 ~/AI-Workspace/fix_shell_snapshots.py
# Then restart Claude Desktop
```

### Issue: Coding history not capturing
```bash
# Check if enabled
echo $CODING_HISTORY_ENABLED
# Should be: 1

# Enable if needed
ch_on
```

### Issue: MCP server not appearing in Claude
```bash
# 1. Check config is correct
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 2. Completely quit Claude Desktop (Cmd+Q)
# 3. Reopen Claude Desktop
```

### Issue: Performance degradation
```bash
# Check async queue size
python3 -c "
from coding_history_summary import get_queue_stats
print(get_queue_stats())
"

# Clear if backed up
python3 -c "
from coding_history_summary import clear_queue
clear_queue()
"
```

## 📁 File Locations

### Core Files
- `/AI-Workspace/mcp_servers/coding_history_summary_mcp.py` - MCP server
- `/AI-Workspace/scripts/coding_history_summary.py` - Summary processor
- `/AI-Workspace/scripts/coding_history_hooks_minimal.sh` - Shell hooks
- `/AI-Workspace/fix_shell_snapshots.py` - Shell fix utility

### Data Storage
- `/data/coding_history/sessions.db` - Summary database
- `/data/coding_history/config/settings.json` - Configuration
- `/data/claude_memory_json/` - Memory server JSON
- `/data/claude_memory_qdrant/` - Memory server vectors

### Archives
- `/archive/old_coding_history/` - Old complex implementations

## 🧪 Testing Procedures

### 1. Shell Environment Test
```bash
# After fixing snapshots, in NEW Claude session:
echo "Test" && pwd && date
# Should work without errors
```

### 2. Performance Test
```bash
# Measure hook overhead
time for i in {1..100}; do echo "test" > /dev/null; done
# Should be negligible difference with/without hooks
```

### 3. MCP Access Test
In Claude Desktop:
```
"Can you check my coding history?"
"What sessions do I have today?"
"Search for TypeScript errors in my history"
```

### 4. Full System Test
```bash
# Run comprehensive health check
python3 ~/AI-Workspace/health_check.py
```

## 🆘 Emergency Recovery

### If everything breaks:

1. **Reset Shell Environment**
```bash
# From regular terminal (not Claude)
rm -rf ~/.claude/shell-snapshots/
cp ~/.zshrc ~/.zshrc.backup
grep -v "coding_history" ~/.zshrc > ~/.zshrc.tmp && mv ~/.zshrc.tmp ~/.zshrc
```

2. **Disable All MCP Servers**
```bash
# Backup config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/Desktop/backup.json

# Reset to minimal
echo '{"mcpServers": {}}' > ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

3. **Restart Everything**
```bash
# Quit Claude Desktop
# Restart Mac if needed
# Start fresh
```

## 🎯 Design Principles

1. **Separation of Concerns**
   - Memory: High-level knowledge
   - Coding History: Session summaries
   - Don't mix raw data with insights

2. **Async Everything**
   - Never block terminal
   - Process in background
   - Queue and batch operations

3. **Smart Summaries**
   - Capture intent, not raw output
   - Group related commands
   - Extract patterns and learnings

4. **Clean Architecture**
   - Archive old code
   - Keep minimal active set
   - Document everything

## 📊 Expected Performance

- Shell hook overhead: <1ms
- Background processing: 50-100ms per batch
- MCP query response: <200ms
- Memory usage: <50MB for 10,000 sessions
- No noticeable terminal slowdown

## 🔄 Update History

- 2025-01-17: Initial smart summary system design
- 2025-01-17: Fixed PATH escaping issue in shell snapshots
- 2025-01-17: Separated coding history from memory server
- 2025-01-17: Implemented async processing for zero overhead

---

**For AI Systems:** This is the authoritative guide for the coding history system. If shell issues occur, run the fix script first. The system uses smart summaries, not raw data capture.