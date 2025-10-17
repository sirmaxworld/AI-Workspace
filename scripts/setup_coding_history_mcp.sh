#!/bin/bash

# Coding History MCP Setup Script
# This script sets up the coding history MCP server for Claude Desktop

set -e

echo "🚀 Coding History MCP Setup"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python installation
echo "1. Checking Python installation..."
if command -v /usr/local/bin/python3.11 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python 3.11 found"
else
    echo -e "${RED}✗${NC} Python 3.11 not found at /usr/local/bin/python3.11"
    echo "Please install Python 3.11 first"
    exit 1
fi

# Step 2: Install dependencies
echo ""
echo "2. Installing required Python packages..."
/usr/local/bin/python3.11 -m pip install --quiet --upgrade pip
/usr/local/bin/python3.11 -m pip install --quiet zstandard mcp

if /usr/local/bin/python3.11 -c "import zstandard, mcp" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Some dependencies may be missing, continuing anyway..."
fi

# Step 3: Test core module
echo ""
echo "3. Testing coding history core module..."
if /usr/local/bin/python3.11 /Users/yourox/AI-Workspace/scripts/coding_history_core.py; then
    echo -e "${GREEN}✓${NC} Core module test passed"
else
    echo -e "${YELLOW}⚠${NC} Core module test had issues, but continuing..."
fi

# Step 4: Backup current Claude config
echo ""
echo "4. Backing up current Claude Desktop configuration..."
CONFIG_DIR="$HOME/Library/Application Support/Claude"
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
BACKUP_FILE="$CONFIG_DIR/claude_desktop_config.backup.$(date +%Y%m%d_%H%M%S).json"

if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✓${NC} Configuration backed up to: $BACKUP_FILE"
else
    echo -e "${YELLOW}⚠${NC} No existing configuration found"
fi

# Step 5: Update Claude Desktop configuration
echo ""
echo "5. Updating Claude Desktop configuration..."
cat > "$CONFIG_FILE" << 'EOF'
{
  "mcpServers": {
    "ref": {
      "command": "npx",
      "args": ["-y", "ref-tools-mcp@latest"],
      "env": {
        "REF_API_KEY": "ref-91bc566473a59b3f6b6a"
      }
    },
    "DesktopCommander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
    },
    "semgrep": {
      "command": "/Users/yourox/.local/bin/uvx",
      "args": ["semgrep-mcp"]
    },
    "memory": {
      "command": "/usr/local/bin/python3.11",
      "args": ["/Users/yourox/AI-Workspace/mcp_servers/claude_memory_server.py"]
    },
    "coding-history": {
      "command": "/usr/local/bin/python3.11",
      "args": ["/Users/yourox/AI-Workspace/mcp_servers/coding_history_mcp.py"]
    }
  }
}
EOF

echo -e "${GREEN}✓${NC} Configuration updated successfully"

# Step 6: Create data directories
echo ""
echo "6. Creating data directories..."
mkdir -p /Users/yourox/AI-Workspace/data/coding_history/outputs
mkdir -p /Users/yourox/AI-Workspace/data/coding_history/config
echo -e "${GREEN}✓${NC} Data directories created"

# Step 7: Initialize default configuration
echo ""
echo "7. Initializing default configuration..."
if [ ! -f "/Users/yourox/AI-Workspace/data/coding_history/config/settings.json" ]; then
    cat > /Users/yourox/AI-Workspace/data/coding_history/config/settings.json << 'EOF'
{
  "capture_enabled": true,
  "capture_commands": true,
  "capture_outputs": true,
  "capture_errors": true,
  "max_chunk_size": 100000,
  "compression_level": 3,
  "auto_index": true,
  "auto_embed": false,
  "excluded_patterns": ["password:", "api_key:", "secret:", "token:"],
  "included_projects": [],
  "excluded_projects": []
}
EOF
    echo -e "${GREEN}✓${NC} Default configuration created"
else
    echo -e "${GREEN}✓${NC} Configuration already exists"
fi

# Final instructions
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Coding History MCP Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop completely (Quit and reopen)"
echo "2. Test the integration by asking Claude:"
echo "   'Can you check my coding history stats?'"
echo ""
echo "Available commands in Claude Desktop:"
echo "- Search coding history"
echo "- View recent coding sessions"
echo "- Analyze error patterns"
echo "- Export session history"
echo ""
echo "Documentation: /Users/yourox/AI-Workspace/docs/CODING_HISTORY_MCP_SETUP.md"
echo ""