#!/usr/bin/env python3
"""
Check the status of the coding history system
Works without shell
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def check_database():
    """Check the coding history database"""
    db_path = Path("/Users/yourox/AI-Workspace/data/coding_history/summaries.db")

    if not db_path.exists():
        print("❌ Database does not exist")
        return False

    try:
        conn = sqlite3.connect(str(db_path))

        # Check tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor]
        print(f"✅ Database exists with tables: {', '.join(tables)}")

        # Get stats
        cursor = conn.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        print(f"  Total sessions: {session_count}")

        # Get recent sessions
        cursor = conn.execute("""
            SELECT timestamp, prompt, outcome
            FROM sessions
            ORDER BY timestamp DESC
            LIMIT 5
        """)

        recent = cursor.fetchall()
        if recent:
            print("\n📜 Recent sessions:")
            for ts, prompt, outcome in recent:
                timestamp = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
                print(f"  [{timestamp}] {prompt[:50]}...")
                print(f"    → {outcome}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_mcp_config():
    """Check MCP configuration"""
    config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"

    if not config_path.exists():
        print("❌ Claude config not found")
        return False

    with open(config_path) as f:
        config = json.load(f)

    servers = list(config.get('mcpServers', {}).keys())
    print(f"\n📡 MCP Servers configured: {', '.join(servers)}")

    if 'coding-history' in servers:
        print("✅ Coding history MCP is configured")
        return True
    else:
        print("⚠️  Coding history MCP NOT configured")
        print("  To enable: python3 /Users/yourox/AI-Workspace/enable_coding_history_mcp.py")
        return False

def check_scripts():
    """Check if all scripts exist"""
    print("\n📂 Checking scripts:")

    scripts = {
        "Summary system": "/Users/yourox/AI-Workspace/scripts/coding_history_summary.py",
        "MCP server": "/Users/yourox/AI-Workspace/mcp_servers/coding_history_summary_mcp.py",
        "Enable script": "/Users/yourox/AI-Workspace/enable_coding_history_mcp.sh",
        "Test suite": "/Users/yourox/AI-Workspace/test_coding_history_complete.py"
    }

    all_exist = True
    for name, path in scripts.items():
        if Path(path).exists():
            print(f"  ✅ {name}: exists")
        else:
            print(f"  ❌ {name}: missing")
            all_exist = False

    return all_exist

def main():
    print("=" * 60)
    print("🔍 CODING HISTORY SYSTEM STATUS CHECK")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    db_ok = check_database()
    mcp_ok = check_mcp_config()
    scripts_ok = check_scripts()

    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    if db_ok and scripts_ok:
        print("✅ Core system is ready")
    else:
        print("❌ Core system has issues")

    if mcp_ok:
        print("✅ MCP integration is configured")
    else:
        print("⚠️  MCP integration needs setup")

    print("\n📋 NEXT STEPS:")

    if not mcp_ok:
        print("1. Enable MCP in Claude Desktop:")
        print("   python3 /Users/yourox/AI-Workspace/enable_coding_history_mcp.py")
        print("   Then restart Claude Desktop")

    print("\n2. Due to shell corruption in this session:")
    print("   - Quit Claude Desktop (Cmd+Q)")
    print("   - Reopen Claude Desktop")
    print("   - Shell will work normally after restart")

    print("\n3. After restart, test with:")
    print("   'Can you check my coding history?'")

    return 0

if __name__ == "__main__":
    sys.exit(main())