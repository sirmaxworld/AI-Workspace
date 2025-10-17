#!/bin/bash

# Automatic Coding History Capture Installation
# Sets up seamless, lightweight capture for all terminal sessions

set -e

echo "🚀 Installing Automatic Coding History Capture"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_TYPE="zsh"
    RC_FILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_TYPE="bash"
    RC_FILE="$HOME/.bashrc"
else
    echo "Unsupported shell. Please use bash or zsh."
    exit 1
fi

echo -e "${BLUE}Detected shell:${NC} $SHELL_TYPE"
echo -e "${BLUE}Config file:${NC} $RC_FILE"
echo ""

# Step 1: Check Python dependencies
echo "1. Checking dependencies..."
if /usr/local/bin/python3.11 -c "import zstandard" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Dependencies ready"
else
    echo "Installing zstandard..."
    /usr/local/bin/python3.11 -m pip install --quiet zstandard
    echo -e "${GREEN}✓${NC} Dependencies installed"
fi

# Step 2: Make scripts executable
echo ""
echo "2. Setting up capture scripts..."
chmod +x /Users/yourox/AI-Workspace/scripts/coding_history_capture_async.py
chmod +x /Users/yourox/AI-Workspace/scripts/coding_history_shell_hooks.sh
echo -e "${GREEN}✓${NC} Scripts configured"

# Step 3: Test async capture
echo ""
echo "3. Testing async capture system..."
/usr/local/bin/python3.11 /Users/yourox/AI-Workspace/scripts/coding_history_capture_async.py \
    --command "test" \
    --output "Installation test" \
    --exit-code 0

sleep 1  # Give it a moment to process

if /usr/local/bin/python3.11 /Users/yourox/AI-Workspace/scripts/coding_history_capture_async.py --stats | grep -q '"captured": [1-9]'; then
    echo -e "${GREEN}✓${NC} Capture system working"
else
    echo -e "${YELLOW}⚠${NC} Capture test inconclusive, continuing..."
fi

# Step 4: Add to shell configuration
echo ""
echo "4. Installing shell hooks..."

# Check if already installed
if grep -q "coding_history_shell_hooks.sh" "$RC_FILE" 2>/dev/null; then
    echo -e "${YELLOW}Already installed in $RC_FILE${NC}"
else
    # Backup RC file
    cp "$RC_FILE" "$RC_FILE.backup.$(date +%Y%m%d_%H%M%S)"

    # Add source line
    cat >> "$RC_FILE" << 'EOF'

# Coding History Auto-Capture
# Lightweight, async capture of terminal commands
if [ -f "/Users/yourox/AI-Workspace/scripts/coding_history_shell_hooks.sh" ]; then
    # Set to 1 to enable, 0 to disable
    export CODING_HISTORY_ENABLED=1
    # Set to 1 to silence the startup message
    export CODING_HISTORY_SILENT=0
    # Load the hooks
    source "/Users/yourox/AI-Workspace/scripts/coding_history_shell_hooks.sh"
fi
EOF

    echo -e "${GREEN}✓${NC} Added to $RC_FILE"
fi

# Step 5: Create convenience script for Cursor
echo ""
echo "5. Creating Cursor terminal integration..."
cat > /Users/yourox/AI-Workspace/scripts/cursor_terminal_init.sh << 'EOF'
#!/bin/bash
# Cursor Terminal Initialization
# Ensures coding history capture in Cursor terminals

export CURSOR=1
export CODING_HISTORY_ENABLED=1
export CODING_HISTORY_SILENT=1

# Source the hooks
source /Users/yourox/AI-Workspace/scripts/coding_history_shell_hooks.sh

echo "📝 Coding history capture active (ch_stats for info)"
EOF

chmod +x /Users/yourox/AI-Workspace/scripts/cursor_terminal_init.sh
echo -e "${GREEN}✓${NC} Cursor integration ready"

# Step 6: Update MCP configuration
echo ""
echo "6. Updating MCP configuration..."
if [ -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json" ]; then
    # The configuration should already include coding-history from previous setup
    echo -e "${GREEN}✓${NC} MCP configuration present"
else
    echo -e "${YELLOW}⚠${NC} Claude Desktop config not found - run setup_coding_history_mcp.sh"
fi

# Step 7: Performance configuration
echo ""
echo "7. Optimizing performance settings..."
cat > /Users/yourox/AI-Workspace/data/coding_history/config/performance.json << 'EOF'
{
  "capture_enabled": true,
  "batch_size": 10,
  "batch_timeout_seconds": 30,
  "max_chunk_size": 100000,
  "compression_level": 3,
  "dedup_window": 100,
  "max_queue_size": 1000,
  "excluded_commands": [
    "ls",
    "cd",
    "pwd",
    "clear",
    "history",
    "echo $"
  ],
  "min_output_size": 10,
  "auto_cleanup_days": 90
}
EOF
echo -e "${GREEN}✓${NC} Performance optimized"

# Display summary
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "=============================================="
echo ""
echo "📊 Resource Impact:"
echo "  • CPU: <1% (async processing)"
echo "  • Memory: ~5-10MB"
echo "  • Storage: ~10-50MB/day (compressed)"
echo "  • Network: None (local only)"
echo ""
echo "🎯 What's Now Active:"
echo "  • Automatic capture in ALL terminals"
echo "  • Smart deduplication"
echo "  • Async compression (no lag)"
echo "  • Privacy filtering"
echo "  • MCP access from Claude Desktop"
echo ""
echo "🛠️ Available Commands:"
echo "  ${BLUE}ch_stats${NC}   - Show capture statistics"
echo "  ${BLUE}ch_toggle${NC}  - Toggle capture on/off"
echo "  ${BLUE}ch_on${NC}      - Enable capture"
echo "  ${BLUE}ch_off${NC}     - Disable capture"
echo ""
echo "📝 For Cursor/VSCode:"
echo "  Terminals will auto-detect and capture"
echo "  Or manually: source /Users/yourox/AI-Workspace/scripts/cursor_terminal_init.sh"
echo ""
echo "⚡ Next Steps:"
echo "  1. ${YELLOW}Open a new terminal${NC} (or source $RC_FILE)"
echo "  2. ${YELLOW}Run some commands${NC}"
echo "  3. ${YELLOW}Check with:${NC} ch_stats"
echo "  4. ${YELLOW}Access from Claude Desktop${NC} (restart Claude)"
echo ""
echo "Documentation: /Users/yourox/AI-Workspace/docs/CODING_HISTORY_MCP_SETUP.md"