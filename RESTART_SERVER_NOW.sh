#!/bin/bash

echo "🔄 Server Restart Script"
echo "======================="
echo ""

# Kill any existing TubeDB processes
echo "1. Stopping existing TubeDB processes..."
pkill -f "tubedb" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:4000 | xargs kill -9 2>/dev/null
echo "✓ Processes stopped"

# Navigate to TubeDB directory
echo ""
echo "2. Starting TubeDB UI..."
cd /Users/yourox/AI-Workspace/tubedb-ui

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the server
echo ""
echo "3. Launching server on port 4000..."
echo "================================"
echo ""
npm run dev

# If npm run dev fails, try alternative
if [ $? -ne 0 ]; then
    echo ""
    echo "Trying alternative start method..."
    npx next dev -p 4000
fi