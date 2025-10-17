#!/bin/bash

echo "🚀 Starting TubeDB UI on Port 7000"
echo "==================================="
echo ""

# Kill any existing processes on common ports
echo "1. Cleaning up existing processes..."
pkill -f "tubedb" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null

# Kill anything on ports 3000, 4000, and 7000
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:4000 | xargs kill -9 2>/dev/null
lsof -ti:7000 | xargs kill -9 2>/dev/null

echo "✓ Processes cleaned up"

# Navigate to TubeDB directory
echo ""
echo "2. Navigating to TubeDB directory..."
cd /Users/yourox/AI-Workspace/tubedb-ui

# Check if directory exists
if [ ! -d "/Users/yourox/AI-Workspace/tubedb-ui" ]; then
    echo "❌ Error: TubeDB directory not found!"
    echo "Expected at: /Users/yourox/AI-Workspace/tubedb-ui"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo ""
    echo "3. Installing dependencies..."
    npm install
fi

# Start the server on port 7000
echo ""
echo "3. Starting server on port 7000..."
echo "==================================="
echo ""
echo "📍 Server will be available at: http://localhost:7000"
echo ""

# Start with explicit port 7000
PORT=7000 npm run dev

# If that fails, try with next dev directly
if [ $? -ne 0 ]; then
    echo ""
    echo "Trying alternative method..."
    npx next dev -p 7000
fi