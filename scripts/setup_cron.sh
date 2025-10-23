#!/bin/bash
# Setup Cron Jobs for Automated Content Pipeline

WORKSPACE="/Users/yourox/AI-Workspace"

echo "🔧 Setting up automated content pipeline cron jobs..."
echo ""

# Check if cron is available
if ! command -v crontab &> /dev/null; then
    echo "❌ crontab not found. Using launchd for macOS instead."
    echo ""

    # Create launchd plist for daily collection
    PLIST_DAILY="$HOME/Library/LaunchAgents/com.ai-workspace.daily-pipeline.plist"

    cat > "$PLIST_DAILY" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai-workspace.daily-pipeline</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>python3</string>
        <string>/Users/yourox/AI-Workspace/scripts/automated_content_pipeline.py</string>
        <string>--mode</string>
        <string>daily</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/yourox/AI-Workspace/logs/daily-pipeline.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/yourox/AI-Workspace/logs/daily-pipeline-error.log</string>

    <key>WorkingDirectory</key>
    <string>/Users/yourox/AI-Workspace</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

    # Create launchd plist for weekly collection
    PLIST_WEEKLY="$HOME/Library/LaunchAgents/com.ai-workspace.weekly-pipeline.plist"

    cat > "$PLIST_WEEKLY" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai-workspace.weekly-pipeline</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>python3</string>
        <string>/Users/yourox/AI-Workspace/scripts/automated_content_pipeline.py</string>
        <string>--mode</string>
        <string>weekly</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/yourox/AI-Workspace/logs/weekly-pipeline.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/yourox/AI-Workspace/logs/weekly-pipeline-error.log</string>

    <key>WorkingDirectory</key>
    <string>/Users/yourox/AI-Workspace</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

    echo "✅ Created launchd plists:"
    echo "   Daily: $PLIST_DAILY"
    echo "   Weekly: $PLIST_WEEKLY"
    echo ""

    # Load the agents
    echo "Loading launchd agents..."
    launchctl unload "$PLIST_DAILY" 2>/dev/null
    launchctl unload "$PLIST_WEEKLY" 2>/dev/null
    launchctl load "$PLIST_DAILY"
    launchctl load "$PLIST_WEEKLY"

    echo ""
    echo "✅ Agents loaded!"
    echo ""
    echo "To verify:"
    echo "  launchctl list | grep ai-workspace"
    echo ""
    echo "To manually trigger:"
    echo "  launchctl start com.ai-workspace.daily-pipeline"
    echo "  launchctl start com.ai-workspace.weekly-pipeline"
    echo ""
    echo "To disable:"
    echo "  launchctl unload $PLIST_DAILY"
    echo "  launchctl unload $PLIST_WEEKLY"

else
    # Standard cron setup
    echo "Setting up crontab entries..."

    # Backup existing crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null

    # Add new entries (if not already present)
    (crontab -l 2>/dev/null; echo "# AI-Workspace Automated Content Pipeline") | crontab -
    (crontab -l 2>/dev/null; echo "0 8 * * * cd $WORKSPACE && python3 scripts/automated_content_pipeline.py --mode daily >> logs/cron.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 2 * * 0 cd $WORKSPACE && python3 scripts/automated_content_pipeline.py --mode weekly >> logs/cron.log 2>&1") | crontab -

    echo "✅ Cron jobs added:"
    echo "   Daily: 8:00 AM every day"
    echo "   Weekly: 2:00 AM every Sunday"
    echo ""
    echo "Current crontab:"
    crontab -l | grep -A 2 "AI-Workspace"
fi

echo ""
echo "📋 Next steps:"
echo "   1. Check logs directory: $WORKSPACE/logs/"
echo "   2. Test pipeline: python3 scripts/automated_content_pipeline.py --mode daily"
echo "   3. Monitor first scheduled run"
echo ""
echo "✅ Setup complete!"
