#!/bin/bash
# Parallel Collection Script
# Runs GitHub and OSS collection in parallel for maximum speed

echo "================================================================================"
echo "                    PARALLEL INTELLIGENCE COLLECTION"
echo "================================================================================"
echo ""
echo "Starting parallel collection at $(date)"
echo ""

# Create log directory
mkdir -p /tmp/intelligence_logs

# Run GitHub and OSS collection in parallel
echo "🚀 Starting GitHub collection in background..."
python3 /Users/yourox/AI-Workspace/scripts/github_repo_collector.py > /tmp/intelligence_logs/github.log 2>&1 &
GITHUB_PID=$!

echo "🚀 Starting OSS collection in background..."
python3 /Users/yourox/AI-Workspace/scripts/oss_repo_collector.py > /tmp/intelligence_logs/oss.log 2>&1 &
OSS_PID=$!

echo ""
echo "📊 Collection processes running:"
echo "   GitHub (PID: $GITHUB_PID) - logs: /tmp/intelligence_logs/github.log"
echo "   OSS    (PID: $OSS_PID)    - logs: /tmp/intelligence_logs/oss.log"
echo ""
echo "💡 Tip: Run 'tail -f /tmp/intelligence_logs/github.log' to watch progress"
echo ""

# Wait for both to complete
echo "⏳ Waiting for GitHub collection..."
wait $GITHUB_PID
GITHUB_STATUS=$?

echo "⏳ Waiting for OSS collection..."
wait $OSS_PID
OSS_STATUS=$?

echo ""
echo "================================================================================"
if [ $GITHUB_STATUS -eq 0 ] && [ $OSS_STATUS -eq 0 ]; then
    echo "✅ Phase 1 Complete: Both collections finished successfully"
else
    echo "⚠️  Phase 1 had some issues (GitHub: $GITHUB_STATUS, OSS: $OSS_STATUS)"
fi
echo "================================================================================"
echo ""

# Phase 2: Pattern extraction (depends on GitHub collection)
if [ $GITHUB_STATUS -eq 0 ]; then
    echo "🚀 Starting pattern extraction..."
    python3 /Users/yourox/AI-Workspace/scripts/github_pattern_extractor.py | tee /tmp/intelligence_logs/patterns.log
    PATTERN_STATUS=$?
else
    echo "⏭️  Skipping pattern extraction (GitHub collection failed)"
    PATTERN_STATUS=1
fi

# Phase 3: Scoring (depends on OSS collection)
if [ $OSS_STATUS -eq 0 ]; then
    echo ""
    echo "🚀 Starting commercial scoring..."
    python3 /Users/yourox/AI-Workspace/scripts/oss_commercial_scorer.py | tee /tmp/intelligence_logs/scoring.log
    SCORING_STATUS=$?
else
    echo "⏭️  Skipping scoring (OSS collection failed)"
    SCORING_STATUS=1
fi

# Final summary
echo ""
echo "================================================================================"
echo "                           COLLECTION SUMMARY"
echo "================================================================================"
echo ""
echo "Phase 1 - Data Collection:"
[ $GITHUB_STATUS -eq 0 ] && echo "  ✅ GitHub repositories" || echo "  ❌ GitHub repositories"
[ $OSS_STATUS -eq 0 ] && echo "  ✅ OSS repositories" || echo "  ❌ OSS repositories"
echo ""
echo "Phase 2 - Enrichment:"
[ $PATTERN_STATUS -eq 0 ] && echo "  ✅ Pattern extraction" || echo "  ❌ Pattern extraction"
[ $SCORING_STATUS -eq 0 ] && echo "  ✅ Commercial scoring" || echo "  ❌ Commercial scoring"
echo ""
echo "Completed at $(date)"
echo ""
echo "📊 View logs:"
echo "   GitHub:   /tmp/intelligence_logs/github.log"
echo "   OSS:      /tmp/intelligence_logs/oss.log"
echo "   Patterns: /tmp/intelligence_logs/patterns.log"
echo "   Scoring:  /tmp/intelligence_logs/scoring.log"
echo ""
echo "================================================================================"
echo ""

# Show database stats
echo "📊 Final Database Stats:"
python3 -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv('/Users/yourox/AI-Workspace/.env')

conn = psycopg2.connect(os.getenv('RAILWAY_DATABASE_URL'))
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM github_repositories')
print(f'   GitHub Repos: {cursor.fetchone()[0]:,}')

cursor.execute('SELECT COUNT(*) FROM coding_patterns')
print(f'   Coding Patterns: {cursor.fetchone()[0]:,}')

cursor.execute('SELECT COUNT(*) FROM coding_rules')
print(f'   Coding Rules: {cursor.fetchone()[0]:,}')

cursor.execute('SELECT COUNT(*) FROM oss_commercial_repos')
print(f'   OSS Repos: {cursor.fetchone()[0]:,}')

cursor.execute('SELECT COUNT(*) FROM oss_commercial_repos WHERE docs_quality_score IS NOT NULL')
scored = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM oss_commercial_repos')
total = cursor.fetchone()[0]
if total > 0:
    print(f'   OSS Scored: {scored:,}/{total:,} ({scored/total*100:.1f}%)')

cursor.close()
conn.close()
"

echo ""
echo "🎯 Next: Run AI enrichment with 'python3 scripts/ai_intelligence_enricher.py'"
echo ""
