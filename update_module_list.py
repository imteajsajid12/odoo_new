#!/usr/bin/env python3
"""
Script to update Odoo module list and check if events_clone is available
This should be run AFTER Odoo has been restarted with the updated configuration
"""

import xmlrpc.client
import sys

# Odoo connection details
url = "http://localhost:8069"
db = "odoo_v1"
username = "admin"
password = "admin"  # Change this if your admin password is different

print("=" * 70)
print("Odoo Module List Updater - Events Clone")
print("=" * 70)
print()

try:
    # Connect to Odoo
    print("[1/5] Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    
    # Check version
    version_info = common.version()
    print(f"  ✓ Connected to Odoo {version_info.get('server_version')}")
    print()
    
    # Authenticate
    print("[2/5] Authenticating...")
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("  ✗ Authentication failed!")
        print("  Please check your username and password")
        sys.exit(1)
    
    print(f"  ✓ Authenticated as user ID: {uid}")
    print()
    
    # Get models proxy
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Update module list
    print("[3/5] Updating module list...")
    print("  This may take 10-30 seconds...")
    
    try:
        # Call update_list method on ir.module.module
        models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])
        print("  ✓ Module list updated successfully!")
    except Exception as e:
        print(f"  ✗ Error updating module list: {e}")
        sys.exit(1)
    
    print()
    
    # Search for events_clone module
    print("[4/5] Searching for Events Clone module...")
    
    module_ids = models.execute_kw(
        db, uid, password,
        'ir.module.module', 'search',
        [[['name', '=', 'events_clone']]]
    )
    
    if module_ids:
        print(f"  ✓ Events Clone module found! (ID: {module_ids[0]})")
        
        # Get module details
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids],
            {'fields': ['name', 'state', 'latest_version', 'summary', 'application']}
        )
        
        if module_data:
            module = module_data[0]
            print(f"  Name: {module.get('name')}")
            print(f"  State: {module.get('state')}")
            print(f"  Version: {module.get('latest_version')}")
            print(f"  Summary: {module.get('summary')}")
            print(f"  Application: {module.get('application')}")
    else:
        print("  ✗ Events Clone module NOT found!")
        print()
        print("  Possible reasons:")
        print("  1. Odoo was not restarted with updated odoo.conf")
        print("  2. custom_addons path is not correct in odoo.conf")
        print("  3. Module has syntax errors")
        print()
        print("  Please run: ./CRITICAL_FIX_AND_RESTART.sh")
        sys.exit(1)
    
    print()
    
    # Final instructions
    print("[5/5] Next Steps:")
    print("=" * 70)
    print()
    print("✓ Events Clone module is now available in Odoo!")
    print()
    print("To install it:")
    print("  1. Go to: http://localhost:8069/web#action=base.open_module_tree")
    print("  2. Remove the 'Apps' filter (click X)")
    print("  3. Search for: Events Clone")
    print("  4. Click 'Install'")
    print()
    print("=" * 70)
    
except xmlrpc.client.Fault as e:
    print(f"  ✗ XML-RPC Error: {e}")
    sys.exit(1)
except ConnectionRefusedError:
    print("  ✗ Cannot connect to Odoo!")
    print("  Make sure Odoo is running on http://localhost:8069")
    sys.exit(1)
except Exception as e:
    print(f"  ✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

