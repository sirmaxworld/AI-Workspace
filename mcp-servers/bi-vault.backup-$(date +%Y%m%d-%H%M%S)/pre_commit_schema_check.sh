#!/bin/bash
#
# Pre-Commit Schema Validation Hook
# Place this in .git/hooks/pre-commit to auto-validate schema changes
#
# This script runs whenever you commit changes to:
# - schema.py
# - business_intelligence_extractor.py
# - server.py
#
# It ensures all components stay in sync

set -e

echo "🔍 Checking for schema-related changes..."

# Check if schema files are being committed
SCHEMA_CHANGED=$(git diff --cached --name-only | grep -E "(schema\.py|business_intelligence_extractor\.py|server\.py)" || true)

if [ -z "$SCHEMA_CHANGED" ]; then
    echo "✅ No schema changes detected"
    exit 0
fi

echo "⚠️  Schema-related files changed:"
echo "$SCHEMA_CHANGED"
echo ""

# Navigate to MCP directory
cd "$(dirname "$0")"

# Run schema validation
echo "Running schema validation..."
python3 schema_sync.py --full-sync

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Schema validation failed!"
    echo "   Please fix schema issues before committing"
    echo "   Run: python3 schema_sync.py --full-sync"
    exit 1
fi

# Check for breaking changes in sync results
if grep -q "Backward Compatible: ❌" <<< "$(python3 schema_sync.py --full-sync 2>&1)"; then
    echo ""
    echo "⚠️  WARNING: Breaking schema changes detected!"
    echo "   This will require data migration"
    echo ""
    read -p "Continue with commit? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Schema validation passed"
exit 0
