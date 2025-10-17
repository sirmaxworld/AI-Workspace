#!/bin/bash

echo "🔧 Shell Fix and Server Restart Script"
echo "======================================"
echo ""

# Step 1: Clean up problematic shell snapshots
echo "1. Cleaning Claude shell snapshots..."
rm -f ~/.claude/shell-snapshots/snapshot-zsh-1760609*.sh 2>/dev/null
rm -f ~/.claude/shell-snapshots/snapshot-zsh-fixed.sh 2>/dev/null
echo "   ✓ Removed problematic snapshots"

# Step 2: Archive old coding history files (don't delete, just move)
echo ""
echo "2. Archiving coding history files..."
mkdir -p ~/AI-Workspace/archive/coding_history_backup 2>/dev/null
mv ~/AI-Workspace/scripts/coding_history_shell_hooks.sh ~/AI-Workspace/archive/coding_history_backup/ 2>/dev/null
mv ~/AI-Workspace/scripts/coding_history_hooks_simple.sh ~/AI-Workspace/archive/coding_history_backup/ 2>/dev/null
echo "   ✓ Archived old hook files"

# Step 3: Verify .zshrc is clean
echo ""
echo "3. Checking .zshrc..."
if grep -q "coding_history" ~/.zshrc; then
    echo "   ⚠️  Found coding history references in .zshrc"
    echo "   Please manually remove any coding history lines from ~/.zshrc"
else
    echo "   ✓ .zshrc is clean"
fi

# Step 4: Kill any stuck processes
echo ""
echo "4. Cleaning up processes..."
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "tubedb" 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:4000 | xargs kill -9 2>/dev/null
lsof -ti:7000 | xargs kill -9 2>/dev/null
echo "   ✓ Killed any running servers"

# Step 5: Start TubeDB
echo ""
echo "5. Starting TubeDB UI on port 7000..."
echo "======================================"

cd ~/AI-Workspace/tubedb-ui

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies first..."
    npm install
fi

echo ""
echo "🚀 Starting server..."
echo "📍 Access at: http://localhost:7000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
PORT=7000 npm run dev

# If that doesn't work, try alternative
if [ $? -ne 0 ]; then
    echo ""
    echo "Trying alternative start method..."
    npx next dev -p 7000
fi