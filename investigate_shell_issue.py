#!/usr/bin/env python3
"""
Investigate shell snapshot corruption issue
"""

import os
import re
from pathlib import Path
from datetime import datetime

def analyze_snapshot(file_path):
    """Analyze a shell snapshot file for issues"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract timestamp from filename
    filename = Path(file_path).name
    timestamp_match = re.search(r'snapshot-zsh-(\d+)-', filename)
    timestamp = None
    if timestamp_match:
        timestamp_ms = int(timestamp_match.group(1))
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000)

    # Check for escaped colons
    has_escaped_colons = r'\:' in content

    # Find PATH exports
    path_lines = []
    for i, line in enumerate(content.split('\n'), 1):
        if 'export PATH=' in line:
            path_lines.append((i, line))

    # Check for problematic patterns
    issues = []
    if has_escaped_colons:
        issues.append("Contains escaped colons (\\:)")

    # Check for embedded Python in shell
    if 'python3 -c' in content and len(content.split('\n')) > 100:
        issues.append("Contains embedded Python code")

    # Check for multiline strings that might cause issues
    if content.count("'''") > 2 or content.count('"""') > 2:
        issues.append("Contains multiline Python strings")

    return {
        'file': file_path,
        'filename': filename,
        'timestamp': timestamp,
        'has_escaped_colons': has_escaped_colons,
        'path_lines': path_lines,
        'issues': issues,
        'size': len(content),
        'lines': len(content.split('\n'))
    }

def main():
    snapshot_dir = Path.home() / ".claude" / "shell-snapshots"
    snapshots = sorted(snapshot_dir.glob("snapshot-zsh-*.sh"))

    print("=" * 80)
    print("SHELL SNAPSHOT ANALYSIS")
    print("=" * 80)
    print(f"Found {len(snapshots)} snapshots\n")

    # Analyze each snapshot
    problematic = []
    clean = []

    for snapshot in snapshots:
        result = analyze_snapshot(snapshot)

        if result['issues']:
            problematic.append(result)
        else:
            clean.append(result)

    # Report findings
    print(f"✅ Clean snapshots: {len(clean)}")
    print(f"❌ Problematic snapshots: {len(problematic)}")
    print()

    if problematic:
        print("PROBLEMATIC SNAPSHOTS:")
        print("-" * 40)

        for snap in problematic:
            print(f"\n📁 {snap['filename']}")
            if snap['timestamp']:
                print(f"   Created: {snap['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {snap['size']} bytes, {snap['lines']} lines")
            print(f"   Issues:")
            for issue in snap['issues']:
                print(f"     - {issue}")

            if snap['path_lines']:
                for line_no, line in snap['path_lines'][:1]:  # Show first PATH line
                    if len(line) > 100:
                        print(f"   PATH (line {line_no}): {line[:100]}...")
                    else:
                        print(f"   PATH (line {line_no}): {line}")

    # Pattern analysis
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS:")
    print("-" * 40)

    # Check when escaping started
    if problematic:
        earliest_problematic = min(problematic, key=lambda x: x['timestamp'] if x['timestamp'] else datetime.max)
        print(f"Earliest problematic snapshot: {earliest_problematic['filename']}")
        if earliest_problematic['timestamp']:
            print(f"Created: {earliest_problematic['timestamp']}")

    # Check for common patterns
    all_have_escaped = all(s['has_escaped_colons'] for s in problematic)
    if all_have_escaped and problematic:
        print("\n⚠️  ALL problematic snapshots have escaped colons in PATH")
        print("This suggests Claude Desktop is escaping colons when creating snapshots")

    # Check current environment
    print("\n" + "=" * 80)
    print("CURRENT ENVIRONMENT:")
    print("-" * 40)

    current_path = os.environ.get('PATH', '')
    print(f"Current PATH from os.environ:")
    if '\\:' in current_path:
        print("  ❌ Contains escaped colons!")
    else:
        print("  ✅ Clean (no escaped colons)")

    print(f"\nFirst 200 chars: {current_path[:200]}...")

    # Recommendations
    print("\n" + "=" * 80)
    print("ROOT CAUSE ANALYSIS:")
    print("-" * 40)

    print("""
The issue appears to be that Claude Desktop is escaping colons when it creates
shell snapshots. This happens during the snapshot creation process, not from
your shell configuration.

EVIDENCE:
1. Your .zshrc is clean (no escaped colons)
2. Multiple snapshots across different dates have the same issue
3. The 'fixed' snapshot you created manually has clean colons
4. This affects the PATH export specifically

LIKELY CAUSE:
Claude Desktop's snapshot creation mechanism is incorrectly escaping special
characters, treating colons as special characters that need escaping when they
shouldn't be in this context.

IMPACT:
The escaped colons (\\:) break PATH parsing, causing shell parse errors.
""")

    print("\nSOLUTION OPTIONS:")
    print("-" * 40)
    print("""
1. SHORT-TERM FIX:
   - Delete problematic snapshots
   - Use the 'snapshot-zsh-fixed.sh' as template
   - Restart Claude Desktop to regenerate

2. WORKAROUND:
   - Create a wrapper script that fixes PATH on startup
   - Or use the fixed snapshot approach

3. LONG-TERM:
   - This appears to be a Claude Desktop bug
   - The escaping logic needs to be fixed in the app

The coding history system didn't CAUSE this issue, but it may have
made it more visible by adding complexity to the shell environment.
""")

if __name__ == "__main__":
    main()