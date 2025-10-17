#!/bin/bash
# Quick script to run the fix from terminal

echo "🔧 Starting Claude Desktop Shell Snapshot Fix..."
echo "================================================"

# Run the investigation first
echo -e "\n📊 Running investigation..."
python3 /Users/yourox/AI-Workspace/investigate_shell_issue.py

# Run the fix
echo -e "\n🔧 Running fix..."
python3 /Users/yourox/AI-Workspace/fix_shell_snapshots.py

echo -e "\n✅ Fix complete! Please restart Claude Desktop for best results."