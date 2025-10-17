#!/bin/bash

# TubeDB UI Server Management Script
# Ensures the server always runs on port 9000

PORT=9000
APP_DIR="/Users/yourox/AI-Workspace/tubedb-ui"
LOG_FILE="$APP_DIR/server.log"
PID_FILE="$APP_DIR/.server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to get PID of process using port
get_port_pid() {
    lsof -Pi :$PORT -sTCP:LISTEN -t 2>/dev/null
}

# Function to kill process on port
kill_port_process() {
    local pid=$(get_port_pid)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Killing process $pid on port $PORT...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 2
    fi
}

# Function to start the server
start_server() {
    echo -e "${GREEN}Starting TubeDB UI on port $PORT...${NC}"

    # Check if port is already in use
    if check_port; then
        echo -e "${YELLOW}Port $PORT is already in use.${NC}"
        local pid=$(get_port_pid)

        # Check if it's our Next.js app
        if ps -p $pid -o comm= | grep -q "node"; then
            echo -e "${GREEN}TubeDB UI is already running on port $PORT (PID: $pid)${NC}"
            echo $pid > "$PID_FILE"
            return 0
        else
            echo -e "${RED}Another process is using port $PORT${NC}"
            read -p "Do you want to kill it and start TubeDB UI? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill_port_process
            else
                echo -e "${RED}Aborting...${NC}"
                return 1
            fi
        fi
    fi

    # Navigate to app directory
    cd "$APP_DIR"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        npm install
    fi

    # Start the server with explicit port
    echo -e "${GREEN}Starting Next.js server on port $PORT...${NC}"
    PORT=$PORT npm run dev > "$LOG_FILE" 2>&1 &
    local server_pid=$!

    # Save PID
    echo $server_pid > "$PID_FILE"

    # Wait for server to start
    echo -n "Waiting for server to start"
    for i in {1..30}; do
        if check_port; then
            echo -e "\n${GREEN}✓ Server started successfully!${NC}"
            echo -e "${GREEN}Access the UI at: http://localhost:$PORT${NC}"
            echo -e "${YELLOW}Server PID: $server_pid${NC}"
            echo -e "${YELLOW}Logs: tail -f $LOG_FILE${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done

    echo -e "\n${RED}Failed to start server. Check logs: $LOG_FILE${NC}"
    return 1
}

# Function to stop the server
stop_server() {
    echo -e "${YELLOW}Stopping TubeDB UI...${NC}"

    # Try to read PID from file first
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping process $pid...${NC}"
            kill -TERM $pid 2>/dev/null
            sleep 2
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null
            fi
            rm -f "$PID_FILE"
        fi
    fi

    # Also check port directly
    if check_port; then
        kill_port_process
    fi

    echo -e "${GREEN}✓ Server stopped${NC}"
}

# Function to restart the server
restart_server() {
    echo -e "${YELLOW}Restarting TubeDB UI...${NC}"
    stop_server
    sleep 2
    start_server
}

# Function to check server status
check_status() {
    if check_port; then
        local pid=$(get_port_pid)
        echo -e "${GREEN}✓ TubeDB UI is running${NC}"
        echo -e "  Port: $PORT"
        echo -e "  PID: $pid"
        echo -e "  URL: http://localhost:$PORT"

        # Check if it's responding
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" | grep -q "200\|304"; then
            echo -e "  Status: ${GREEN}Responding${NC}"
        else
            echo -e "  Status: ${YELLOW}Starting up...${NC}"
        fi
    else
        echo -e "${RED}✗ TubeDB UI is not running${NC}"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}Showing last 50 lines of logs:${NC}"
        tail -50 "$LOG_FILE"
        echo -e "\n${YELLOW}For live logs: tail -f $LOG_FILE${NC}"
    else
        echo -e "${RED}No log file found${NC}"
    fi
}

# Main script logic
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "TubeDB UI Server Manager"
        echo "========================"
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the server on port $PORT"
        echo "  stop    - Stop the server"
        echo "  restart - Restart the server"
        echo "  status  - Check server status"
        echo "  logs    - Show server logs"
        echo ""
        echo "The server will always run on port $PORT"
        ;;
esac