#!/bin/bash
# Independent Coding History Hooks
# Works in ANY terminal (iTerm, Terminal, Cursor, etc.)
# NO dependency on Claude Desktop

# Only load once
if [ -n "$CODING_HISTORY_INDEPENDENT_LOADED" ]; then
    return 0
fi
export CODING_HISTORY_INDEPENDENT_LOADED=1

# Configuration
export CODING_HISTORY_ENABLED="${CODING_HISTORY_ENABLED:-1}"
export CODING_HISTORY_QUEUE="$HOME/.coding_history_queue.txt"
export CODING_HISTORY_PROCESSOR="$HOME/AI-Workspace/scripts/process_history_queue.py"

# Capture command before execution (preexec hook)
preexec() {
    if [ "$CODING_HISTORY_ENABLED" != "1" ]; then
        return 0
    fi

    # Queue command asynchronously (non-blocking)
    # Use >> for append, run in background
    echo "$1" >> "$CODING_HISTORY_QUEUE" 2>/dev/null &
}

# Process queue periodically in background
_start_history_processor() {
    if [ "$CODING_HISTORY_ENABLED" != "1" ]; then
        return 0
    fi

    # Start background processor (every 10 seconds)
    (
        while sleep 10; do
            if [ -f "$CODING_HISTORY_QUEUE" ]; then
                /usr/bin/python3 "$CODING_HISTORY_PROCESSOR" >/dev/null 2>&1 &
            fi
        done
    ) &

    # Save PID for cleanup
    export CODING_HISTORY_BG_PID=$!

    # Kill background process on shell exit
    trap "kill $CODING_HISTORY_BG_PID 2>/dev/null" EXIT
}

# Control functions
ch_on() {
    export CODING_HISTORY_ENABLED=1
    _start_history_processor
    echo "✅ Coding history capture enabled (independent mode)"
}

ch_off() {
    export CODING_HISTORY_ENABLED=0
    if [ -n "$CODING_HISTORY_BG_PID" ]; then
        kill $CODING_HISTORY_BG_PID 2>/dev/null
    fi
    echo "❌ Coding history capture disabled"
}

ch_status() {
    if [ "$CODING_HISTORY_ENABLED" = "1" ]; then
        echo "✅ Coding history: ENABLED"
        if [ -n "$CODING_HISTORY_BG_PID" ] && kill -0 $CODING_HISTORY_BG_PID 2>/dev/null; then
            echo "   Background processor: RUNNING (PID $CODING_HISTORY_BG_PID)"
        else
            echo "   Background processor: NOT RUNNING"
        fi

        if [ -f "$CODING_HISTORY_QUEUE" ]; then
            local count=$(wc -l < "$CODING_HISTORY_QUEUE" 2>/dev/null || echo 0)
            echo "   Queued commands: $count"
        else
            echo "   Queued commands: 0"
        fi
    else
        echo "❌ Coding history: DISABLED"
    fi
}

ch_flush() {
    echo "Flushing queue..."
    /usr/bin/python3 "$CODING_HISTORY_PROCESSOR"
    echo "✅ Queue processed"
}

# Start processor on load
_start_history_processor

# Friendly message
if [ "$CODING_HISTORY_ENABLED" = "1" ]; then
    echo "📝 Coding history capture active (independent mode)"
    echo "   Controls: ch_on | ch_off | ch_status | ch_flush"
fi