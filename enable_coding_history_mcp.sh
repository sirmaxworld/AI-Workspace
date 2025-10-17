#!/bin/bash
# Enable Coding History MCP in Claude Desktop

echo "🔧 Enabling Coding History MCP Server in Claude Desktop"
echo "========================================================"
echo ""

CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Claude Desktop config not found at: $CONFIG_FILE"
    echo "Please ensure Claude Desktop is installed"
    exit 1
fi

# Backup current config
echo "📋 Backing up current configuration..."
cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup created"

# Check if coding-history already exists
if grep -q '"coding-history"' "$CONFIG_FILE"; then
    echo "✅ Coding history MCP is already configured"
else
    echo "📝 Adding coding history MCP to configuration..."

    # Use Python to safely modify JSON
    python3 - <<EOF
import json

config_path = "$CONFIG_FILE"

# Read current config
with open(config_path, 'r') as f:
    config = json.load(f)

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add coding-history server
config['mcpServers']['coding-history'] = {
    "command": "/usr/local/bin/python3.11",
    "args": ["/Users/yourox/AI-Workspace/mcp_servers/coding_history_summary_mcp.py"]
}

# Write updated config
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Configuration updated successfully")
EOF
fi

echo ""
echo "📋 Current MCP Servers configured:"
python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
    for server in config.get('mcpServers', {}).keys():
        print(f'  - {server}')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Quit Claude Desktop completely (Cmd+Q)"
echo "2. Reopen Claude Desktop"
echo "3. Test with: 'Can you check my coding history?'"
echo ""
echo "The new MCP server provides:"
echo "  - Session summaries (not raw output)"
echo "  - Error analysis"
echo "  - Productivity insights"
echo "  - Lightweight and fast queries"