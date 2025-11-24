#!/usr/bin/env python3
"""
Simple script to check trainer field in view - run via odoo shell
"""

# Check if the view contains trainer_id field
view = env['ir.ui.view'].search([('name', '=', 'events.clone.event.form')])
print("=" * 80)
print("TRAINER FIELD VIEW VERIFICATION")
print("=" * 80)

if view:
    print(f"\n✓ Form view found: {view.name} (ID: {view.id})")
    
    # Check if trainer_id is in the view
    if 'trainer_id' in view.arch:
        print("✓ Field 'trainer_id' FOUND in view XML")
        
        # Find position relative to seats_limited
        arch_str = view.arch
        seats_pos = arch_str.find('seats_limited')
        trainer_pos = arch_str.find('trainer_id')
        
        print(f"\nPosition analysis:")
        print(f"  - seats_limited at position: {seats_pos}")
        print(f"  - trainer_id at position: {trainer_pos}")
        
        if trainer_pos > seats_pos:
            print("  ✓ trainer_id appears AFTER seats_limited (CORRECT)")
        else:
            print("  ✗ trainer_id appears BEFORE seats_limited (WRONG)")
        
        # Extract context around trainer_id
        import re
        pattern = r'.{0,300}<field name="trainer_id"[^>]*>.{0,300}'
        match = re.search(pattern, arch_str, re.DOTALL)
        if match:
            print("\nContext around trainer_id field:")
            print("-" * 80)
            context = match.group(0)
            # Clean up and format
            for line in context.split('\n'):
                line = line.strip()
                if line:
                    print(f"  {line}")
            print("-" * 80)
    else:
        print("✗ Field 'trainer_id' NOT FOUND in view XML")
else:
    print("✗ Form view not found")

# Check events
print("\nEvent data:")
Event = env['events.clone.event']
events = Event.search([])
print(f"Total events: {len(events)}")

if events:
    for event in events:
        trainer_name = event.trainer_id.name if event.trainer_id else "Not set"
        print(f"  - Event: {event.name} (ID: {event.id})")
        print(f"    Trainer: {trainer_name}")
        print(f"    Seats Limited: {event.seats_limited}")

# Check contacts
print("\nContacts available:")
contacts = env['res.partner'].search([('is_company', '=', False)], limit=5)
print(f"Found {len(contacts)} contacts:")
for contact in contacts:
    print(f"  - {contact.name} (ID: {contact.id})")

print("\n" + "=" * 80)
print("BROWSER TESTING INSTRUCTIONS:")
print("=" * 80)
print("1. Open browser to: http://localhost:8069")
print("2. Navigate to: Events Clone > Events > Events")
print("3. Click on an event to open it")
print("4. Look for 'Trainer' field below 'Limit Attendees'")
print("5. If not visible:")
print("   - Press Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)")
print("   - This will hard refresh and clear browser cache")
print("   - Or try logging out and logging back in")
print("=" * 80)

