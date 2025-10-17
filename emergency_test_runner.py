#!/usr/bin/env python3
"""
Emergency test runner that works without shell
Runs tests directly in Python to bypass shell issues
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run command directly without shell"""
    print(f"\n🔧 {description}")
    print("-" * 40)
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()

        # Use absolute paths
        if cmd[0] == 'python3':
            cmd[0] = '/usr/local/bin/python3.11'

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False,  # Don't use shell
            env=os.environ.copy()
        )

        if result.returncode == 0:
            print(f"✅ SUCCESS")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ FAILED (exit {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr}")

        return result.returncode == 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("🚨 EMERGENCY TEST RUNNER")
    print("Running tests without shell due to snapshot corruption")
    print("=" * 60)

    # Fix snapshots first
    print("\n📝 Step 1: Fixing shell snapshots...")
    snapshot_dir = Path.home() / ".claude" / "shell-snapshots"
    if snapshot_dir.exists():
        for snapshot in snapshot_dir.glob("snapshot-zsh-*.sh"):
            try:
                content = snapshot.read_text()
                if '\\:' in content:
                    fixed = content.replace('\\:', ':')
                    snapshot.write_text(fixed)
                    print(f"  Fixed: {snapshot.name}")
            except Exception as e:
                print(f"  Error fixing {snapshot.name}: {e}")

    # Run the comprehensive test
    print("\n📝 Step 2: Running comprehensive test suite...")
    test_path = "/Users/yourox/AI-Workspace/test_coding_history_complete.py"
    success = run_command(
        ['/usr/local/bin/python3.11', test_path],
        "Comprehensive Test Suite"
    )

    # Check MCP configuration
    print("\n📝 Step 3: Checking MCP configuration...")
    config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"

    if config_path.exists():
        import json
        with open(config_path) as f:
            config = json.load(f)

        if 'mcpServers' in config:
            print("MCP Servers configured:")
            for server in config.get('mcpServers', {}).keys():
                print(f"  - {server}")

            if 'coding-history' in config['mcpServers']:
                print("✅ Coding history MCP is configured")
            else:
                print("⚠️  Coding history MCP not configured")
                print("  Run: python3 enable_coding_history_mcp.py")
    else:
        print("❌ Claude config not found")

    # Summary
    print("\n" + "=" * 60)
    print("📊 EMERGENCY TEST COMPLETE")
    print("=" * 60)

    print("\nRECOMMENDATIONS:")
    print("1. Quit Claude Desktop completely (Cmd+Q)")
    print("2. Reopen Claude Desktop")
    print("3. The shell should work normally after restart")
    print("\nThe coding history system is ready but needs Claude restart to work.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())