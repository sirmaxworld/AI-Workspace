#!/usr/bin/env python3
"""
Health Check Script for Verifying System Recovery
This script tests various aspects of the system without relying on shell commands
"""

import os
import socket
import subprocess
import sys
import glob
import requests
from datetime import datetime
from pathlib import Path

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def check_shell_snapshots():
    """Check for problematic shell snapshot files"""
    print_section("Shell Snapshot Check")

    snapshot_dir = Path.home() / ".claude" / "shell-snapshots"
    problematic_patterns = [
        "snapshot-zsh-1760609*.sh",
        "snapshot-zsh-1760635*.sh"
    ]

    issues_found = []

    for pattern in problematic_patterns:
        full_pattern = snapshot_dir / pattern
        matches = glob.glob(str(full_pattern))
        if matches:
            for match in matches:
                print(f"  ❌ Found problematic snapshot: {match}")
                issues_found.append(match)

                # Check for escaped colons in the file
                try:
                    with open(match, 'r') as f:
                        content = f.read()
                        if '\\:' in content:
                            print(f"     └─ Contains escaped colons in PATH")
                except Exception as e:
                    print(f"     └─ Could not read file: {e}")

    if not issues_found:
        print("  ✅ No problematic shell snapshots found")
    else:
        print(f"\n  ⚠️  Found {len(issues_found)} problematic snapshots")
        print("  Recommended action: Delete these files from terminal:")
        for file in issues_found:
            print(f"    rm '{file}'")

    return len(issues_found) == 0

def check_server_status(port=7000):
    """Check if TubeDB server is running on specified port"""
    print_section(f"Server Status Check (Port {port})")

    # First check if port is in use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', port))
    sock.close()

    if result == 0:
        print(f"  ✅ Port {port} is open")

        # Try to make HTTP request
        try:
            response = requests.get(f'http://localhost:{port}', timeout=5)
            print(f"  ✅ Server responding with status: {response.status_code}")

            # Check if it's the TubeDB app
            if 'tubedb' in response.text.lower() or 'next' in response.headers.get('x-powered-by', '').lower():
                print(f"  ✅ Appears to be TubeDB/Next.js application")
            return True
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Port is open but HTTP request failed: {e}")
            return False
    else:
        print(f"  ❌ Port {port} is not open")
        print(f"  Recommended action: Start server with 'PORT={port} npm run dev'")
        return False

def check_node_npm():
    """Check Node.js and npm installation"""
    print_section("Node.js and npm Check")

    tools_ok = True

    # Check for node
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✅ Node.js installed: {result.stdout.strip()}")
        else:
            print("  ❌ Node.js check failed")
            tools_ok = False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Node.js not found or not responding")
        tools_ok = False

    # Check for npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✅ npm installed: {result.stdout.strip()}")
        else:
            print("  ❌ npm check failed")
            tools_ok = False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ npm not found or not responding")
        tools_ok = False

    return tools_ok

def check_tubedb_directory():
    """Check if TubeDB directory exists and has necessary files"""
    print_section("TubeDB Directory Check")

    tubedb_dir = Path.home() / "AI-Workspace" / "tubedb-ui"

    if not tubedb_dir.exists():
        print(f"  ❌ TubeDB directory not found: {tubedb_dir}")
        return False

    print(f"  ✅ TubeDB directory exists: {tubedb_dir}")

    # Check for important files
    important_files = [
        "package.json",
        "next.config.js",
        "node_modules"
    ]

    all_present = True
    for file in important_files:
        file_path = tubedb_dir / file
        if file_path.exists():
            print(f"  ✅ Found: {file}")
        else:
            print(f"  ❌ Missing: {file}")
            if file == "node_modules":
                print("     └─ Run 'npm install' in the tubedb-ui directory")
            all_present = False

    return all_present

def check_problematic_scripts():
    """Check for the problematic coding history scripts"""
    print_section("Problematic Scripts Check")

    scripts_dir = Path.home() / "AI-Workspace" / "scripts"
    problematic_files = [
        "coding_history_shell_hooks.sh",
        "coding_history_hooks_simple.sh",
        "coding_history_capture.py",
        "coding_history_capture_async.py"
    ]

    found_issues = []
    for file in problematic_files:
        file_path = scripts_dir / file
        if file_path.exists():
            print(f"  ⚠️  Found problematic script: {file}")
            found_issues.append(str(file_path))

    mcp_file = Path.home() / "AI-Workspace" / "mcp_servers" / "coding_history_mcp.py"
    if mcp_file.exists():
        print(f"  ⚠️  Found problematic MCP server: coding_history_mcp.py")
        found_issues.append(str(mcp_file))

    if not found_issues:
        print("  ✅ No problematic scripts found")
    else:
        print(f"\n  Recommended action: Archive or delete these files:")
        for file in found_issues:
            print(f"    mv '{file}' '{file}.disabled'")

    return len(found_issues) == 0

def main():
    """Run all health checks"""
    print("\n" + "="*60)
    print("  🆘 SYSTEM HEALTH CHECK")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)

    results = {
        "Shell Snapshots": check_shell_snapshots(),
        "Node/npm": check_node_npm(),
        "TubeDB Directory": check_tubedb_directory(),
        "Problematic Scripts": check_problematic_scripts(),
        "Server Status": check_server_status(7000)
    }

    # Also check alternative ports if main port fails
    if not results["Server Status"]:
        for port in [3000, 3001, 4000, 8000]:
            if check_server_status(port):
                results[f"Server on port {port}"] = True
                break

    # Summary
    print_section("SUMMARY")

    all_ok = all(results.values())

    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    print("\n" + "="*60)
    if all_ok:
        print("  ✅ ALL CHECKS PASSED - System is healthy!")
    else:
        print("  ⚠️  ISSUES DETECTED - Follow recommendations above")
        print("\n  Key actions needed:")
        if not results["Shell Snapshots"]:
            print("  1. Delete problematic shell snapshots from terminal")
            print("  2. Restart Claude Desktop after cleanup")
        if not results["Server Status"]:
            print("  3. Start TubeDB server: cd ~/AI-Workspace/tubedb-ui && PORT=7000 npm run dev")
    print("="*60 + "\n")

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())