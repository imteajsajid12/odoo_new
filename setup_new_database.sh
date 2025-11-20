#!/bin/bash

# ==============================================================================
# ODOO NEW DATABASE SETUP SCRIPT
# ==============================================================================
# This script will:
# 1. Stop any running Odoo processes
# 2. Drop the corrupted database (optional)
# 3. Create a new fresh database
# 4. Start Odoo server
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================================================${NC}"
echo -e "${BLUE}ODOO NEW DATABASE SETUP${NC}"
echo -e "${BLUE}===================================================================${NC}"
echo ""

# Configuration
OLD_DB="odoo_test_db"
NEW_DB="odoo_v1"
DB_USER="luminous_imteaj"

# Step 1: Stop running Odoo processes
echo -e "${YELLOW}Step 1: Stopping running Odoo processes...${NC}"
pkill -f "odoo-bin" || true
sleep 2
echo -e "${GREEN}✓ Odoo processes stopped${NC}"
echo ""

# Step 2: Check if new database already exists
echo -e "${YELLOW}Step 2: Checking database status...${NC}"
DB_EXISTS=$(psql -U "$DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$NEW_DB'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${YELLOW}Database '$NEW_DB' already exists.${NC}"
    read -p "Do you want to drop and recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Dropping database '$NEW_DB'...${NC}"
        psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $NEW_DB;" 2>/dev/null || true
        echo -e "${GREEN}✓ Database dropped${NC}"
    else
        echo -e "${YELLOW}Using existing database '$NEW_DB'${NC}"
    fi
else
    echo -e "${GREEN}✓ Database '$NEW_DB' does not exist (will be created)${NC}"
fi
echo ""

# Step 3: Create new database (if it doesn't exist)
echo -e "${YELLOW}Step 3: Creating new database...${NC}"
DB_EXISTS=$(psql -U "$DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$NEW_DB'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" != "1" ]; then
    psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $NEW_DB OWNER $DB_USER ENCODING 'UTF8';" 2>/dev/null || {
        echo -e "${RED}✗ Failed to create database${NC}"
        echo -e "${YELLOW}Note: Database will be created automatically by Odoo on first run${NC}"
    }
    echo -e "${GREEN}✓ Database '$NEW_DB' created${NC}"
else
    echo -e "${GREEN}✓ Database '$NEW_DB' ready${NC}"
fi
echo ""

# Step 4: Update odoo.conf to use new database
echo -e "${YELLOW}Step 4: Updating odoo.conf...${NC}"
if [ -f "odoo.conf" ]; then
    # Backup original config
    cp odoo.conf odoo.conf.backup
    
    # Update db_name
    sed -i.bak "s/^db_name = .*/db_name = $NEW_DB/" odoo.conf
    
    # Update dbfilter to match new database
    sed -i.bak "s/^dbfilter = .*/dbfilter = ^${NEW_DB}\$/" odoo.conf
    
    echo -e "${GREEN}✓ Configuration updated${NC}"
    echo -e "${BLUE}  - Database name: $NEW_DB${NC}"
    echo -e "${BLUE}  - Backup saved: odoo.conf.backup${NC}"
else
    echo -e "${RED}✗ odoo.conf not found${NC}"
    exit 1
fi
echo ""

# Step 5: Start Odoo server
echo -e "${YELLOW}Step 5: Starting Odoo server...${NC}"
echo -e "${BLUE}Starting Odoo with new database '$NEW_DB'...${NC}"
echo -e "${BLUE}Access Odoo at: http://localhost:8069${NC}"
echo ""
echo -e "${GREEN}===================================================================${NC}"
echo -e "${GREEN}SETUP COMPLETE!${NC}"
echo -e "${GREEN}===================================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Run: ${BLUE}./odoo-bin --config=./odoo.conf${NC}"
echo -e "2. Open browser: ${BLUE}http://localhost:8069${NC}"
echo -e "3. Create a new database through the web interface"
echo -e "   - Database name: ${BLUE}$NEW_DB${NC}"
echo -e "   - Email: your email"
echo -e "   - Password: your password"
echo -e "   - Language: English"
echo -e "   - Country: Your country"
echo -e "   - Demo data: Check if you want sample data"
echo ""
echo -e "${YELLOW}Or run Odoo directly with:${NC}"
echo -e "${BLUE}./odoo-bin --config=./odoo.conf --dev=all${NC}"
echo ""

