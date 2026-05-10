#!/bin/bash

################################################################################
# Server Monitoring System - Start Monitoring Script
# Starts all monitoring services and the Flask dashboard
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}   Server Monitoring System - Start                           ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${RED}✗ Virtual environment not found. Run setup.sh first${NC}"
    exit 1
fi

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi

# Start metrics collector in background
echo -e "${YELLOW}Starting metrics collector...${NC}"
cd "$PROJECT_ROOT"
python3 monitoring/collector.py > "$PROJECT_ROOT/logs/collector.log" 2>&1 &
COLLECTOR_PID=$!
echo -e "${GREEN}✓ Metrics collector started (PID: $COLLECTOR_PID)${NC}"
echo "$COLLECTOR_PID" > "$PROJECT_ROOT/collector.pid"

# Start Flask dashboard
echo -e "${YELLOW}Starting Flask dashboard...${NC}"
python3 dashboard/app.py > "$PROJECT_ROOT/logs/dashboard.log" 2>&1 &
DASHBOARD_PID=$!
echo -e "${GREEN}✓ Flask dashboard started (PID: $DASHBOARD_PID)${NC}"
echo "$DASHBOARD_PID" > "$PROJECT_ROOT/dashboard.pid"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✓ All services started successfully!${NC}${BLUE}                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Services:${NC}"
echo "  Metrics Collector: ${GREEN}Running${NC} (PID: $COLLECTOR_PID)"
echo "  Flask Dashboard:   ${GREEN}Running${NC} (PID: $DASHBOARD_PID)"
echo ""
echo -e "${YELLOW}Access:${NC}"
echo "  Dashboard:  ${YELLOW}http://localhost:5000${NC}"
echo "  Collector:  ${YELLOW}Logging to ${PROJECT_ROOT}/logs/collector.log${NC}"
echo "  Dashboard:  ${YELLOW}Logging to ${PROJECT_ROOT}/logs/dashboard.log${NC}"
echo ""
echo -e "${YELLOW}Stop services:${NC}"
echo "  Run: ${YELLOW}bash ${SCRIPT_DIR}/stop_monitoring.sh${NC}"
echo ""
