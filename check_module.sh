#!/bin/bash

echo "=========================================="
echo "Events Clone Module Diagnostic Check"
echo "=========================================="
echo ""

# Check 1: Module directory exists
echo "✓ Checking module directory..."
if [ -d "custom_addons/events_clone" ]; then
    echo "  ✓ Module directory exists"
else
    echo "  ✗ Module directory NOT found!"
    exit 1
fi

# Check 2: Required files exist
echo ""
echo "✓ Checking required files..."
files=(
    "custom_addons/events_clone/__init__.py"
    "custom_addons/events_clone/__manifest__.py"
    "custom_addons/events_clone/models/__init__.py"
    "custom_addons/events_clone/security/ir.model.access.csv"
    "custom_addons/events_clone/security/events_clone_security.xml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING!"
    fi
done

# Check 3: Python syntax
echo ""
echo "✓ Checking Python syntax..."
python3 -m py_compile custom_addons/events_clone/__init__.py 2>/dev/null && echo "  ✓ __init__.py is valid" || echo "  ✗ __init__.py has errors"
python3 -m py_compile custom_addons/events_clone/models/__init__.py 2>/dev/null && echo "  ✓ models/__init__.py is valid" || echo "  ✗ models/__init__.py has errors"

# Check 4: Odoo configuration
echo ""
echo "✓ Checking Odoo configuration..."
if grep -q "custom_addons" odoo.conf; then
    echo "  ✓ custom_addons path is in odoo.conf"
    echo "  Current addons_path:"
    grep "addons_path" odoo.conf | sed 's/^/    /'
else
    echo "  ✗ custom_addons path NOT in odoo.conf!"
fi

# Check 5: Odoo process
echo ""
echo "✓ Checking Odoo process..."
if pgrep -f "odoo-bin" > /dev/null; then
    echo "  ✓ Odoo is running"
    echo "  Process:"
    ps aux | grep "odoo-bin" | grep -v grep | sed 's/^/    /'
else
    echo "  ✗ Odoo is NOT running!"
    echo "  Start Odoo with: ./odoo-bin -c odoo.conf --dev=all"
fi

# Check 6: File permissions
echo ""
echo "✓ Checking file permissions..."
if [ -r "custom_addons/events_clone/__manifest__.py" ]; then
    echo "  ✓ Files are readable"
else
    echo "  ✗ Permission issues detected!"
    echo "  Run: chmod -R 755 custom_addons/events_clone"
fi

# Summary
echo ""
echo "=========================================="
echo "Diagnostic Summary"
echo "=========================================="
echo ""
echo "If all checks passed (✓), you can proceed with:"
echo "1. Restart Odoo (if not already done)"
echo "2. Go to http://localhost:8069/web?debug=1"
echo "3. Apps → Update Apps List"
echo "4. Search for 'Events Clone'"
echo "5. Click Install"
echo ""
echo "For detailed instructions, see: FOLLOW_THESE_STEPS.md"
echo "=========================================="

