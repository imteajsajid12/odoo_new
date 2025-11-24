#!/bin/bash

# Start Odoo with event module upgrade
cd /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo

echo "Starting Odoo with event module upgrade..."
echo ""

# Use the Python 3.12 that was previously working
/opt/homebrew/Cellar/python@3.12/3.12.12/Frameworks/Python.framework/Versions/3.12/Resources/Python.app/Contents/MacOS/Python \
  -c "
import sys
import os
sys.path.insert(0, '/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo')
os.chdir('/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo')

# Import and run Odoo CLI
from odoo.cli import main

# Run with -u event flag to upgrade the event module
sys.argv = ['odoo-bin', '-c', 'odoo.conf', '-u', 'event', '--dev=all']
main()
" &

sleep 10
echo "Odoo started. Waiting for module upgrade to complete..."
sleep 10
echo "Done! Access Odoo at http://localhost:8069"
