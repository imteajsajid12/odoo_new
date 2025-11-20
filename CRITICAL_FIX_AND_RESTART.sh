#!/bin/bash

echo "============================================================"
echo "CRITICAL FIX: Restarting Odoo with custom_addons path"
echo "============================================================"
echo ""
echo "ISSUE FOUND:"
echo "  Odoo is running with OLD configuration (before custom_addons was added)"
echo "  Started at: 5:12PM (before odoo.conf was updated)"
echo ""
echo "SOLUTION:"
echo "  1. Kill ALL running Odoo processes"
echo "  2. Start Odoo with UPDATED odoo.conf"
echo "  3. Update Apps List in Odoo"
echo "  4. Install Events Clone"
echo ""
echo "============================================================"
echo ""

# Step 1: Kill all Odoo processes
echo "[Step 1/4] Stopping ALL Odoo processes..."
pkill -9 -f "odoo-bin"
sleep 3

# Verify all processes are killed
if pgrep -f "odoo-bin" > /dev/null; then
    echo "  ⚠ Some Odoo processes still running. Trying again..."
    pkill -9 -f "odoo-bin"
    sleep 2
fi

if pgrep -f "odoo-bin" > /dev/null; then
    echo "  ✗ ERROR: Could not stop Odoo processes"
    echo "  Please manually stop Odoo and run this script again"
    exit 1
else
    echo "  ✓ All Odoo processes stopped"
fi

# Step 2: Verify configuration
echo ""
echo "[Step 2/4] Verifying odoo.conf..."
if grep -q "custom_addons" odoo.conf; then
    echo "  ✓ custom_addons path is in odoo.conf"
    grep "addons_path" odoo.conf | sed 's/^/    /'
else
    echo "  ✗ ERROR: custom_addons NOT in odoo.conf"
    exit 1
fi

# Step 3: Start Odoo with updated configuration
echo ""
echo "[Step 3/4] Starting Odoo with updated configuration..."

# Check if virtual environment exists
if [ -d "odoo-venv" ]; then
    echo "  Using virtual environment: odoo-venv"
    source odoo-venv/bin/activate
    CMD="odoo-venv/bin/python3 ./odoo-bin -c odoo.conf --dev=all"
else
    echo "  Using system Python 3.12"
    CMD="/opt/homebrew/Cellar/python@3.12/3.12.12/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python ./odoo-bin -c odoo.conf --dev=all"
fi

echo "  Command: $CMD"
echo ""

# Start Odoo in background
nohup $CMD > odoo_startup.log 2>&1 &
ODOO_PID=$!

echo "  ✓ Odoo starting... (PID: $ODOO_PID)"
echo "  ✓ Logs: odoo_startup.log"
echo ""
echo "  Waiting for Odoo to start (this may take 15-30 seconds)..."

# Wait for Odoo to start
for i in {1..30}; do
    if grep -q "HTTP service.*running" odoo_startup.log 2>/dev/null; then
        echo "  ✓ Odoo started successfully!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Check if Odoo is running
if pgrep -f "odoo-bin" > /dev/null; then
    echo "  ✓ Odoo process is running"
else
    echo "  ✗ ERROR: Odoo failed to start"
    echo "  Check odoo_startup.log for errors"
    exit 1
fi

# Step 4: Instructions for user
echo ""
echo "[Step 4/4] Next Steps - FOLLOW THESE CAREFULLY:"
echo "============================================================"
echo ""
echo "1. Open your browser and go to:"
echo "   http://localhost:8069/web?debug=1"
echo ""
echo "2. Click on 'Apps' menu (grid icon)"
echo ""
echo "3. Click the three dots (⋮) in the top-right corner"
echo ""
echo "4. Select 'Update Apps List'"
echo ""
echo "5. Click 'Update' button and wait"
echo ""
echo "6. Remove the 'Apps' filter (click X on the filter chip)"
echo ""
echo "7. Search for: Events Clone"
echo ""
echo "8. Click 'Install' button"
echo ""
echo "============================================================"
echo ""
echo "✓ Odoo is now running with custom_addons path!"
echo "✓ Events Clone module is ready to be installed!"
echo ""
echo "If you see any errors, check: odoo_startup.log"
echo "============================================================"

