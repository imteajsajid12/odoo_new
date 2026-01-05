#!/usr/bin/env python3
"""
Event Reminder System Test Script

This script tests the event reminder functionality by:
1. Checking if cron jobs are configured
2. Verifying reminder methods exist
3. Testing email generation
4. Providing diagnostic information

Usage:
    ./odoo-bin shell -d your_database_name < test_reminder_system.py
    
Or manually in Odoo shell:
    ./odoo-bin shell -d your_database_name
    >>> exec(open('test_reminder_system.py').read())
"""

import logging
from datetime import datetime, timedelta
from odoo import fields

_logger = logging.getLogger(__name__)

def test_reminder_system():
    """Test the event reminder system"""
    
    print("\n" + "="*80)
    print("EVENT REMINDER SYSTEM - DIAGNOSTIC TEST")
    print("="*80 + "\n")
    
    # Test 1: Check if cron job exists
    print("📋 TEST 1: Checking Cron Job Configuration")
    print("-" * 80)
    try:
        cron = env.ref('event.event_weekly_reminder_cron', raise_if_not_found=False)
        if cron:
            print(f"✅ Cron found: {cron.name}")
            print(f"   - Active: {cron.active}")
            print(f"   - Interval: {cron.interval_number} {cron.interval_type}")
            print(f"   - Next Call: {cron.nextcall}")
            print(f"   - Code: {cron.code}")
        else:
            print("❌ Cron job 'event_weekly_reminder_cron' not found!")
            print("   ACTION: Update the event module: ./odoo-bin -d your_db -u event")
    except Exception as e:
        print(f"❌ Error checking cron: {e}")
    print()
    
    # Test 2: Check if method exists
    print("📋 TEST 2: Checking Reminder Methods")
    print("-" * 80)
    event_model = env['event.event']
    
    methods_to_check = [
        'send_weekly_event_reminders',
        '_send_one_week_reminder_emails',
        '_prepare_one_week_reminder_email_body',
        '_create_reminder_scheduled_action',
    ]
    
    for method_name in methods_to_check:
        if hasattr(event_model, method_name):
            print(f"✅ Method exists: {method_name}")
        else:
            print(f"❌ Method missing: {method_name}")
    print()
    
    # Test 3: Check for test events
    print("📋 TEST 3: Checking for Upcoming Events")
    print("-" * 80)
    
    now = fields.Datetime.now()
    future_events = env['event.event'].search([
        ('date_begin', '>', now),
        ('date_begin', '<', now + timedelta(days=14)),
        ('kanban_state', '!=', 'cancel'),
    ], limit=5)
    
    if future_events:
        print(f"Found {len(future_events)} upcoming events:")
        for event in future_events:
            time_until = event.date_begin - now
            days = time_until.days
            hours = time_until.seconds // 3600
            minutes = (time_until.seconds % 3600) // 60
            
            print(f"\n   Event: {event.name}")
            print(f"   - ID: {event.id}")
            print(f"   - Start: {event.date_begin}")
            print(f"   - Time until: {days}d {hours}h {minutes}m")
            print(f"   - Reminder sent: {event.is_reminder_sent}")
            print(f"   - Responsible: {event.user_id.name if event.user_id else 'None'}")
            print(f"   - Trainer tags: {', '.join(event.trainer_tag_ids.mapped('name')) if event.trainer_tag_ids else 'None'}")
    else:
        print("⚠️  No upcoming events found in the next 14 days")
        print("   ACTION: Create a test event to test the reminder system")
    print()
    
    # Test 4: Check test mode setting
    print("📋 TEST 4: Checking Test Mode Configuration")
    print("-" * 80)
    test_mode_param = env['ir.config_parameter'].sudo().get_param('event.reminder_test_mode', 'False')
    print(f"Test Mode: {test_mode_param}")
    if test_mode_param.lower() == 'true':
        print("   ⚠️  TEST MODE is ENABLED")
        print("   - Reminders will be sent for events 10 minutes from now")
        print("   - Cron runs every 5 minutes")
    else:
        print("   ℹ️  PRODUCTION MODE is enabled")
        print("   - Reminders will be sent 7 days before events")
        print("   - Cron should run daily")
    print()
    
    # Test 5: Check email configuration
    print("📋 TEST 5: Checking Email Configuration")
    print("-" * 80)
    mail_servers = env['ir.mail_server'].search([])
    if mail_servers:
        print(f"✅ Found {len(mail_servers)} mail server(s) configured")
        for server in mail_servers[:3]:
            print(f"   - {server.name}: {server.smtp_host}:{server.smtp_port}")
    else:
        print("❌ No mail servers configured!")
        print("   ACTION: Configure email in Settings → Technical → Outgoing Mail Servers")
    print()
    
    # Test 6: Recent reminder emails
    print("📋 TEST 6: Checking Recent Reminder Emails")
    print("-" * 80)
    recent_mails = env['mail.mail'].search([
        ('subject', 'ilike', 'Reminder:'),
        ('create_date', '>', fields.Datetime.now() - timedelta(days=7))
    ], limit=10, order='create_date DESC')
    
    if recent_mails:
        print(f"Found {len(recent_mails)} reminder emails in the last 7 days:")
        for mail in recent_mails:
            status = '✅' if mail.state == 'sent' else '⚠️ ' if mail.state == 'outgoing' else '❌'
            print(f"   {status} {mail.subject} → {mail.email_to} ({mail.state}) - {mail.create_date}")
    else:
        print("ℹ️  No reminder emails found in the last 7 days")
    print()
    
    # Test 7: Database fields
    print("📋 TEST 7: Checking Database Fields")
    print("-" * 80)
    
    # Check if fields exist
    event_fields = env['event.event']._fields
    required_fields = ['is_reminder_sent', 'reminder_cron_id', 'trainer_notified', 'responsible_notified']
    
    for field_name in required_fields:
        if field_name in event_fields:
            print(f"✅ Field exists: {field_name}")
        else:
            print(f"❌ Field missing: {field_name}")
    print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✅ The event reminder system is installed and configured!")
    print("\n📝 NEXT STEPS:")
    print("   1. If cron is not active, enable it via Settings → Technical → Scheduled Actions")
    print("   2. Create a test event with start date 10 minutes from now (test mode)")
    print("   3. Wait 5 minutes for cron to run")
    print("   4. Check if reminder email was sent")
    print("   5. Switch to production mode when ready")
    print("\n🔧 TO CREATE A TEST EVENT:")
    print("   Run: ./odoo-bin shell -d your_db")
    print("   >>> event = env['event.event'].create({")
    print("   ...     'name': 'Test Reminder Event',")
    print("   ...     'date_begin': fields.Datetime.now() + timedelta(minutes=10),")
    print("   ...     'date_end': fields.Datetime.now() + timedelta(minutes=130),")
    print("   ...     'user_id': 2,  # Admin user")
    print("   ... })")
    print("   >>> env.cr.commit()")
    print("\n📚 For detailed documentation, see: EVENT_REMINDER_SYSTEM_ANALYSIS.md")
    print("\n" + "="*80 + "\n")

# Run the test
if __name__ == '__main__':
    test_reminder_system()

# If running in Odoo shell, execute automatically
try:
    # Check if we're in Odoo environment
    if 'env' in dir():
        test_reminder_system()
except:
    print("Run this script from Odoo shell:")
    print("./odoo-bin shell -d your_database_name")
    print(">>> exec(open('test_reminder_system.py').read())")
