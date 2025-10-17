#!/bin/bash
# Monitor YC Companies Phase 1 Enrichment Progress

echo "========================================================================"
echo "📊 YC COMPANIES ENRICHMENT - LIVE MONITOR"
echo "========================================================================"
echo ""

# Check if enrichment is running
if ps aux | grep "enrichment_coordinator.py phase1" | grep -v grep > /dev/null; then
    echo "✅ Status: RUNNING"
else
    echo "⏸️  Status: NOT RUNNING (may have completed or stopped)"
fi

echo ""

# Count total lines (rough progress indicator)
TOTAL_LINES=$(wc -l < /tmp/yc_phase1_enrichment.log 2>/dev/null || echo "0")
echo "📝 Total log lines: $TOTAL_LINES"

echo ""

# Count enriched files
ENRICHED_COUNT=$(ls -1 /Users/yourox/AI-Workspace/data/yc_enriched/*_enriched.json 2>/dev/null | wc -l | tr -d ' ')
echo "✅ Companies enriched: $ENRICHED_COUNT / 5,490"

if [ "$ENRICHED_COUNT" -gt 0 ]; then
    PROGRESS=$(echo "scale=1; ($ENRICHED_COUNT / 5490) * 100" | bc)
    echo "📈 Progress: $PROGRESS%"
fi

echo ""

# Show last 10 enriched companies
echo "🔄 Recently enriched:"
tail -20 /tmp/yc_phase1_enrichment.log 2>/dev/null | grep "Enriching" | tail -10

echo ""
echo "========================================================================"
echo "💡 Commands:"
echo "   Watch live: tail -f /tmp/yc_phase1_enrichment.log"
echo "   Check stats: cd /Users/yourox/AI-Workspace/scripts/enrichment/yc && python3 enrichment_coordinator.py stats"
echo "   Re-run monitor: bash monitor_enrichment.sh"
echo "========================================================================"
