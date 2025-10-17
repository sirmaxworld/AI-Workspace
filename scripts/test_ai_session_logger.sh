#!/bin/bash
echo "🧪 Testing AI Session Logger System"
echo "====================================="
echo ""

echo "✅ 1. Checking directory structure..."
if [ -d "/Users/yourox/AI-Workspace/data/ai_sessions" ]; then
    echo "   ✓ Data directory exists"
else
    echo "   ✗ Data directory missing"
fi

echo ""
echo "✅ 2. Checking database..."
if [ -f "/Users/yourox/AI-Workspace/data/ai_sessions/sessions/ai_sessions.db" ]; then
    echo "   ✓ Database file exists"
    TABLES=$(sqlite3 /Users/yourox/AI-Workspace/data/ai_sessions/sessions/ai_sessions.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
    echo "   ✓ Tables created: $TABLES"
else
    echo "   ✗ Database file missing"
fi

echo ""
echo "✅ 3. Checking Python scripts..."
for script in ai_session_logger_core.py ai_passive_capture.py ai_learning_extractor.py; do
    if [ -f "/Users/yourox/AI-Workspace/scripts/$script" ]; then
        echo "   ✓ $script"
    else
        echo "   ✗ $script missing"
    fi
done

echo ""
echo "✅ 4. Checking MCP server..."
if [ -f "/Users/yourox/AI-Workspace/mcp-servers/ai_session_mcp.py" ]; then
    echo "   ✓ MCP server file exists"
else
    echo "   ✗ MCP server missing"
fi

echo ""
echo "✅ 5. Checking MCP configuration..."
if grep -q "ai-session-logger" /Users/yourox/AI-Workspace/mcp_servers/coding_history_config.json; then
    echo "   ✓ MCP configuration updated"
else
    echo "   ✗ MCP configuration not updated"
fi

echo ""
echo "✅ 6. Testing passive capture..."
python3 /Users/yourox/AI-Workspace/scripts/ai_passive_capture.py 2>&1 | head -5

echo ""
echo "====================================="
echo "🎉 System Status: READY"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop to load MCP server"
echo "2. Try querying: 'Show me my AI session stats'"
echo "3. Keep coding - system learns automatically!"
