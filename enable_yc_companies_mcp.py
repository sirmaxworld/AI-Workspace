#!/usr/bin/env python3
"""
Enable YC Companies MCP in Claude Desktop
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    print("🔧 Enabling YC Companies MCP Server in Claude Desktop")
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
    if 'yc-companies' in config.get('mcpServers', {}):
        print("✅ YC Companies MCP is already configured")
    else:
        # Add yc-companies server
        if 'mcpServers' not in config:
            config['mcpServers'] = {}

        config['mcpServers']['yc-companies'] = {
            "command": "/usr/local/bin/python3.11",
            "args": ["/Users/yourox/AI-Workspace/mcp_servers/yc_companies_mcp.py"]
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
    print("1. Run the extractor to populate the database:")
    print("   python3 scripts/yc_companies_extractor.py --upload")
    print("2. Quit Claude Desktop completely (Cmd+Q)")
    print("3. Reopen Claude Desktop")
    print("4. Test with: 'Show me YC companies that are hiring in AI'")
    print("\nThe MCP server provides:")
    print("  - Search 5,490+ YC companies")
    print("  - Filter by batch, industry, status, hiring")
    print("  - Get company details by slug")
    print("  - Semantic search with natural language")
    print("  - Statistics and insights")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
