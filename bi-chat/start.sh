#!/bin/bash
# Start BI Intelligence Chat
# Starts both backend and frontend servers

set -e

echo "🚀 Starting BI Intelligence Chat..."
echo ""

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "❌ Error: .env file not found at ../AI-Workspace/.env"
    echo "Please create .env with OPENROUTER_API_KEY"
    exit 1
fi

# Check for OpenRouter API key
if ! grep -q "OPENROUTER_API_KEY" ../.env; then
    echo "⚠️  Warning: OPENROUTER_API_KEY not found in .env"
    echo "The chat will not work without this key"
fi

echo "📦 Checking dependencies..."
echo ""

# Check Python dependencies
if [ ! -d "server/venv" ]; then
    echo "Creating Python virtual environment..."
    cd server
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "✅ Python venv found"
fi

# Check Node dependencies
if [ ! -d "ui/node_modules" ]; then
    echo "Installing Node dependencies..."
    cd ui
    npm install
    cd ..
else
    echo "✅ Node modules found"
fi

echo ""
echo "🔥 Starting servers..."
echo ""

# Start backend in background
echo "Starting Backend (port 8000)..."
cd server
source venv/bin/activate 2>/dev/null || true
python bi_chat_api.py > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start. Check server/backend.log"
    exit 1
fi

# Test backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend running on http://localhost:8000"
else
    echo "⚠️  Backend started but health check failed"
fi

echo ""

# Start frontend
echo "Starting Frontend (port 3001)..."
cd ui
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 BI Intelligence Chat is starting!"
echo ""
echo "📍 Frontend: http://localhost:3001"
echo "📍 Backend:  http://localhost:8000"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:  bi-chat/server/backend.log"
echo "   Frontend: stdout"
echo ""
echo "🛑 To stop: Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for frontend
wait $FRONTEND_PID

# Cleanup
echo ""
echo "🛑 Shutting down..."
kill $BACKEND_PID 2>/dev/null || true
rm -f .backend.pid .frontend.pid
echo "✅ Stopped"
