#!/bin/bash

# BI Intelligence Chat Startup Script
# Starts both backend and frontend servers

set -e

echo "🚀 Starting BI Intelligence Chat System"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python3 not found${NC}"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found${NC}"
    exit 1
fi

# Check environment
if [ ! -f "/Users/yourox/AI-Workspace/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found at /Users/yourox/AI-Workspace/.env${NC}"
    exit 1
fi

# Check for OPENROUTER_API_KEY
if ! grep -q "OPENROUTER_API_KEY" /Users/yourox/AI-Workspace/.env; then
    echo -e "${YELLOW}⚠️  OPENROUTER_API_KEY not found in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"

# Kill existing processes
echo -e "\n${BLUE}🛑 Stopping existing processes...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:9000 | xargs kill -9 2>/dev/null || true
echo -e "${GREEN}✓ Cleaned up existing processes${NC}"

# Create log directory
mkdir -p /Users/yourox/AI-Workspace/bi-chat/logs

# Start backend
echo -e "\n${BLUE}🔧 Starting backend server (port 8000)...${NC}"
cd /Users/yourox/AI-Workspace/bi-chat/server
python3 bi_chat_api.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend started successfully (PID: $BACKEND_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may not have started properly. Check logs/backend.log${NC}"
fi

# Start frontend
echo -e "\n${BLUE}🎨 Starting frontend (port 9000)...${NC}"
cd /Users/yourox/AI-Workspace/tubedb-ui
npm run dev > ../bi-chat/logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
sleep 8

# Check if frontend is running
if curl -s http://localhost:9000 > /dev/null; then
    echo -e "${GREEN}✓ Frontend started successfully (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may not have started properly. Check logs/frontend.log${NC}"
fi

# Summary
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}✨ BI Intelligence Chat is ready!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "📍 ${BLUE}Frontend:${NC} http://localhost:9000"
echo -e "📍 ${BLUE}Backend API:${NC} http://localhost:8000"
echo -e "📍 ${BLUE}Health Check:${NC} http://localhost:8000/health"
echo ""
echo -e "📊 ${BLUE}Process IDs:${NC}"
echo -e "   Backend:  ${BACKEND_PID}"
echo -e "   Frontend: ${FRONTEND_PID}"
echo ""
echo -e "📝 ${BLUE}Logs:${NC}"
echo -e "   Backend:  bi-chat/logs/backend.log"
echo -e "   Frontend: bi-chat/logs/frontend.log"
echo ""
echo -e "${YELLOW}To stop:${NC}"
echo -e "   kill ${BACKEND_PID} ${FRONTEND_PID}"
echo -e "   or run: lsof -ti:8000,9000 | xargs kill -9"
echo ""
echo -e "${GREEN}Happy analyzing! 🚀${NC}"
