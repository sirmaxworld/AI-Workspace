# Claude Memory MCP Server

## Installation

This MCP server requires Python 3.10+ and uses `uv` for dependency management.

### Quick Install to Claude Desktop

```bash
cd /Users/yourox/AI-Workspace/mcp_servers
uv run mcp install claude_memory_server.py --name "Claude Memory"
```

### Manual Installation

Add to Claude Desktop config at:
`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "claude-memory": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourox/AI-Workspace/mcp_servers",
        "run",
        "claude_memory_server.py"
      ]
    }
  }
}
```

## Features

- **Resource**: `memory://context` - Access persistent memories
- **Tool**: `save_memory(text, type)` - Save new memories
- **Tool**: `search_memories(query)` - Search past memories  
- **Tool**: `get_memory_stats()` - View memory statistics

## Testing

```bash
# Test with MCP Inspector
uv run mcp dev claude_memory_server.py

# Test loading memories
python3 -c "import json; print(len(json.load(open('../data/claude_memory_json/memories.json'))))"
```

## Troubleshooting

If you get "No module named 'mcp'":
```bash
uv add "mcp[cli]"
```

## Dependencies

Automatically managed by `uv`:
- mcp[cli]
- Python 3.10+
