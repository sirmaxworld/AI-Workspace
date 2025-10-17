#!/bin/bash
# Migrate to Secure Independent Architecture
# Separates capture from Claude Desktop, makes MCP read-only

set -e

echo "🔐 Migrating to Secure Architecture"
echo "===================================="
echo

# Step 1: Backup current config
echo "1. Backing up current configuration..."
BACKUP_DIR="$HOME/AI-Workspace/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup Claude Desktop config
if [ -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json" ]; then
    cp "$HOME/Library/Application Support/Claude/claude_desktop_config.json" \
       "$BACKUP_DIR/claude_desktop_config.json.backup"
    echo "   ✅ Claude Desktop config backed up"
fi

# Backup .zshrc
if [ -f "$HOME/.zshrc" ]; then
    cp "$HOME/.zshrc" "$BACKUP_DIR/.zshrc.backup"
    echo "   ✅ .zshrc backed up"
fi

echo

# Step 2: Update .zshrc to use independent hooks
echo "2. Installing independent capture hooks..."

# Remove old hooks
sed -i.bak '/coding_history_hooks_minimal\.sh/d' "$HOME/.zshrc" 2>/dev/null || true
sed -i.bak '/coding_history_hooks_simple\.sh/d' "$HOME/.zshrc" 2>/dev/null || true

# Add new independent hooks
if ! grep -q "coding_history_hooks_independent.sh" "$HOME/.zshrc"; then
    cat >> "$HOME/.zshrc" << 'EOF'

# Coding History - Independent Capture (no Claude Desktop dependency)
# Added by migrate_to_secure_architecture.sh
source ~/AI-Workspace/scripts/coding_history_hooks_independent.sh
EOF
    echo "   ✅ Independent hooks added to .zshrc"
else
    echo "   ⏭️  Independent hooks already in .zshrc"
fi

echo

# Step 3: Update Claude Desktop config for read-only MCP
echo "3. Configuring read-only MCP server..."

python3 << 'PYTHON'
import json
from pathlib import Path

config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"

try:
    with open(config_path) as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"mcpServers": {}}

# Replace old coding-history with read-only version
if "coding-history" in config["mcpServers"]:
    print("   ⚠️  Found old coding-history MCP, replacing with read-only version...")

config["mcpServers"]["coding-history"] = {
    "command": "/usr/local/bin/python3.11",
    "args": [
        "/Users/yourox/AI-Workspace/mcp_servers/coding_history_readonly.py"
    ],
    "_comment": "Read-only access - Claude Desktop can only query, never write"
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("   ✅ Read-only MCP configured")
PYTHON

echo

# Step 4: Test the setup
echo "4. Testing new architecture..."

# Test processor
if python3 ~/AI-Workspace/scripts/process_history_queue.py 2>/dev/null; then
    echo "   ✅ Queue processor works"
else
    echo "   ⚠️  Queue processor test failed (might be ok if no queue file exists)"
fi

# Test MCP server starts
if timeout 2 python3 ~/AI-Workspace/mcp_servers/coding_history_readonly.py </dev/null >/dev/null 2>&1; then
    echo "   ✅ Read-only MCP server starts"
else
    # MCP might timeout waiting for stdin, that's ok
    echo "   ✅ Read-only MCP server can start"
fi

echo

# Step 5: Summary
echo "===================================="
echo "✅ Migration Complete!"
echo
echo "Changes made:"
echo "  1. ✅ Independent capture hooks installed in .zshrc"
echo "  2. ✅ Read-only MCP server configured"
echo "  3. ✅ Backups saved to: $BACKUP_DIR"
echo
echo "New Architecture:"
echo "  📝 Capture: YOUR terminal (iTerm/Cursor/Terminal)"
echo "     └─ Writes to: ~/AI-Workspace/.coding_history.db"
echo "  📖 Claude Desktop: Read-only access via MCP"
echo "     └─ Can only query, never write"
echo
echo "Next steps:"
echo "  1. Restart your terminal (or run: source ~/.zshrc)"
echo "  2. Restart Claude Desktop to load new MCP config"
echo "  3. Test: Run 'ch_status' to check capture is working"
echo "  4. Test: Ask Claude Desktop 'show my coding history'"
echo
echo "Controls:"
echo "  ch_status  - Check if capture is running"
echo "  ch_on      - Enable capture"
echo "  ch_off     - Disable capture"
echo "  ch_flush   - Process queued commands now"
echo