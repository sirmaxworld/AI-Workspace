#!/bin/bash
# Auto-fix shell snapshots when they get corrupted
# Run this periodically or add to crontab

SNAPSHOT_DIR="$HOME/.claude/shell-snapshots"
LOG_FILE="$HOME/AI-Workspace/snapshot_fix.log"

echo "[$(date)] Starting auto-fix check..." >> "$LOG_FILE"

# Count snapshots with escaped colons
BROKEN_COUNT=$(grep -l 'export PATH=.*\\:' "$SNAPSHOT_DIR"/snapshot-zsh-*.sh 2>/dev/null | wc -l | tr -d ' ')

if [ "$BROKEN_COUNT" -gt 0 ]; then
    echo "[$(date)] Found $BROKEN_COUNT broken snapshots - fixing..." >> "$LOG_FILE"

    # Fix all broken snapshots
    for file in "$SNAPSHOT_DIR"/snapshot-zsh-*.sh; do
        if [ -f "$file" ]; then
            # Check if it has escaped colons
            if grep -q 'export PATH=.*\\:' "$file" 2>/dev/null; then
                echo "  Fixing: $(basename "$file")" >> "$LOG_FILE"
                # Use the clean template
                cp "$SNAPSHOT_DIR/snapshot-zsh-template.sh" "$file"
            fi
        fi
    done

    echo "[$(date)] ✅ Fixed $BROKEN_COUNT snapshots" >> "$LOG_FILE"
else
    echo "[$(date)] No broken snapshots found" >> "$LOG_FILE"
fi

# Cleanup old log (keep last 100 lines)
if [ -f "$LOG_FILE" ]; then
    tail -100 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi