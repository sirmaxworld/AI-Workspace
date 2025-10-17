#!/usr/bin/env python3
"""
Fix Claude Desktop shell snapshot PATH escaping issue
This script fixes the escaped colons in PATH exports in shell snapshots
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def fix_snapshot(file_path, backup=True):
    """Fix escaped colons in a shell snapshot file"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Check if file needs fixing
    if r'\:' not in content:
        return False, "No escaped colons found"

    # Create backup if requested
    if backup:
        backup_path = str(file_path) + '.backup'
        shutil.copy2(file_path, backup_path)

    # Fix escaped colons (but preserve other escapes like \@ for ripgrep)
    fixed_content = content.replace(r'\:', ':')

    # Write fixed content
    with open(file_path, 'w') as f:
        f.write(fixed_content)

    return True, "Fixed escaped colons in PATH"

def create_clean_snapshot():
    """Create a clean snapshot template that Claude can use"""
    snapshot_dir = Path.home() / ".claude" / "shell-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    template_path = snapshot_dir / "snapshot-zsh-template.sh"

    template_content = """#!/bin/zsh
# Clean snapshot template
# This file provides a working shell environment for Claude Desktop

# Unset all aliases to avoid conflicts
unalias -a 2>/dev/null || true

# Functions
# (Add any shell functions here if needed)

# Shell Options
setopt nohashdirs
setopt login

# Environment Variables
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Clean PATH without escaped colons
export PATH=/opt/homebrew/bin:/opt/homebrew/sbin:/Library/Frameworks/Python.framework/Versions/3.11/bin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/Users/yourox/.local/bin

# Aliases - Add your common aliases here
alias ws='cd /Users/yourox/AI-Workspace'
alias py='python3'
alias python='python3'

# Check for ripgrep availability
if ! command -v rg >/dev/null 2>&1; then
  alias rg='/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/vendor/ripgrep/arm64-darwin/rg'
fi

# Set working directory
cd /Users/yourox/AI-Workspace

# Source additional configurations if they exist
[ -f ~/.dictation_helpers ] && source ~/.dictation_helpers
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
"""

    with open(template_path, 'w') as f:
        f.write(template_content)

    return template_path

def main():
    print("=" * 80)
    print("CLAUDE DESKTOP SHELL SNAPSHOT FIXER")
    print("=" * 80)

    snapshot_dir = Path.home() / ".claude" / "shell-snapshots"

    # Find all problematic snapshots
    snapshots = list(snapshot_dir.glob("snapshot-zsh-*.sh"))
    print(f"\nFound {len(snapshots)} snapshots")

    # Fix each snapshot
    fixed_count = 0
    skip_count = 0
    errors = []

    print("\nFixing snapshots...")
    print("-" * 40)

    for snapshot in snapshots:
        try:
            # Skip the fixed and template files
            if 'fixed' in snapshot.name or 'template' in snapshot.name:
                print(f"⏭️  Skipping {snapshot.name} (special file)")
                continue

            fixed, message = fix_snapshot(snapshot)
            if fixed:
                print(f"✅ Fixed: {snapshot.name}")
                fixed_count += 1
            else:
                print(f"⏭️  Skip: {snapshot.name} - {message}")
                skip_count += 1

        except Exception as e:
            errors.append((snapshot.name, str(e)))
            print(f"❌ Error: {snapshot.name} - {e}")

    # Create clean template
    print("\nCreating clean template...")
    template_path = create_clean_snapshot()
    print(f"✅ Template created: {template_path}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("-" * 40)
    print(f"✅ Fixed: {fixed_count} snapshots")
    print(f"⏭️  Skipped: {skip_count} snapshots")
    if errors:
        print(f"❌ Errors: {len(errors)} snapshots")
        for name, error in errors:
            print(f"   - {name}: {error}")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("-" * 40)
    print("""
1. The snapshots have been fixed (backups created with .backup extension)
2. A clean template has been created for future use
3. You should now be able to use bash commands in Claude Desktop

To test:
1. Try a simple command in this session (may still fail due to caching)
2. For best results, restart Claude Desktop to use the fixed snapshots

If issues persist:
- Delete all snapshots: rm ~/.claude/shell-snapshots/snapshot-zsh-*.sh
- Keep only the template: cp ~/.claude/shell-snapshots/snapshot-zsh-template.sh ~/.claude/shell-snapshots/snapshot-zsh-fixed.sh
- Restart Claude Desktop
""")

    # Check if coding history can be safely re-enabled
    print("\n" + "=" * 80)
    print("CODING HISTORY SYSTEM STATUS:")
    print("-" * 40)

    print("""
The coding history system DIDN'T cause the PATH escaping issue.
The issue is with how Claude Desktop creates shell snapshots.

However, the coding history hooks may have made the snapshots more complex,
which could trigger edge cases in the snapshot creation.

RECOMMENDATION:
- The PATH issue is now fixed
- You can potentially re-enable coding history if desired
- But monitor for any new snapshot corruptions

To re-enable coding history (if desired):
1. Add to ~/.zshrc:
   source ~/AI-Workspace/archive/old_coding_history/coding_history_hooks_simple.sh

2. Or re-add the MCP server to Claude config

The simpler version (coding_history_hooks_simple.sh) is less likely to
cause issues as it doesn't have embedded Python code.
""")

if __name__ == "__main__":
    main()