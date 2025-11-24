#!/usr/bin/env python3
"""
Trigger event module upgrade via direct database connection
"""

import psycopg2
import sys

def upgrade_event_module():
    """Upgrade event module by updating ir_module_module state"""
    
    print("=" * 80)
    print("TRIGGERING EVENT MODULE UPGRADE")
    print("=" * 80)
    print()
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="odoo_v1",
            user="luminous_imteaj",
            password=""
        )
        cursor = conn.cursor()
        
        print("✓ Connected to PostgreSQL")
        print()
        
        # Check current state of event module
        cursor.execute("""
            SELECT id, name, state FROM ir_module_module 
            WHERE name = 'event'
        """)
        result = cursor.fetchone()
        
        if result:
            module_id, module_name, current_state = result
            print(f"Event module found:")
            print(f"  - ID: {module_id}")
            print(f"  - Name: {module_name}")
            print(f"  - Current State: {current_state}")
            print()
            
            # Mark module for upgrade
            if current_state == 'installed':
                print("Marking module for upgrade...")
                cursor.execute("""
                    UPDATE ir_module_module 
                    SET state = 'to upgrade'
                    WHERE id = %s
                """, (module_id,))
                conn.commit()
                print("✓ Module marked for upgrade!")
                print()
                print("The module will be upgraded when Odoo processes the queue.")
                print("Please refresh the browser to see the changes.")
                return True
            else:
                print(f"Module is in '{current_state}' state, no upgrade needed.")
                return False
        else:
            print("✗ Event module not found in database!")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    success = upgrade_event_module()
    sys.exit(0 if success else 1)
