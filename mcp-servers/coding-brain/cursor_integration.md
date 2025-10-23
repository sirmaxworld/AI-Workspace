# Coding History MCP Server - Cursor Integration Guide

## Overview
The Coding History MCP Server provides persistent memory of all terminal outputs, commands, and errors across your coding sessions. It enables Cursor to access your complete development history with advanced search capabilities.

## Features
- ✅ **Automatic Capture**: Records all terminal outputs, commands, and errors
- ✅ **Toggle Control**: Enable/disable capture globally or per-project
- ✅ **Compression**: Efficient storage with zstd compression
- ✅ **Advanced Search**: Keyword, time-based, and semantic search
- ✅ **Error Learning**: Find similar errors and their solutions
- ✅ **Project Analytics**: Track coding patterns and progress
- ✅ **Privacy Control**: Automatic filtering of sensitive data

## Installation

### 1. Install Dependencies
```bash
# Core dependencies (already installed)
pip3 install zstandard

# Optional: Vector search capabilities
pip3 install qdrant-client sentence-transformers numpy
```

### 2. Configure Cursor

Add to your Cursor MCP settings (`~/.cursor/mcp/settings.json` or via Cursor settings):

```json
{
  "mcpServers": {
    "coding-history": {
      "command": "python3",
      "args": [
        "/Users/yourox/AI-Workspace/mcp-servers/coding-history/server.py"
      ],
      "env": {},
      "disabled": false
    }
  }
}
```

### 3. Configure Capture Settings

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
  "auto_embed": false,
  "excluded_patterns": [
    "password:",
    "api_key:",
    "secret:",
    "token:"
  ],
  "included_projects": [],
  "excluded_projects": []
}
```

## Usage in Cursor

### Basic Commands

```typescript
// Toggle capture on/off
toggle_capture(true)  // Enable
toggle_capture(false) // Disable

// Check status
get_capture_status()

// Search history
search_history({
  query: "npm install error",
  project_path: "/path/to/project",
  hours_ago: 24,
  limit: 10
})

// Get recent errors with solutions
get_errors({
  project_path: "/current/project",
  with_solutions: true
})

// Get project summary
get_project_summary("/path/to/project", 7)  // Last 7 days
```

### Manual Capture

```typescript
// Start a capture session
start_capture("/path/to/project", "cursor", ["feature", "testing"])

// Capture specific commands/outputs
capture_command("npm run build", "/path/to/project")
capture_output("Build successful!", "output")

// Stop capture session
stop_capture("session_id")
```

### Advanced Search

```typescript
// Semantic search (requires vector DB)
// The MCP server will automatically use vector search when available
search_history({
  query: "how to fix typescript error",
  output_type: "error",
  limit: 20
})

// Find similar errors
get_errors({
  with_solutions: true,
  hours_ago: 168  // Last week
})
```

## Integration Methods

### Method 1: Named Pipe (Automatic Capture)

1. Start the pipe capture:
```bash
python3 scripts/coding_history_capture.py pipe start
```

2. Send outputs to the pipe from any tool:
```bash
echo "[CMD] npm install" > /tmp/coding_history_pipe
echo "[OUT] Success!" > /tmp/coding_history_pipe
echo "[ERR] Error occurred" > /tmp/coding_history_pipe
```

### Method 2: Shell Wrapper (Bash Integration)

1. Create wrapper:
```bash
python3 scripts/coding_history_capture.py wrapper
```

2. Add to `.bashrc` or `.zshrc`:
```bash
source ~/coding_history_wrapper.sh
```

3. Optionally alias commands:
```bash
alias npm="coding_history_exec npm"
alias python="coding_history_exec python"
alias git="coding_history_exec git"
```

### Method 3: Direct Execution

Wrap any command:
```bash
python3 scripts/coding_history_capture.py exec "npm run build"
```

## MCP Tools Available

| Tool | Description | Example |
|------|-------------|---------|
| `search_history` | Search coding history | Find all npm errors |
| `get_session` | Get specific session details | Review a debugging session |
| `get_errors` | Find recent errors | Get TypeScript errors with fixes |
| `start_capture` | Start capture session | Begin recording for project |
| `stop_capture` | Stop capture session | End recording |
| `toggle_capture` | Enable/disable globally | Turn capture on/off |
| `get_capture_status` | Check current status | See if capture is active |
| `capture_command` | Manually capture command | Record specific command |
| `capture_output` | Manually capture output | Record specific output |
| `get_project_summary` | Project activity summary | Weekly coding stats |
| `configure_capture` | Update settings | Change what gets captured |

## Privacy & Security

### Automatic Filtering
The system automatically excludes patterns containing:
- Passwords
- API keys
- Secrets
- Tokens

### Project Exclusion
Exclude sensitive projects:
```json
{
  "excluded_projects": [
    "/path/to/sensitive/project"
  ]
}
```

### Manual Control
- Toggle capture on/off anytime
- Delete specific sessions or chunks
- Configure custom exclusion patterns

## Database Location

All data is stored locally:
```
data/coding_history/
├── sessions.db          # SQLite metadata
├── outputs/            # Compressed chunks
├── config/
│   └── settings.json   # Configuration
└── qdrant/            # Vector embeddings (optional)
```

## Troubleshooting

### Check if capture is working:
```bash
python3 scripts/coding_history_capture.py test
```

### View database stats:
```bash
sqlite3 data/coding_history/sessions.db "SELECT COUNT(*) FROM sessions;"
```

### Index vector database:
```bash
python3 scripts/coding_history_vector.py index
```

### Clear all history (reset):
```bash
rm -rf data/coding_history/*
```

## Benefits for Cursor Users

1. **Never Lose Solutions**: Every fix you've found is searchable
2. **Learn from Errors**: Find how you solved similar issues before
3. **Project Context**: Cursor can understand your project's history
4. **Team Knowledge**: Share coding history across team (optional)
5. **Progress Tracking**: See how projects evolve over time
6. **Debugging Aid**: Full context of what led to errors

## Example Workflow

1. **Start your day**: Cursor automatically has context from previous sessions
2. **Hit an error**: Search for similar errors and their solutions
3. **Try different approaches**: All attempts are recorded
4. **Find what worked**: Review successful commands and outputs
5. **Share knowledge**: Export sessions for team learning

## Performance Considerations

- Compression reduces storage by ~70%
- SQLite indexes provide fast searches
- Vector embeddings cached for semantic search
- Async processing doesn't block terminal
- Configurable chunk sizes for optimization

## Future Enhancements

- [ ] Web UI for browsing history
- [ ] Export/import sessions
- [ ] Team sharing capabilities
- [ ] AI-powered pattern recognition
- [ ] Automated documentation generation
- [ ] Integration with git commits

---

For issues or questions, check the logs:
```bash
tail -f data/coding_history/capture.log
```

Remember: This system is designed to be your "external brain" for coding, making every solution you've ever found instantly accessible!