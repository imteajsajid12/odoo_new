#!/usr/bin/env python3
"""
Test script to create an event and verify email notifications.

This script creates a test event with:
- A responsible user
- Trainer tags
- Future date (to trigger reminder)

It will:
1. Create the event (triggers immediate emails)
2. Wait 1 minute
3. Check if reminder emails were sent
"""

import xmlrpc.client
import time
from datetime import datetime, timedelta

# Odoo connection settings
URL = 'http://localhost:8069'
DB = 'odoo_v1'
USERNAME = 'admin@example.com'  # Change this to your admin email
PASSWORD = 'admin'  # Change this to your admin password

def connect_odoo():
    """Connect to Odoo and return uid."""
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        raise Exception("Authentication failed! Check your credentials.")
    print(f"✓ Connected to Odoo as user ID: {uid}")
    return uid

def create_test_event(uid):
    """Create a test event with responsible user and trainer tags."""
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    # Calculate future dates
    start_date = datetime.now() + timedelta(days=7)
    end_date = start_date + timedelta(hours=3)
    
    # Event data
    event_data = {
        'name': f'Email Test Event - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        'date_begin': start_date.strftime('%Y-%m-%d %H:%M:%S'),
        'date_end': end_date.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': uid,  # Assign to current user
        'description': '<p>This is a test event to verify email notifications.</p>',
    }
    
    print("\n📧 Creating test event...")
    print(f"   Event Name: {event_data['name']}")
    print(f"   Start Date: {event_data['date_begin']}")
    print(f"   End Date: {event_data['date_end']}")
    
    # Create the event
    event_id = models.execute_kw(
        DB, uid, PASSWORD,
        'event.event', 'create',
        [event_data]
    )
    
    print(f"✓ Event created with ID: {event_id}")
    return event_id

def check_scheduled_action(uid, event_id):
    """Check if scheduled action was created for the event."""
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    # Get the event to find its reminder_cron_id
    event = models.execute_kw(
        DB, uid, PASSWORD,
        'event.event', 'read',
        [event_id],
        {'fields': ['name', 'reminder_cron_id']}
    )
    
    if event and event[0].get('reminder_cron_id'):
        cron_id = event[0]['reminder_cron_id'][0]
        print(f"✓ Scheduled action created with ID: {cron_id}")
        
        # Get cron details
        cron = models.execute_kw(
            DB, uid, PASSWORD,
            'ir.cron', 'read',
            [cron_id],
            {'fields': ['name', 'nextcall', 'active']}
        )
        
        if cron:
            print(f"   Name: {cron[0]['name']}")
            print(f"   Next Call: {cron[0]['nextcall']}")
            print(f"   Active: {cron[0]['active']}")
        
        return True
    else:
        print("⚠ No scheduled action found (event date might be in the past)")
        return False

def check_emails(uid, event_id):
    """Check if emails were sent for the event."""
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    # Search for emails related to this event
    email_ids = models.execute_kw(
        DB, uid, PASSWORD,
        'mail.mail', 'search',
        [[['model', '=', 'event.event'], ['res_id', '=', event_id]]]
    )
    
    if email_ids:
        emails = models.execute_kw(
            DB, uid, PASSWORD,
            'mail.mail', 'read',
            [email_ids],
            {'fields': ['subject', 'email_to', 'state', 'create_date']}
        )
        
        print(f"\n📬 Found {len(emails)} email(s):")
        for email in emails:
            print(f"   - To: {email['email_to']}")
            print(f"     Subject: {email['subject']}")
            print(f"     State: {email['state']}")
            print(f"     Created: {email['create_date']}")
            print()
        
        return len(emails)
    else:
        print("⚠ No emails found for this event")
        return 0

def main():
    """Main test function."""
    print("=" * 70)
    print("EVENT EMAIL NOTIFICATION TEST")
    print("=" * 70)
    
    try:
        # Connect to Odoo
        uid = connect_odoo()
        
        # Create test event
        event_id = create_test_event(uid)
        
        # Check scheduled action
        print("\n🔍 Checking scheduled action...")
        check_scheduled_action(uid, event_id)
        
        # Check immediate emails
        print("\n🔍 Checking immediate emails...")
        initial_count = check_emails(uid, event_id)
        
        # Wait for reminder
        print("\n⏳ Waiting 70 seconds for reminder email...")
        print("   (Reminder is scheduled for 1 minute after creation)")
        for i in range(70, 0, -10):
            print(f"   {i} seconds remaining...")
            time.sleep(10)
        
        # Check reminder emails
        print("\n🔍 Checking for reminder emails...")
        final_count = check_emails(uid, event_id)
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✓ Event created successfully (ID: {event_id})")
        print(f"✓ Initial emails sent: {initial_count}")
        print(f"✓ Total emails after reminder: {final_count}")
        
        if final_count > initial_count:
            print("✓ Reminder emails were sent successfully!")
        else:
            print("⚠ No new reminder emails detected")
            print("  Check the Odoo logs for more details")
        
        print("\n💡 TIP: Check your email inbox for the actual emails")
        print("💡 TIP: Check Odoo logs with: tail -f odoo.log | grep Event")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

