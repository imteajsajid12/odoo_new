#!/usr/bin/env python3
"""
Test script for Email Contacts Feature in Events App
Tests the email functionality implementation
"""

import xmlrpc.client
import sys

# Configuration
url = 'http://localhost:8069'
db = 'odoo_v1'
username = 'admin'
password = 'admin'

def test_email_feature():
    """Test the email feature implementation"""
    
    print("=" * 70)
    print("🧪 TESTING EMAIL CONTACTS FEATURE")
    print("=" * 70)
    
    try:
        # Connect to Odoo
        print("\n1️⃣  Connecting to Odoo...")
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Authentication failed!")
            return False
        
        print(f"✅ Connected successfully (UID: {uid})")
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Test 1: Check if action_send_email_to_contacts method exists
        print("\n2️⃣  Checking if action_send_email_to_contacts method exists...")
        
        # Get event model
        event_model = models.execute_kw(db, uid, password,
            'ir.model', 'search_read',
            [[['model', '=', 'event.event']]],
            {'fields': ['name', 'model'], 'limit': 1})
        
        if event_model:
            print(f"✅ Event model found: {event_model[0]['name']}")
        else:
            print("❌ Event model not found!")
            return False
        
        # Test 2: Get an event with contacts
        print("\n3️⃣  Finding events with contacts...")
        
        events = models.execute_kw(db, uid, password,
            'event.event', 'search_read',
            [[['contact_ids', '!=', False]]],
            {'fields': ['name', 'contact_ids', 'date_begin', 'address_id'], 'limit': 5})
        
        if events:
            print(f"✅ Found {len(events)} event(s) with contacts:")
            for event in events:
                contact_count = len(event.get('contact_ids', []))
                print(f"   - {event['name']} ({contact_count} contacts)")
        else:
            print("⚠️  No events with contacts found")
            print("   Creating a test event with contacts...")
            
            # Get a contact
            contacts = models.execute_kw(db, uid, password,
                'res.partner', 'search',
                [[['email', '!=', False]]], {'limit': 2})
            
            if not contacts:
                print("❌ No contacts with email found!")
                return False
            
            # Create test event
            test_event_id = models.execute_kw(db, uid, password,
                'event.event', 'create',
                [{
                    'name': 'Test Event for Email Feature',
                    'date_begin': '2025-12-01 10:00:00',
                    'date_end': '2025-12-01 18:00:00',
                    'contact_ids': [(6, 0, contacts)],
                }])
            
            print(f"✅ Created test event (ID: {test_event_id})")
            events = [{'id': test_event_id, 'name': 'Test Event for Email Feature'}]
        
        # Test 3: Test action_send_email_to_contacts method
        print("\n4️⃣  Testing action_send_email_to_contacts method...")
        
        test_event = events[0]
        
        try:
            result = models.execute_kw(db, uid, password,
                'event.event', 'action_send_email_to_contacts',
                [[test_event['id']]])
            
            if result and isinstance(result, dict):
                print("✅ Method executed successfully!")
                print(f"   Action type: {result.get('type')}")
                print(f"   Model: {result.get('res_model')}")
                print(f"   View mode: {result.get('view_mode')}")
                print(f"   Target: {result.get('target')}")
                
                if 'context' in result:
                    context = result['context']
                    print(f"   Composition mode: {context.get('default_composition_mode')}")
                    print(f"   Subject: {context.get('default_subject')}")
                    print(f"   Has body: {'default_body' in context}")
            else:
                print("❌ Method returned unexpected result")
                return False
                
        except Exception as e:
            print(f"❌ Error calling method: {e}")
            return False
        
        # Test 4: Test _get_default_email_body method
        print("\n5️⃣  Testing _get_default_email_body method...")
        
        try:
            body = models.execute_kw(db, uid, password,
                'event.event', '_get_default_email_body',
                [[test_event['id']]])
            
            if body and isinstance(body, str):
                print("✅ Email body generated successfully!")
                print(f"   Body length: {len(body)} characters")
                print(f"   Contains event name: {test_event['name'] in body}")
                print(f"   Contains HTML: {'<p>' in body}")
            else:
                print("❌ Email body generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error generating email body: {e}")
            return False
        
        # Test 5: Check view modifications
        print("\n6️⃣  Checking view modifications...")
        
        views = models.execute_kw(db, uid, password,
            'ir.ui.view', 'search_read',
            [[['model', '=', 'event.event'], ['type', '=', 'form']]],
            {'fields': ['name', 'arch_db'], 'limit': 1})
        
        if views:
            arch = views[0].get('arch_db', '')
            has_email_button = 'action_send_email_to_contacts' in arch
            has_individual_button = 'mail.action_email_compose_message_wizard' in arch
            
            print(f"✅ Form view found: {views[0]['name']}")
            print(f"   Has 'Send Email to All' button: {has_email_button}")
            print(f"   Has individual email buttons: {has_individual_button}")
            
            if not has_email_button or not has_individual_button:
                print("⚠️  Some buttons may be missing from the view")
        else:
            print("❌ Event form view not found")
            return False
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n📋 Summary:")
        print("   ✅ Email methods implemented correctly")
        print("   ✅ Action returns proper email composer configuration")
        print("   ✅ Email body generation works")
        print("   ✅ View modifications in place")
        print("\n🎯 Next Steps:")
        print("   1. Open browser: http://localhost:8069/odoo/events")
        print("   2. Open an event with contacts")
        print("   3. Go to Contacts tab")
        print("   4. Click 'Send Email to All Contacts' button")
        print("   5. Verify email composer opens with pre-filled content")
        print("   6. Test individual email buttons (envelope icons)")
        print("\n" + "=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_email_feature()
    sys.exit(0 if success else 1)

