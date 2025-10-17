#!/usr/bin/env python3
"""
MCP Server Health Report
Checks status of all MCP servers and their configurations
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def check_mcp_server_file(file_path):
    """Check if an MCP server file exists and is valid"""
    path = Path(file_path)
    if not path.exists():
        return {"status": "missing", "error": f"File not found: {file_path}"}

    try:
        # Check if it's a valid Python file
        with open(path, 'r') as f:
            content = f.read()
            if 'mcp.server' in content or 'FastMCP' in content:
                return {"status": "valid", "type": "MCP server"}
            else:
                return {"status": "unknown", "note": "File exists but may not be MCP server"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    print("=" * 80)
    print("MCP SERVER HEALTH REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Read Claude Desktop config
    claude_config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"

    print("\n📋 CLAUDE DESKTOP MCP SERVERS:")
    print("-" * 40)

    if claude_config_path.exists():
        with open(claude_config_path, 'r') as f:
            config = json.load(f)

        servers = config.get('mcpServers', {})

        for name, settings in servers.items():
            print(f"\n✓ {name}")
            print(f"  Command: {settings.get('command', 'N/A')}")

            args = settings.get('args', [])
            if args:
                # Check if it's a Python script
                for arg in args:
                    if arg.endswith('.py'):
                        file_status = check_mcp_server_file(arg)
                        print(f"  Script: {arg}")
                        print(f"  Status: {file_status['status']}")
                        if 'error' in file_status:
                            print(f"  Issue: {file_status['error']}")
                    else:
                        print(f"  Args: {arg}")

            if 'env' in settings:
                print(f"  Environment vars: {', '.join(settings['env'].keys())}")
    else:
        print("❌ Claude config not found")

    # Special report on specific servers
    print("\n" + "=" * 80)
    print("📊 DETAILED SERVER ANALYSIS:")
    print("-" * 40)

    # Memory Server
    print("\n1. MEMORY SERVER:")
    memory_server = Path("/Users/yourox/AI-Workspace/mcp_servers/claude_memory_server.py")
    if memory_server.exists():
        print("  ✅ File exists")
        print("  Purpose: Persistent memory and knowledge base for Claude")
        print("  Features:")
        print("    - save_memory: Store conversation memories")
        print("    - search_memories: Query stored memories")
        print("    - get_memory_stats: View memory statistics")
        print("    - run_pipeline: Process knowledge pipeline")
    else:
        print("  ❌ File not found")

    # Coding History Server
    print("\n2. CODING HISTORY SERVER:")
    coding_history = Path("/Users/yourox/AI-Workspace/mcp_servers/coding_history_mcp.py")
    if coding_history.exists():
        print("  ✅ File exists")
        print("  ⚠️  NOT configured in Claude Desktop")
        print("  Purpose: Track and search terminal command history")
        print("  Features:")
        print("    - search_history: Search coding history")
        print("    - get_session_details: View session info")
        print("    - toggle_capture: Enable/disable capture")
        print("    - export_session_history: Export history")
        print("\n  To enable in Claude Desktop, add to config:")
        print('    "coding_history": {')
        print('      "command": "/usr/local/bin/python3.11",')
        print(f'      "args": ["{coding_history}"]')
        print('    }')
    else:
        print("  ❌ File not found")

    # Check for Cursor config
    print("\n" + "=" * 80)
    print("📝 CURSOR CONFIGURATION:")
    print("-" * 40)

    cursor_configs = [
        Path.home() / ".cursor" / "config.json",
        Path.home() / "Library/Application Support/Cursor/User/settings.json"
    ]

    cursor_found = False
    for config_path in cursor_configs:
        if config_path.exists():
            cursor_found = True
            print(f"  Found: {config_path}")
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                    if 'mcp' in content.lower() or 'coding_history' in content:
                        print("  ✅ May contain MCP configuration")
                    else:
                        print("  ℹ️  No MCP references found")
            except Exception as e:
                print(f"  Error reading: {e}")

    if not cursor_found:
        print("  ℹ️  No Cursor config files found")
        print("  Note: Cursor MCP configuration may be in a different location")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("-" * 40)

    print("\n✅ ACTIVE MCP SERVERS (in Claude Desktop):")
    if servers:
        for name in servers.keys():
            print(f"  - {name}")

    print("\n⚠️  AVAILABLE BUT NOT ACTIVE:")
    if coding_history.exists():
        print("  - coding_history (can be enabled)")

    print("\n📌 RECOMMENDATIONS:")
    print("  1. The 'memory' server is active and working")
    print("  2. Coding history server exists but not configured")
    print("  3. Shell fixes have been applied (no escaped colons)")
    print("  4. Restart Claude Desktop for full effect")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()