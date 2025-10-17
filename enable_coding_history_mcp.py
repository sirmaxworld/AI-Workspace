#!/usr/bin/env python3
"""
Enable Coding History MCP in Claude Desktop
Python version that works without shell
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    print("🔧 Enabling Coding History MCP Server in Claude Desktop")
    print("=" * 60)

    config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"

    if not config_path.exists():
        print("❌ Claude Desktop config not found")
        print(f"   Expected at: {config_path}")
        return 1

    # Backup current config
    backup_path = config_path.parent / f"claude_desktop_config.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    config_path.read_bytes()  # Read to ensure it exists
    with open(backup_path, 'wb') as f:
        f.write(config_path.read_bytes())
    print(f"✅ Backup created: {backup_path.name}")

    # Load config
    with open(config_path) as f:
        config = json.load(f)

    # Check if already configured
    if 'coding-history' in config.get('mcpServers', {}):
        print("✅ Coding history MCP is already configured")
    else:
        # Add coding-history server
        if 'mcpServers' not in config:
            config['mcpServers'] = {}

        config['mcpServers']['coding-history'] = {
            "command": "/usr/local/bin/python3.11",
            "args": ["/Users/yourox/AI-Workspace/mcp_servers/coding_history_summary_mcp.py"]
        }

        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print("✅ Configuration updated successfully")

    # Show current MCP servers
    print("\n📋 Current MCP Servers configured:")
    for server in config.get('mcpServers', {}).keys():
        print(f"  - {server}")

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Quit Claude Desktop completely (Cmd+Q)")
    print("2. Reopen Claude Desktop")
    print("3. Test with: 'Can you check my coding history?'")
    print("\nThe MCP server provides:")
    print("  - Session summaries (not raw output)")
    print("  - Error analysis")
    print("  - Productivity insights")
    print("  - Lightweight and fast queries")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())