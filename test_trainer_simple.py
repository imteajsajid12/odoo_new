"""
Simple test to verify trainer field - Run with: ./odoo-bin shell -c odoo.conf -d odoo_v1 < test_trainer_simple.py
"""

print("=" * 80)
print("TESTING TRAINER FIELD IMPLEMENTATION")
print("=" * 80)
print()

# Test 1: Check if events.clone.event model exists
print("Test 1: Checking if events.clone.event model exists...")
try:
    Event = env['events.clone.event']
    print("  ✓ events.clone.event model found")
except KeyError:
    print("  ✗ events.clone.event model NOT found!")
    exit(1)
print()

# Test 2: Check if trainer_id field exists
print("Test 2: Checking if trainer_id field exists...")
if 'trainer_id' in Event._fields:
    print("  ✓ trainer_id field exists")
    field = Event._fields['trainer_id']
    print(f"  - Field type: {field.type}")
    print(f"  - Field string: {field.string}")
    print(f"  - Comodel: {field.comodel_name}")
else:
    print("  ✗ trainer_id field NOT found!")
    exit(1)
print()

# Test 3: Check if contacts_available field exists
print("Test 3: Checking if contacts_available field exists...")
if 'contacts_available' in Event._fields:
    print("  ✓ contacts_available field exists")
else:
    print("  ✗ contacts_available field NOT found!")
    exit(1)
print()

# Test 4: Check if res.partner (contacts) are available
print("Test 4: Checking if contacts are available...")
try:
    Partner = env['res.partner']
    contact_count = Partner.search_count([('is_company', '=', False)])
    print(f"  ✓ Found {contact_count} contacts in the system")
    
    # Show first 5 contacts
    if contact_count > 0:
        contacts = Partner.search([('is_company', '=', False)], limit=5)
        print("  Sample contacts:")
        for contact in contacts:
            print(f"    - {contact.name} (ID: {contact.id})")
except Exception as e:
    print(f"  ✗ Error accessing contacts: {e}")
    exit(1)
print()

# Test 5: Check if events exist
print("Test 5: Checking existing events...")
event_count = Event.search_count([])
print(f"  ✓ Found {event_count} events in the system")

if event_count > 0:
    events = Event.search([], limit=3)
    print("  Sample events:")
    for event in events:
        trainer_name = event.trainer_id.name if event.trainer_id else "Not assigned"
        print(f"    - {event.name} (ID: {event.id}) - Trainer: {trainer_name}")
print()

# Test 6: Test creating an event with a trainer
print("Test 6: Testing event creation with trainer...")
try:
    # Get a contact to use as trainer
    trainer = Partner.search([('is_company', '=', False)], limit=1)
    if trainer:
        # Create a test event
        test_event = Event.create({
            'name': 'Test Event - Trainer Field Test',
            'date_begin': '2024-12-01 10:00:00',
            'date_end': '2024-12-01 18:00:00',
            'trainer_id': trainer.id,
        })
        print(f"  ✓ Created test event (ID: {test_event.id})")
        print(f"  - Event name: {test_event.name}")
        print(f"  - Trainer: {test_event.trainer_id.name}")
        print(f"  - Contacts available: {test_event.contacts_available}")
        
        # Clean up - delete test event
        test_event.unlink()
        print("  ✓ Test event cleaned up")
    else:
        print("  ⚠ No contacts available to test with")
except Exception as e:
    print(f"  ✗ Error creating test event: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
print()

print("=" * 80)
print("ALL TESTS PASSED! ✓")
print("=" * 80)
print()
print("The Trainer field has been successfully implemented!")
print()
print("You can now:")
print("1. Open http://localhost:8069/odoo/events/3 to view an existing event")
print("2. Open http://localhost:8069/odoo/events/new to create a new event")
print("3. The Trainer field will appear below 'Limit Registrations'")
print("4. Select any contact from the dropdown to assign as trainer")
print()

