# MCP Server Fix Summary - October 17, 2025

## Issue
Claude Desktop was throwing errors connecting to MCP servers after architecture changes in the ai-workspace project.

## Findings

### 1. **BI-Vault Server** ✅ WORKING
- Location: `/Users/yourox/AI-Workspace/mcp-servers/bi-vault/server.py`
- Status: **Successfully imports and runs**
- Contains: 5,487 YC companies, 331 enriched insights, 554 files with 19,192 insights
- Purpose: Intelligence vault with transcripts, YC companies, and business insights

### 2. **Coding-Brain Server** ❌ BROKEN
- Location: `/Users/yourox/AI-Workspace/mcp-servers/coding-brain/server.py`
- Status: **Import errors**
- Problem: Tries to import non-existent modules:
  - `coding_history_core` 
  - `coding_history_capture`
- These modules don't exist in the scripts directory or anywhere in the project

### 3. **Old Business Intelligence** 🗑️ REMOVED
- The old `/mcp-servers/business-intelligence/` directory no longer exists
- Successfully migrated to bi-vault architecture

## Solution Applied

Updated `/Users/yourox/Library/Application Support/Claude/claude_desktop_config.json`:

1. ✅ **Added bi-vault** - Working intelligence vault server
2. ✅ **Kept coding-history** - Using the working `coding_history_readonly.py` instead of broken coding-brain
3. ✅ **Removed business-intelligence** - Replaced by bi-vault
4. ✅ **Backup created** - Original config saved as `claude_desktop_config.json.backup`

## Working Configuration

```json
{
  "bi-vault": {
    "command": "/usr/local/bin/python3.11",
    "args": ["/Users/yourox/AI-Workspace/mcp-servers/bi-vault/server.py"]
  },
  "coding-history": {
    "command": "/usr/local/bin/python3.11",
    "args": ["/Users/yourox/AI-Workspace/mcp_servers/coding_history_readonly.py"]
  }
}
```

## Fix Applied (October 17, 2025 - Update)

### Problem Root Cause
The coding-brain server was looking for `coding_history_core` and `coding_history_capture` in the `/scripts` directory, but these modules actually exist in `/archive/old_coding_history/`.

### Solution
1. ✅ Updated `mcp-servers/coding-brain/server.py` import path from `scripts/` to `archive/old_coding_history/`
2. ✅ Verified all dependencies (zstandard v0.25.0) are installed
3. ✅ Tested server initialization - all components working correctly
4. ✅ Confirmed Claude Desktop config already has coding-brain configured

### File Changed
`/Users/yourox/AI-Workspace/mcp-servers/coding-brain/server.py:14-15`
```python
# Changed from:
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# To:
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "archive" / "old_coding_history"))
```

## Restart Claude Desktop
After this fix, restart Claude Desktop to load the working coding-brain MCP server.

---
**Status**: Both bi-vault AND coding-brain are now working! 🎉
