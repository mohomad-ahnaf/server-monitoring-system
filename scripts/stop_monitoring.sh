#!/bin/bash

################################################################################
# Server Monitoring System - Stop Monitoring Script
# Stops all monitoring services
################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}   Server Monitoring System - Stop                            ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Stop collector
if [ -f "$PROJECT_ROOT/collector.pid" ]; then
    COLLECTOR_PID=$(cat "$PROJECT_ROOT/collector.pid")
    if kill -0 $COLLECTOR_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping metrics collector (PID: $COLLECTOR_PID)...${NC}"
        kill $COLLECTOR_PID
        rm "$PROJECT_ROOT/collector.pid"
        echo -e "${GREEN}✓ Metrics collector stopped${NC}"
    else
        echo -e "${YELLOW}ℹ Metrics collector not running${NC}"
        rm "$PROJECT_ROOT/collector.pid"
    fi
else
    echo -e "${YELLOW}ℹ No collector PID file found${NC}"
fi

# Stop dashboard
if [ -f "$PROJECT_ROOT/dashboard.pid" ]; then
    DASHBOARD_PID=$(cat "$PROJECT_ROOT/dashboard.pid")
    if kill -0 $DASHBOARD_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping Flask dashboard (PID: $DASHBOARD_PID)...${NC}"
        kill $DASHBOARD_PID
        rm "$PROJECT_ROOT/dashboard.pid"
        echo -e "${GREEN}✓ Flask dashboard stopped${NC}"
    else
        echo -e "${YELLOW}ℹ Flask dashboard not running${NC}"
        rm "$PROJECT_ROOT/dashboard.pid"
    fi
else
    echo -e "${YELLOW}ℹ No dashboard PID file found${NC}"
fi

echo ""
echo -e "${GREEN}✓ All services stopped${NC}"
echo ""
