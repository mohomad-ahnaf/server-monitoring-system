#!/bin/bash

################################################################################
# Server Monitoring System - Setup Script
# Initializes the system with all dependencies and configuration
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}   Server Monitoring System - Setup Script                    ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ] && [ "$1" != "--no-sudo" ]; then 
    echo -e "${YELLOW}ℹ Some operations may require sudo. Re-running with sudo...${NC}"
    sudo "$0" "$@"
    exit $?
fi

echo -e "${GREEN}✓ Starting setup...${NC}"
echo ""

# Step 1: Check Python installation
echo -e "${BLUE}[1/6] Checking Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "  Install it with: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"
echo ""

# Step 2: Create virtual environment
echo -e "${BLUE}[2/6] Setting up Python virtual environment...${NC}"
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    python3 -m venv "$PROJECT_ROOT/venv"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 3: Install Python dependencies
echo -e "${BLUE}[3/6] Installing Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r "$PROJECT_ROOT/requirements.txt"
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Step 4: Setup environment file
echo -e "${BLUE}[4/6] Configuring environment...${NC}"
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo -e "${YELLOW}ℹ Created .env file from example${NC}"
    echo -e "${YELLOW}  Please edit: $PROJECT_ROOT/.env${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Step 5: Create necessary directories
echo -e "${BLUE}[5/6] Creating directories...${NC}"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/data"
mkdir -p "$PROJECT_ROOT/backups"
chmod 755 "$PROJECT_ROOT/logs"
chmod 755 "$PROJECT_ROOT/data"
chmod 755 "$PROJECT_ROOT/backups"
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 6: Initialize database
echo -e "${BLUE}[6/6] Initializing database...${NC}"
cd "$PROJECT_ROOT"
python3 database/db_connection.py
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✓ Setup completed successfully!${NC}${BLUE}                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit configuration: ${YELLOW}${PROJECT_ROOT}/.env${NC}"
echo "2. Start monitoring: ${YELLOW}bash ${SCRIPT_DIR}/start_monitoring.sh${NC}"
echo "3. Start dashboard: ${YELLOW}cd ${PROJECT_ROOT} && python3 dashboard/app.py${NC}"
echo "4. Access dashboard: ${YELLOW}http://localhost:5000${NC}"
echo ""
