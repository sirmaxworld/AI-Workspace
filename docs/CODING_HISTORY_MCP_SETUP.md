# Coding History MCP Server Setup Guide

## Overview
The Coding History MCP Server provides seamless access to your terminal output history and coding sessions directly from Claude Desktop. It captures, compresses, and indexes all your coding activities for easy retrieval and analysis.

## Status Check

### Core Components
- **coding_history_core.py**: ✅ Implemented (Database, compression, configuration)
- **coding_history_mcp.py**: ✅ Created (MCP server with full tool suite)
- **MCP Configuration**: ✅ Ready to deploy

## Installation Steps

### 1. Install Required Dependencies

```bash
pip3 install zstandard mcp
```

### 2. Test the Core Module

```bash
python3 /Users/yourox/AI-Workspace/scripts/coding_history_core.py
```

Expected output:
```
Testing Coding History Core...
✓ Created session: [session_id]...
✓ Added chunk: [chunk_id]...
✓ Found N chunks
✓ Decompressed content: [preview]...
✓ Capture enabled: True
✅ All tests passed!
```

### 3. Update Claude Desktop Configuration

To add the coding history server to Claude Desktop, update your configuration:

```bash
# Backup current config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.backup.json

# Apply new configuration with coding history
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
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

echo "Configuration updated! Restart Claude Desktop to apply changes."
```

### 4. Restart Claude Desktop
After updating the configuration, completely quit and restart Claude Desktop for the changes to take effect.

## Available MCP Tools

Once configured, you'll have access to these tools in Claude Desktop:

### Resources
- **`history://stats`** - Get coding history statistics
- **`history://recent`** - View recent coding history

### Tools

#### 1. `search_history`
Search your coding history with filters:
```
Search my coding history for "npm install" in the last 24 hours
```

#### 2. `get_session_details`
Get details about a specific coding session:
```
Show me details for session [session_id]
```

#### 3. `toggle_capture`
Enable or disable history capture:
```
Turn off coding history capture
```

#### 4. `get_error_patterns`
Analyze common errors in your projects:
```
What are the most common errors in my AI-Workspace project?
```

#### 5. `export_session_history`
Export history for documentation or analysis:
```
Export my coding history for today as text
```

#### 6. `create_session`
Start a new coding session:
```
Create a new coding session for my AI-Workspace project
```

#### 7. `add_output`
Manually add output to a session:
```
Add this error output to my current session
```

## Testing the Integration

### Test 1: Check Server Status
In Claude Desktop, ask:
```
Can you check my coding history stats?
```

Expected: Statistics showing sessions, chunks, and capture status.

### Test 2: Search History
```
Search my coding history for Python errors
```

Expected: List of error chunks with previews.

### Test 3: Analyze Patterns
```
What error patterns do you see in my recent coding?
```

Expected: Analysis of common error types with examples.

## Data Storage

Your coding history is stored in:
- **Database**: `/Users/yourox/AI-Workspace/data/coding_history/sessions.db`
- **Compressed outputs**: `/Users/yourox/AI-Workspace/data/coding_history/outputs/`
- **Configuration**: `/Users/yourox/AI-Workspace/data/coding_history/config/settings.json`

## Configuration Options

Edit `/Users/yourox/AI-Workspace/data/coding_history/config/settings.json`:

```json
{
  "capture_enabled": true,
  "capture_commands": true,
  "capture_outputs": true,
  "capture_errors": true,
  "max_chunk_size": 100000,
  "compression_level": 3,
  "auto_index": true,
  "excluded_patterns": ["password:", "api_key:", "secret:", "token:"],
  "included_projects": [],
  "excluded_projects": []
}
```

## Privacy & Security

The coding history system:
- Automatically filters sensitive data (passwords, API keys, secrets)
- Compresses all captured data using Zstandard
- Stores everything locally on your machine
- Can be toggled on/off at any time
- Respects project-specific inclusion/exclusion rules

## Troubleshooting

### Issue: MCP server not appearing in Claude Desktop
**Solution**: Ensure you've restarted Claude Desktop completely after updating the config.

### Issue: No history being captured
**Solution**: Check if capture is enabled:
```bash
python3 -c "from coding_history_core import CaptureConfig; print(CaptureConfig().is_capture_enabled())"
```

### Issue: Database errors
**Solution**: Check database integrity:
```bash
sqlite3 /Users/yourox/AI-Workspace/data/coding_history/sessions.db "PRAGMA integrity_check;"
```

## Next Steps

1. **Install dependencies** (if not already installed)
2. **Test the core module** to ensure it's working
3. **Update Claude Desktop config** with the new server
4. **Restart Claude Desktop**
5. **Test the integration** with the provided test commands

Once set up, your coding history will be automatically captured and searchable through Claude Desktop!