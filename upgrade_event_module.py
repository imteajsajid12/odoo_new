#!/usr/bin/env python3
"""
Script to upgrade the event module and reload the trainer field
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import odoo
from odoo import api, SUPERUSER_ID

def upgrade_event_module():
    """Upgrade the event module to load the trainer field"""
    
    print("=" * 80)
    print("UPGRADING EVENT MODULE")
    print("=" * 80)
    print()
    
    # Initialize Odoo
    odoo.tools.config.parse_config(['-c', 'odoo.conf'])
    
    db_name = odoo.tools.config['db_name']
    if isinstance(db_name, list):
        db_name = db_name[0] if db_name else 'odoo_v1'
    
    print(f"✓ Connected to database: {db_name}")
    print()
    
    registry = odoo.registry(db_name)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        print("Upgrading event module...")
        try:
            # Get the module
            module = env['ir.module.module'].search([('name', '=', 'event')])
            if module:
                print(f"  Found event module: {module.name} (State: {module.state})")
                
                # Upgrade the module
                module.button_upgrade()
                cr.commit()
                print("  ✓ Event module upgraded successfully!")
                print()
                
                # Verify the trainer_id field exists
                Event = env['event.event']
                if 'trainer_id' in Event._fields:
                    print("✓ trainer_id field is now available!")
                    print(f"  - Field type: {Event._fields['trainer_id'].type}")
                    print(f"  - Target model: {Event._fields['trainer_id'].comodel_name}")
                    print()
                    print("✓ MODULE UPGRADE COMPLETE!")
                    return True
                else:
                    print("✗ trainer_id field NOT found after upgrade!")
                    return False
            else:
                print("✗ Event module not found!")
                return False
        except Exception as e:
            print(f"✗ Error upgrading module: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    try:
        success = upgrade_event_module()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
