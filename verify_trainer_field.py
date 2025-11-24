#!/usr/bin/env python3
"""
Verification script to check if trainer_id field is properly configured
"""

import sys
import os

# Add Odoo to path
sys.path.insert(0, os.path.dirname(__file__))

import odoo
from odoo import api, SUPERUSER_ID

# Configuration
DB_NAME = 'odoo_v1'
CONFIG_FILE = 'odoo.conf'

def verify_trainer_field():
    """Verify trainer_id field in events.clone.event"""
    
    print("=" * 80)
    print("TRAINER FIELD VERIFICATION REPORT")
    print("=" * 80)
    
    # Initialize Odoo
    odoo.tools.config.parse_config(['-c', CONFIG_FILE, '-d', DB_NAME])

    registry = odoo.registry(DB_NAME)

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
            
        # 1. Check if model exists
        print("\n1. MODEL CHECK:")
        try:
            Event = env['events.clone.event']
            print("   ✓ Model 'events.clone.event' exists")
        except Exception as e:
            print(f"   ✗ Model not found: {e}")
            return

        # 2. Check if trainer_id field exists
        print("\n2. FIELD CHECK:")
        if hasattr(Event, 'trainer_id'):
            print("   ✓ Field 'trainer_id' exists in model")

            # Get field info
            field_info = Event._fields.get('trainer_id')
            print(f"   - Field type: {field_info.type}")
            print(f"   - Related model: {field_info.comodel_name}")
            print(f"   - String: {field_info.string}")
        else:
            print("   ✗ Field 'trainer_id' NOT found in model")
            return

        # 3. Check view
        print("\n3. VIEW CHECK:")
        view = env['ir.ui.view'].search([('name', '=', 'events.clone.event.form')])
        if view:
            print(f"   ✓ Form view found (ID: {view.id})")

            if 'trainer_id' in view.arch:
                print("   ✓ Field 'trainer_id' found in view XML")

                # Extract the section
                import re
                pattern = r'<field name="trainer_id"[^>]*>'
                match = re.search(pattern, view.arch)
                if match:
                    print(f"   - Field definition: {match.group(0)}")
            else:
                print("   ✗ Field 'trainer_id' NOT found in view XML")
        else:
            print("   ✗ Form view not found")

        # 4. Check existing events
        print("\n4. EVENT DATA CHECK:")
        events = Event.search([])
        print(f"   Total events: {len(events)}")

        if events:
            for event in events:
                trainer_name = event.trainer_id.name if event.trainer_id else "Not set"
                print(f"   - Event '{event.name}' (ID: {event.id})")
                print(f"     Trainer: {trainer_name}")
                print(f"     Seats Limited: {event.seats_limited}")

        # 5. Check contacts availability
        print("\n5. CONTACTS CHECK:")
        try:
            contacts = env['res.partner'].search([('is_company', '=', False)], limit=5)
            print(f"   ✓ Found {len(contacts)} contacts")
            for contact in contacts:
                print(f"   - {contact.name} (ID: {contact.id})")
        except Exception as e:
            print(f"   ✗ Error accessing contacts: {e}")

        # 6. View structure analysis
        print("\n6. VIEW STRUCTURE ANALYSIS:")
        if view:
            # Find the position of trainer_id relative to seats_limited
            arch_str = view.arch
            seats_pos = arch_str.find('seats_limited')
            trainer_pos = arch_str.find('trainer_id')

            if seats_pos > 0 and trainer_pos > 0:
                if trainer_pos > seats_pos:
                    print("   ✓ trainer_id appears AFTER seats_limited (correct position)")
                    print(f"   - seats_limited at position: {seats_pos}")
                    print(f"   - trainer_id at position: {trainer_pos}")
                else:
                    print("   ✗ trainer_id appears BEFORE seats_limited (wrong position)")

            # Extract context around trainer_id
            start = max(0, trainer_pos - 200)
            end = min(len(arch_str), trainer_pos + 300)
            context = arch_str[start:end]
            print("\n   Context around trainer_id field:")
            print("   " + "-" * 70)
            for line in context.split('\n'):
                if line.strip():
                    print(f"   {line}")
            print("   " + "-" * 70)
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print("\nNEXT STEPS:")
    print("1. Open browser to: http://localhost:8069")
    print("2. Navigate to: Events Clone > Events > Events")
    print("3. Open an existing event or create a new one")
    print("4. Look for 'Trainer' field below 'Limit Attendees'")
    print("5. If not visible, try:")
    print("   - Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)")
    print("   - Clear browser cache")
    print("   - Log out and log back in")
    print("=" * 80)

if __name__ == '__main__':
    verify_trainer_field()

