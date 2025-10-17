#!/usr/bin/env python3
"""
Permanent fix for Claude Desktop shell snapshot PATH escaping bug.
Watches ~/.claude/shell-snapshots/ and auto-fixes any broken snapshots.
"""

import os
import time
import re
import shutil
from pathlib import Path
from datetime import datetime

SNAPSHOT_DIR = Path.home() / ".claude" / "shell-snapshots"
TEMPLATE_FILE = SNAPSHOT_DIR / "snapshot-zsh-template.sh"
LOG_FILE = Path.home() / "AI-Workspace" / "snapshot_watcher.log"

# Clean template content
CLEAN_TEMPLATE = """#!/bin/zsh
# Clean snapshot - Auto-fixed by snapshot_watcher.py
# This file provides a working shell environment for Claude Desktop

# Unset all aliases to avoid conflicts
unalias -a 2>/dev/null || true

# Shell Options
setopt nohashdirs
setopt login

# Environment Variables
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Clean PATH without escaped colons
export PATH=/opt/homebrew/bin:/opt/homebrew/sbin:/Library/Frameworks/Python.framework/Versions/3.11/bin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/Users/yourox/.local/bin

# Common aliases
alias ws='cd /Users/yourox/AI-Workspace'
alias py='python3'
alias python='python3'

# Check for ripgrep availability
if ! command -v rg >/dev/null 2>&1; then
  alias rg='/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/vendor/ripgrep/arm64-darwin/rg'
fi

# Set working directory
cd /Users/yourox/AI-Workspace
"""

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)

    # Append to log file
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")

    # Keep log file manageable (last 500 lines)
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 50000:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        with open(LOG_FILE, "w") as f:
            f.writelines(lines[-500:])

def is_broken(snapshot_file):
    """Check if snapshot has escaped colons in PATH"""
    try:
        with open(snapshot_file, "r") as f:
            content = f.read()
        # Check for escaped colons in export PATH
        return bool(re.search(r'export PATH=.*\\:', content))
    except Exception as e:
        log(f"Error checking {snapshot_file.name}: {e}")
        return False

def fix_snapshot(snapshot_file):
    """Fix a broken snapshot by replacing with clean template"""
    try:
        # Create backup
        backup_file = snapshot_file.with_suffix(".sh.broken")
        shutil.copy2(snapshot_file, backup_file)

        # Replace with clean template
        with open(snapshot_file, "w") as f:
            f.write(CLEAN_TEMPLATE)

        log(f"✅ Fixed: {snapshot_file.name}")
        return True
    except Exception as e:
        log(f"❌ Error fixing {snapshot_file.name}: {e}")
        return False

def ensure_template_exists():
    """Ensure clean template exists"""
    if not TEMPLATE_FILE.exists():
        with open(TEMPLATE_FILE, "w") as f:
            f.write(CLEAN_TEMPLATE)
        log(f"Created template: {TEMPLATE_FILE}")

def scan_and_fix():
    """Scan all snapshots and fix broken ones"""
    if not SNAPSHOT_DIR.exists():
        log(f"Snapshot directory not found: {SNAPSHOT_DIR}")
        return

    ensure_template_exists()

    fixed_count = 0
    for snapshot_file in SNAPSHOT_DIR.glob("snapshot-zsh-*.sh"):
        # Skip template and special files
        if snapshot_file.name in ["snapshot-zsh-template.sh", "snapshot-zsh-fixed.sh"]:
            continue

        if is_broken(snapshot_file):
            if fix_snapshot(snapshot_file):
                fixed_count += 1

    if fixed_count > 0:
        log(f"Fixed {fixed_count} broken snapshot(s)")

    return fixed_count

def watch_mode():
    """Watch directory and auto-fix broken snapshots"""
    log("🔍 Starting snapshot watcher...")
    log(f"Watching: {SNAPSHOT_DIR}")
    log("Press Ctrl+C to stop")

    # Initial scan
    scan_and_fix()

    # Track file modification times
    seen_files = {}

    try:
        while True:
            time.sleep(2)  # Check every 2 seconds

            for snapshot_file in SNAPSHOT_DIR.glob("snapshot-zsh-*.sh"):
                # Skip template and special files
                if snapshot_file.name in ["snapshot-zsh-template.sh", "snapshot-zsh-fixed.sh"]:
                    continue

                # Check if file is new or modified
                try:
                    mtime = snapshot_file.stat().st_mtime

                    if snapshot_file not in seen_files or seen_files[snapshot_file] != mtime:
                        seen_files[snapshot_file] = mtime

                        # Check if broken and fix
                        if is_broken(snapshot_file):
                            log(f"⚠️  Detected broken snapshot: {snapshot_file.name}")
                            fix_snapshot(snapshot_file)

                except Exception as e:
                    log(f"Error checking {snapshot_file.name}: {e}")

    except KeyboardInterrupt:
        log("🛑 Snapshot watcher stopped")

def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        watch_mode()
    else:
        # One-time scan and fix
        fixed = scan_and_fix()
        if fixed == 0:
            log("✅ All snapshots are clean")

if __name__ == "__main__":
    main()
