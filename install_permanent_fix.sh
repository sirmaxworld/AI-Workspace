#!/bin/bash
# Install permanent fix for Claude Desktop shell snapshot bug
# This runs a background watcher that auto-fixes snapshots as they're created

echo "🔧 Installing Permanent Shell Snapshot Fix"
echo "=========================================="
echo

# Fix all current snapshots
echo "1. Fixing existing snapshots..."
python3 /Users/yourox/AI-Workspace/snapshot_watcher.py
echo

# Load the LaunchAgent
echo "2. Installing background watcher..."
launchctl unload ~/Library/LaunchAgents/com.yourox.snapshot-watcher.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.yourox.snapshot-watcher.plist

if [ $? -eq 0 ]; then
    echo "✅ Background watcher installed successfully!"
else
    echo "❌ Failed to install background watcher"
    exit 1
fi

echo

# Check if it's running
echo "3. Verifying watcher is running..."
sleep 2
if ps aux | grep -q "[s]napshot_watcher.py"; then
    echo "✅ Watcher is running!"
    PID=$(ps aux | grep "[s]napshot_watcher.py" | awk '{print $2}')
    echo "   Process ID: $PID"
else
    echo "⚠️  Watcher may not be running yet (give it a few seconds)"
fi

echo
echo "=========================================="
echo "✅ Installation Complete!"
echo
echo "The watcher will now:"
echo "  • Run automatically at login"
echo "  • Monitor ~/.claude/shell-snapshots/"
echo "  • Auto-fix broken snapshots instantly"
echo "  • Log activity to ~/AI-Workspace/snapshot_watcher.log"
echo
echo "To check status:"
echo "  ps aux | grep snapshot_watcher"
echo
echo "To view logs:"
echo "  tail -f ~/AI-Workspace/snapshot_watcher.log"
echo
echo "To uninstall:"
echo "  bash ~/AI-Workspace/uninstall_permanent_fix.sh"
echo