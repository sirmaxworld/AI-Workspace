#!/bin/bash

# TubeDB Manager - Comprehensive server management
# Ensures server ALWAYS runs on port 7000

PORT=7000
APP_DIR="/Users/yourox/AI-Workspace/tubedb-ui"
MAIN_DIR="/Users/yourox/AI-Workspace"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       TubeDB Manager (Port 7000)     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo

# Function to check if port is in use
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill anything on port 7000
kill_port() {
    echo -e "${YELLOW}Checking port $PORT...${NC}"
    if check_port; then
        local pid=$(lsof -Pi :$PORT -sTCP:LISTEN -t 2>/dev/null)
        echo -e "${RED}Killing process $pid on port $PORT${NC}"
        kill -9 $pid 2>/dev/null
        sleep 2
    fi
    echo -e "${GREEN}✓ Port $PORT is clear${NC}"
}

# Function to start with npm
start_npm() {
    kill_port
    cd "$APP_DIR"
    echo -e "${GREEN}Starting TubeDB UI on port $PORT with npm...${NC}"
    npm run dev &
    echo -e "${GREEN}✓ Server starting on http://localhost:$PORT${NC}"
}

# Function to start with PM2
start_pm2() {
    echo -e "${GREEN}Starting TubeDB UI with PM2...${NC}"
    cd "$APP_DIR"

    # Check if PM2 is installed
    if ! command -v pm2 &> /dev/null; then
        echo -e "${YELLOW}PM2 not found. Installing globally...${NC}"
        npm install -g pm2
    fi

    # Kill anything on port first
    kill_port

    # Start with PM2
    pm2 start ecosystem.config.js --only tubedb-ui-dev
    pm2 save
    echo -e "${GREEN}✓ Server managed by PM2 on port $PORT${NC}"
    echo -e "${YELLOW}Commands:${NC}"
    echo "  pm2 logs tubedb-ui-dev    - View logs"
    echo "  pm2 stop tubedb-ui-dev    - Stop server"
    echo "  pm2 restart tubedb-ui-dev - Restart server"
    echo "  pm2 monit                 - Monitor server"
}

# Function to start production with PM2
start_production() {
    echo -e "${GREEN}Starting TubeDB UI in PRODUCTION mode...${NC}"
    cd "$APP_DIR"

    # Build first
    echo -e "${YELLOW}Building production version...${NC}"
    npm run build

    # Kill anything on port
    kill_port

    # Start production with PM2
    pm2 start ecosystem.config.js --only tubedb-ui
    pm2 save
    echo -e "${GREEN}✓ Production server running on port $PORT${NC}"
}

# Function to stop all
stop_all() {
    echo -e "${RED}Stopping all TubeDB processes...${NC}"

    # Stop PM2 processes
    if command -v pm2 &> /dev/null; then
        pm2 stop tubedb-ui 2>/dev/null
        pm2 stop tubedb-ui-dev 2>/dev/null
        pm2 delete tubedb-ui 2>/dev/null
        pm2 delete tubedb-ui-dev 2>/dev/null
    fi

    # Kill port
    kill_port

    echo -e "${GREEN}✓ All processes stopped${NC}"
}

# Function to check status
status() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}TubeDB Status Check${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

    # Check port
    if check_port; then
        local pid=$(lsof -Pi :$PORT -sTCP:LISTEN -t 2>/dev/null)
        echo -e "${GREEN}✓ Server is running${NC}"
        echo -e "  Port: $PORT"
        echo -e "  PID: $pid"
        echo -e "  URL: http://localhost:$PORT"

        # Check if responding
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" | grep -q "200\|304"; then
            echo -e "  Status: ${GREEN}Responding${NC}"

            # Count videos
            response=$(curl -s "http://localhost:$PORT/api/batch" 2>/dev/null)
            if [ $? -eq 0 ]; then
                video_count=$(echo "$response" | grep -o '"video_id"' | wc -l)
                echo -e "  Videos in DB: ${GREEN}$video_count${NC}"
            fi
        else
            echo -e "  Status: ${YELLOW}Starting up...${NC}"
        fi
    else
        echo -e "${RED}✗ Server is not running${NC}"
    fi

    # Check PM2 status
    if command -v pm2 &> /dev/null; then
        echo -e "\n${BLUE}PM2 Status:${NC}"
        pm2 list | grep tubedb || echo "  No PM2 processes"
    fi

    echo
}

# Main menu
case "$1" in
    start)
        start_npm
        ;;
    start-pm2)
        start_pm2
        ;;
    start-prod)
        start_production
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_npm
        ;;
    status)
        status
        ;;
    kill-port)
        kill_port
        ;;
    *)
        echo "Usage: $0 {start|start-pm2|start-prod|stop|restart|status|kill-port}"
        echo
        echo "Commands:"
        echo "  start      - Start development server (npm)"
        echo "  start-pm2  - Start with PM2 (auto-restart)"
        echo "  start-prod - Start production build with PM2"
        echo "  stop       - Stop all TubeDB processes"
        echo "  restart    - Restart the server"
        echo "  status     - Check server status"
        echo "  kill-port  - Kill anything on port $PORT"
        echo
        echo -e "${GREEN}Server ALWAYS runs on port $PORT${NC}"
        echo -e "${BLUE}Access at: http://localhost:$PORT${NC}"
        ;;
esac