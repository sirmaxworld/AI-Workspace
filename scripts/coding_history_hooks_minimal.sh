#!/bin/bash
# Minimal Coding History Shell Hooks - Safe version
# This version avoids complex embedded code that could trigger snapshot issues

# Only load if not already loaded
if [ -z "$CODING_HISTORY_LOADED" ]; then
    export CODING_HISTORY_LOADED=1

    # Configuration
    export CODING_HISTORY_ENABLED="${CODING_HISTORY_ENABLED:-1}"
    export CODING_HISTORY_PYTHON="/usr/local/bin/python3.11"

    # Simple aliases for coding history tools
    alias ch_stats="$CODING_HISTORY_PYTHON /Users/yourox/AI-Workspace/scripts/ch_stats_standalone.py 2>/dev/null"
    alias ch_details="$CODING_HISTORY_PYTHON /Users/yourox/AI-Workspace/scripts/ch_details.py 2>/dev/null"
    alias ch_monitor="$CODING_HISTORY_PYTHON /Users/yourox/AI-Workspace/scripts/coding_history_monitor.py 2>/dev/null"

    # Simple toggle function
    ch_toggle() {
        if [ "$1" = "on" ]; then
            export CODING_HISTORY_ENABLED=1
            echo "✅ Coding history capture enabled"
        elif [ "$1" = "off" ]; then
            export CODING_HISTORY_ENABLED=0
            echo "❌ Coding history capture disabled"
        else
            if [ "$CODING_HISTORY_ENABLED" = "1" ]; then
                export CODING_HISTORY_ENABLED=0
                echo "❌ Coding history capture disabled"
            else
                export CODING_HISTORY_ENABLED=1
                echo "✅ Coding history capture enabled"
            fi
        fi
    }

    alias ch_on="ch_toggle on"
    alias ch_off="ch_toggle off"

    # Silent load - no output to avoid cluttering shell
    # Users can run ch_toggle to see status
fi