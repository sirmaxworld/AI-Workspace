#!/bin/bash
# Monitor batch extraction progress

LOG_FILE="/tmp/batch_extraction.log"

while true; do
    clear
    echo "================================================================================"
    echo "📊 BATCH EXTRACTION PROGRESS"
    echo "================================================================================"
    echo ""

    if [ -f "$LOG_FILE" ]; then
        # Count progress indicators
        total=$(grep -c "Processing:" "$LOG_FILE" 2>/dev/null || echo "0")
        transcripts=$(grep -c "✅ Transcript extracted" "$LOG_FILE" 2>/dev/null || echo "0")
        insights=$(grep -c "✅ Business intelligence extracted" "$LOG_FILE" 2>/dev/null || echo "0")
        failed=$(grep -c "❌" "$LOG_FILE" 2>/dev/null || echo "0")

        echo "Videos processed: $total"
        echo "Transcripts: $transcripts"
        echo "Insights: $insights"
        echo "Failed: $failed"
        echo ""

        # Show last few lines
        echo "Recent activity:"
        echo "----------------------------------------"
        tail -10 "$LOG_FILE"
    else
        echo "Waiting for batch extraction to start..."
    fi

    echo ""
    echo "================================================================================"
    echo "Press Ctrl+C to stop monitoring (extraction continues in background)"

    sleep 5
done
