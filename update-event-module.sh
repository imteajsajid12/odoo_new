#!/bin/bash
################################################################################
# UPDATE EVENT MODULE SCRIPT
################################################################################
# This script updates the event module to refresh views and code changes
################################################################################

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

VENV_PATH="./odoo-venv"
ODOO_BIN="./odoo-bin"
ODOO_CONF="./odoo.conf"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              UPDATE EVENT MODULE                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}⚠ This will stop Odoo, update the event module, and restart it${NC}"
echo ""

# Stop Odoo if running
echo -e "${BLUE}ℹ Stopping Odoo...${NC}"
pkill -f "odoo-bin"
sleep 2

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Update the event module
echo -e "${BLUE}ℹ Updating event module...${NC}"
$VENV_PATH/bin/python3 $ODOO_BIN --config=$ODOO_CONF -u event --stop-after-init

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Event module updated successfully!${NC}"
    echo ""
    echo -e "${BLUE}ℹ Starting Odoo...${NC}"
    ./start-odoo.sh
else
    echo -e "${RED}✗ Failed to update event module${NC}"
    exit 1
fi
