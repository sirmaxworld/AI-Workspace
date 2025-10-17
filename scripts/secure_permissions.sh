#!/bin/bash
# Secure Permissions Maintenance Script
# Ensures sensitive files maintain proper permissions

WORKSPACE="/Users/yourox/AI-Workspace"

echo "🔒 Securing AI-Workspace permissions..."

# Secret files - owner only (600)
chmod 600 "$WORKSPACE/.env" 2>/dev/null
chmod 600 "$WORKSPACE/data/claude_memory_json/memories_secret.json" 2>/dev/null

# Private files - owner + group read (640)
chmod 640 "$WORKSPACE/data/claude_memory_json/memories_private.json" 2>/dev/null
chmod 640 "$WORKSPACE/data/claude_memory_json/memories_confidential.json" 2>/dev/null

# Public files - world readable (644)
chmod 644 "$WORKSPACE/data/claude_memory_json/memories_public.json" 2>/dev/null

echo "✓ Permissions secured"
echo ""
echo "Current permissions:"
ls -la "$WORKSPACE/.env" "$WORKSPACE/data/claude_memory_json/memories_"*.json 2>/dev/null
