#!/bin/bash
#
# System Status Check
# Quick overview of the entire BI system
#

echo ""
echo "================================================================================"
echo "🎯 AI BUSINESS INTELLIGENCE SYSTEM STATUS"
echo "================================================================================"
echo ""

# Database Stats
echo "📊 DATABASE:"
transcripts=$(ls /Users/yourox/AI-Workspace/data/transcripts/*_full.json 2>/dev/null | wc -l)
insights=$(ls /Users/yourox/AI-Workspace/data/business_insights/*_insights.json 2>/dev/null | wc -l)
echo "  Transcripts: $transcripts"
echo "  Insights: $insights"
echo ""

# Schema Status
echo "🔧 SCHEMA:"
cd /Users/yourox/AI-Workspace/mcp-servers/business-intelligence
schema_version=$(python3 -c "from schema import SCHEMA_VERSION; print(SCHEMA_VERSION)" 2>/dev/null || echo "Unknown")
echo "  Version: $schema_version"
echo "  Status: $(python3 schema_sync.py --validate 2>&1 | grep "✅ Valid:" || echo "Unknown")"
echo ""

# MCP Server
echo "🌐 MCP SERVER:"
if [ -f "server.py" ]; then
    echo "  Status: Installed ✅"
    echo "  Tools: 13"
    python3 -c "
from server import BusinessIntelligenceDB
db = BusinessIntelligenceDB()
stats = db.get_stats()
print(f'  Database items: {sum([v for k,v in stats.items() if k.startswith(\"total_\") and k != \"total_files\")])}')
" 2>/dev/null || echo "  Database: Not loaded"
else
    echo "  Status: Not found ❌"
fi
echo ""

# Rate Limiting Test
echo "🔥 RATE LIMITING:"
if [ -f "/Users/yourox/AI-Workspace/data/rate_limiting_test_results.json" ]; then
    python3 -c "
import json
with open('/Users/yourox/AI-Workspace/data/rate_limiting_test_results.json') as f:
    results = json.load(f)
print(f'  Last test: {results.get(\"test_date\", \"Unknown\")}')
print(f'  Success rate: {results.get(\"success_rate\", 0):.0f}%')
print(f'  Status: {\"✅ WORKING\" if results.get(\"success_rate\", 0) >= 80 else \"❌ NEEDS FIX\"}')" 2>/dev/null
else
    echo "  Status: Not tested yet ⏳"
fi
echo ""

# Documentation
echo "📚 DOCUMENTATION:"
docs_count=$(ls /Users/yourox/AI-Workspace/docs/*.md 2>/dev/null | wc -l)
echo "  Files: $docs_count"
echo "  Main: README.md"
echo ""

echo "================================================================================"
echo "✅ System Overview Complete"
echo "================================================================================"
echo ""
echo "Quick Commands:"
echo "  Test rate limiting:  python3 scripts/test_rate_limiting.py 3"
echo "  Validate schema:     cd mcp-servers/business-intelligence && python3 schema_sync.py --full-sync"
echo "  Test MCP server:     cd mcp-servers/business-intelligence && python3 test_server.py"
echo "  Extract video:       python3 scripts/batch_extract_videos.py VIDEO_ID"
echo ""
