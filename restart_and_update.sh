#!/bin/bash

echo "=========================================="
echo "Restarting Odoo to load Events Clone"
echo "=========================================="

# Find and kill existing Odoo processes
echo "Stopping existing Odoo processes..."
pkill -f "odoo-bin"
sleep 2

# Start Odoo with the updated configuration
echo "Starting Odoo with custom_addons path..."
./odoo-bin -c odoo.conf --dev=all &

echo ""
echo "=========================================="
echo "Odoo is restarting..."
echo "=========================================="
echo ""
echo "Wait 10-15 seconds for Odoo to fully start, then:"
echo ""
echo "1. Go to: http://localhost:8069/web?debug=1"
echo "2. Click on 'Apps' menu"
echo "3. Click the three dots (⋮) menu"
echo "4. Select 'Update Apps List'"
echo "5. Click 'Update'"
echo "6. Search for 'Events Clone'"
echo "7. Click 'Install'"
echo ""
echo "=========================================="

