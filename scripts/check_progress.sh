#!/bin/bash
# Progress Monitor - Check collection status

echo "================================================================================"
echo "                      COLLECTION PROGRESS STATUS"
echo "================================================================================"
echo ""
echo "⏰ Current Time: $(date)"
echo ""

# Check running processes
GITHUB_RUNNING=$(ps aux | grep "github_repo_collector.py" | grep -v grep | wc -l)
OSS_RUNNING=$(ps aux | grep "oss_repo_collector.py" | grep -v grep | wc -l)
PATTERN_RUNNING=$(ps aux | grep "github_pattern_extractor.py" | grep -v grep | wc -l)

echo "🔄 Running Processes:"
[ $GITHUB_RUNNING -gt 0 ] && echo "  ✅ GitHub collector (active)" || echo "  ⏸️  GitHub collector (not running)"
[ $OSS_RUNNING -gt 0 ] && echo "  ✅ OSS collector (active)" || echo "  ⏸️  OSS collector (not running)"
[ $PATTERN_RUNNING -gt 0 ] && echo "  ✅ Pattern extractor (active)" || echo "  ⏸️  Pattern extractor (not running)"
echo ""

# Show log tail
echo "📊 Latest GitHub Log:"
tail -5 /tmp/intelligence_logs/github.log 2>/dev/null || echo "  No log yet"
echo ""

echo "📊 Latest OSS Log:"
tail -5 /tmp/intelligence_logs/oss.log 2>/dev/null || echo "  No log yet"
echo ""

# Database stats
echo "📊 Current Database Stats:"
python3 -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv('/Users/yourox/AI-Workspace/.env')

try:
    conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM github_repositories')
    print(f'   GitHub Repos: {cursor.fetchone()[0]:,}')

    cursor.execute('SELECT COUNT(*) FROM coding_patterns')
    print(f'   Patterns: {cursor.fetchone()[0]:,}')

    cursor.execute('SELECT COUNT(*) FROM coding_rules')
    print(f'   Rules: {cursor.fetchone()[0]:,}')

    cursor.execute('SELECT COUNT(*) FROM oss_commercial_repos')
    print(f'   OSS Repos: {cursor.fetchone()[0]:,}')

    cursor.close()
    conn.close()
except Exception as e:
    print(f'   Error: {e}')
"

echo ""
echo "================================================================================"
echo "💡 Tips:"
echo "   • Watch GitHub progress: tail -f /tmp/intelligence_logs/github.log"
echo "   • Watch OSS progress:    tail -f /tmp/intelligence_logs/oss.log"
echo "   • Check again:           bash scripts/check_progress.sh"
echo "================================================================================"
