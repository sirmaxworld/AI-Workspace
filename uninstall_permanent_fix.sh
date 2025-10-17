#!/bin/bash
# Uninstall permanent shell snapshot fix

echo "🗑️  Uninstalling Shell Snapshot Watcher"
echo "========================================"
echo

# Unload the LaunchAgent
echo "Stopping background watcher..."
launchctl unload ~/Library/LaunchAgents/com.yourox.snapshot-watcher.plist 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Watcher stopped"
else
    echo "⚠️  Watcher was not running"
fi

# Remove the plist file
echo "Removing LaunchAgent..."
rm -f ~/Library/LaunchAgents/com.yourox.snapshot-watcher.plist

if [ $? -eq 0 ]; then
    echo "✅ LaunchAgent removed"
fi

echo
echo "=========================================="
echo "✅ Uninstall Complete!"
echo
echo "The watcher is no longer running."
echo "You can still manually fix snapshots with:"
echo "  python3 ~/AI-Workspace/snapshot_watcher.py"
echo