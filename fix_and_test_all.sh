#!/bin/bash
# Comprehensive fix and test script for coding history system

echo "================================================"
echo "🔧 CODING HISTORY SYSTEM - FIX & TEST SCRIPT"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Fix shell snapshots
echo -e "${YELLOW}Step 1: Fixing shell snapshots...${NC}"
python3 /Users/yourox/AI-Workspace/fix_shell_snapshots.py

# Check if fix worked
if grep -q '\\:' ~/.claude/shell-snapshots/snapshot-zsh-*.sh 2>/dev/null; then
    echo -e "${RED}⚠️  Warning: Some snapshots still have escaped colons${NC}"
    echo "Running manual fix..."
    for file in ~/.claude/shell-snapshots/snapshot-zsh-*.sh; do
        if [ -f "$file" ]; then
            sed -i.backup 's/\\:/:/g' "$file"
            echo "  Fixed: $(basename $file)"
        fi
    done
else
    echo -e "${GREEN}✅ All snapshots are clean${NC}"
fi

# Step 2: Archive old implementations
echo ""
echo -e "${YELLOW}Step 2: Archiving old implementations...${NC}"

# Ensure archive directory exists
mkdir -p ~/AI-Workspace/archive/old_coding_history/

# Move old complex files if they exist in scripts
for file in coding_history_shell_hooks.sh coding_history_hooks_simple.sh \
            coding_history_capture.py coding_history_capture_async.py; do
    if [ -f ~/AI-Workspace/scripts/$file ]; then
        mv ~/AI-Workspace/scripts/$file ~/AI-Workspace/archive/old_coding_history/
        echo "  Archived: $file"
    fi
done

echo -e "${GREEN}✅ Old files archived${NC}"

# Step 3: Test basic commands
echo ""
echo -e "${YELLOW}Step 3: Testing basic shell commands...${NC}"

if echo "test" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Echo works${NC}"
else
    echo -e "${RED}❌ Echo failed${NC}"
fi

if pwd > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PWD works${NC}"
else
    echo -e "${RED}❌ PWD failed${NC}"
fi

if ls > /dev/null 2>&1; then
    echo -e "${GREEN}✅ LS works${NC}"
else
    echo -e "${RED}❌ LS failed${NC}"
fi

# Step 4: Test Python
echo ""
echo -e "${YELLOW}Step 4: Testing Python...${NC}"

if python3 -c "print('Python works')" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python3 works${NC}"
else
    echo -e "${RED}❌ Python3 failed${NC}"
fi

# Step 5: Check MCP configuration
echo ""
echo -e "${YELLOW}Step 5: Checking MCP configuration...${NC}"

CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$CONFIG_FILE" ]; then
    if grep -q "coding-history" "$CONFIG_FILE"; then
        echo -e "${GREEN}✅ Coding history MCP is configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Coding history MCP not in config${NC}"
        echo "  To add it, run: bash ~/AI-Workspace/enable_coding_history_mcp.sh"
    fi
else
    echo -e "${RED}❌ Claude config not found${NC}"
fi

# Step 6: Test coding history hooks
echo ""
echo -e "${YELLOW}Step 6: Testing coding history hooks...${NC}"

if [ -f ~/AI-Workspace/scripts/coding_history_hooks_minimal.sh ]; then
    echo -e "${GREEN}✅ Minimal hooks exist${NC}"

    # Check if enabled in .zshrc
    if grep -q "coding_history_hooks_minimal.sh" ~/.zshrc; then
        echo -e "${GREEN}✅ Hooks are enabled in .zshrc${NC}"
    else
        echo -e "${YELLOW}⚠️  Hooks not enabled in .zshrc${NC}"
        echo "  To enable, run: bash ~/AI-Workspace/enable_coding_history.sh"
    fi
else
    echo -e "${RED}❌ Minimal hooks not found${NC}"
fi

# Step 7: Performance test
echo ""
echo -e "${YELLOW}Step 7: Performance test...${NC}"

# Time 100 echo commands
START=$(date +%s%N)
for i in {1..100}; do
    echo "test" > /dev/null 2>&1
done
END=$(date +%s%N)

# Calculate time in milliseconds
DIFF=$((($END - $START) / 1000000))
AVG=$(($DIFF / 100))

echo "  100 commands took: ${DIFF}ms"
echo "  Average per command: ${AVG}ms"

if [ $AVG -lt 10 ]; then
    echo -e "${GREEN}✅ Performance is excellent (<10ms per command)${NC}"
elif [ $AVG -lt 50 ]; then
    echo -e "${YELLOW}⚠️  Performance is acceptable (${AVG}ms per command)${NC}"
else
    echo -e "${RED}❌ Performance issue detected (${AVG}ms per command)${NC}"
fi

# Step 8: Check data directories
echo ""
echo -e "${YELLOW}Step 8: Checking data directories...${NC}"

if [ -d ~/AI-Workspace/data/coding_history ]; then
    echo -e "${GREEN}✅ Coding history data directory exists${NC}"

    # Check database
    if [ -f ~/AI-Workspace/data/coding_history/sessions.db ]; then
        SIZE=$(du -h ~/AI-Workspace/data/coding_history/sessions.db | cut -f1)
        echo "  Database size: $SIZE"
    fi
else
    echo -e "${YELLOW}⚠️  Coding history directory not found${NC}"
    mkdir -p ~/AI-Workspace/data/coding_history
    echo "  Created directory"
fi

# Final summary
echo ""
echo "================================================"
echo "📊 SUMMARY"
echo "================================================"

echo ""
echo "Next steps:"
echo "1. If shell still broken in Claude Desktop:"
echo "   - Completely quit Claude Desktop (Cmd+Q)"
echo "   - Reopen Claude Desktop"
echo ""
echo "2. To enable coding history:"
echo "   bash ~/AI-Workspace/enable_coding_history.sh"
echo ""
echo "3. To add MCP server to Claude:"
echo "   bash ~/AI-Workspace/enable_coding_history_mcp.sh"
echo ""
echo "4. To run full health check:"
echo "   python3 ~/AI-Workspace/health_check.py"

echo ""
echo -e "${GREEN}✅ Fix and test script complete!${NC}"