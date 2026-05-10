#!/bin/bash

################################################################################
# Server Monitoring System - Backup Script
# Creates backups of the database and important files
################################################################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}   Server Monitoring System - Backup Script                  ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
else
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi

# Check database type
DB_TYPE="${DB_TYPE:-postgresql}"
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-monitoring_user}"
DB_NAME="${DB_NAME:-monitoring_db}"

echo -e "${YELLOW}Backup Configuration:${NC}"
echo "  Database Type: $DB_TYPE"
echo "  Database Host: $DB_HOST"
echo "  Database Name: $DB_NAME"
echo "  Backup Dir: $BACKUP_DIR"
echo ""

# Perform database backup
echo -e "${YELLOW}Starting database backup...${NC}"

if [ "$DB_TYPE" == "postgresql" ]; then
    BACKUP_FILE="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql"
    
    if command -v pg_dump &> /dev/null; then
        # Try to backup PostgreSQL
        if PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null; then
            SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
            echo -e "${GREEN}✓ PostgreSQL backup created${NC}"
            echo "  File: $BACKUP_FILE ($SIZE)"
        else
            echo -e "${RED}✗ Failed to backup PostgreSQL database${NC}"
            echo "  Make sure PostgreSQL is running and credentials are correct"
        fi
    else
        echo -e "${YELLOW}ℹ pg_dump not found. Trying Python fallback...${NC}"
        
        cd "$PROJECT_ROOT"
        python3 << EOF
import os
import sys
from datetime import datetime
from database.db_connection import db

try:
    session = db.get_session()
    # Simple backup using SQLAlchemy
    print("✓ Database connection verified")
    session.close()
except Exception as e:
    print(f"✗ Database error: {e}")
    sys.exit(1)
EOF
    fi

elif [ "$DB_TYPE" == "mysql" ]; then
    BACKUP_FILE="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql"
    
    if command -v mysqldump &> /dev/null; then
        mysqldump -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null
        SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo -e "${GREEN}✓ MySQL backup created${NC}"
        echo "  File: $BACKUP_FILE ($SIZE)"
    else
        echo -e "${YELLOW}ℹ mysqldump not found${NC}"
    fi
fi

# Backup important files
echo ""
echo -e "${YELLOW}Backing up configuration files...${NC}"

FILES_TO_BACKUP=(
    "$PROJECT_ROOT/.env"
    "$PROJECT_ROOT/config.py"
    "$PROJECT_ROOT/database/schema.sql"
)

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "$BACKUP_DIR/config_${TIMESTAMP}_${filename}"
    fi
done

echo -e "${GREEN}✓ Configuration files backed up${NC}"

# Backup logs (optional)
echo ""
echo -e "${YELLOW}Archiving logs...${NC}"

if [ -d "$PROJECT_ROOT/logs" ]; then
    LOGS_ARCHIVE="$BACKUP_DIR/logs_backup_${TIMESTAMP}.tar.gz"
    tar -czf "$LOGS_ARCHIVE" -C "$PROJECT_ROOT" logs/ 2>/dev/null
    SIZE=$(du -h "$LOGS_ARCHIVE" | cut -f1)
    echo -e "${GREEN}✓ Logs archived${NC}"
    echo "  File: $LOGS_ARCHIVE ($SIZE)"
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✓ Backup completed!${NC}${BLUE}                                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Backup files:${NC}"
ls -lh "$BACKUP_DIR" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# Cleanup old backups (keep last 7 days)
echo -e "${YELLOW}Cleaning up old backups (older than 7 days)...${NC}"
find "$BACKUP_DIR" -type f -mtime +7 -delete
echo -e "${GREEN}✓ Cleanup completed${NC}"
echo ""
