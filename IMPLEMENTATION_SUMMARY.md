# Event Email Notification System - Implementation Summary

## 🎯 Project Overview

Implemented an automated email notification system for Odoo Events that sends:
1. **Immediate emails** when an event is created
2. **Reminder emails** at a scheduled time (1 minute for testing, 1 week for production)

## ✅ What Was Implemented

### 1. Email Notifications on Event Creation
- **Recipients**: 
  - Responsible User (assigned in the event)
  - Trainer Tag Contacts (all contacts with selected trainer tags)
- **Trigger**: Automatically when event is created or when responsible/trainer tags are updated
- **Email Content**: Professional HTML email with event details

### 2. Scheduled Reminder Emails
- **Recipients**: Same as above (Responsible + Trainer Tag Contacts)
- **Timing**: 
  - **TEST MODE**: 1 minute after event creation
  - **PRODUCTION**: 1 week before event date
- **Implementation**: Uses Odoo's `ir.cron` scheduled actions
- **Auto-cleanup**: Scheduled action is deactivated after running

### 3. Email Content Features
- Event name and description
- Event dates and times
- Event location (if set)
- Professional HTML formatting
- Different messages for assignment vs. reminder

## 📁 Files Modified

### Main Implementation File
- **File**: `addons/event/models/event_event.py`
- **Key Changes**:
  - Modified `_create_reminder_scheduled_action()` method (lines 1883-1904)
  - Changed reminder delay from 7 days to 1 minute for testing
  - Updated docstrings to indicate TEST MODE

### Key Methods
1. `_send_trainer_assignment_email()` - Sends immediate email to trainer tag contacts
2. `_send_responsible_assignment_email()` - Sends immediate email to responsible user
3. `_send_one_week_reminder_emails()` - Sends reminder emails
4. `_create_reminder_scheduled_action()` - Creates scheduled action for reminder
5. `_send_event_reminder()` - Static method called by cron job

## 🧪 Testing Tools Created

### 1. Testing Guide
- **File**: `EVENT_EMAIL_TESTING_GUIDE.md`
- **Purpose**: Step-by-step instructions for testing the system
- **Includes**: 
  - How to create test events
  - How to verify emails
  - Troubleshooting tips

### 2. Python Test Script
- **File**: `test_event_email.py`
- **Purpose**: Automated testing script
- **Features**:
  - Creates test event via XML-RPC
  - Checks scheduled actions
  - Monitors email sending
  - Waits for reminder and verifies

### 3. Log Monitor Script
- **File**: `monitor_event_emails.sh`
- **Purpose**: Real-time log monitoring
- **Features**:
  - Color-coded output
  - Filters relevant log entries
  - Easy to track email sending

## 🚀 How to Test

### Option 1: Manual Testing (Recommended)
```bash
# 1. Open the event creation form
http://localhost:8069/odoo/events/new

# 2. Fill in the form:
#    - Event Name: "Test Event"
#    - Start Date: Tomorrow or next week (MUST BE FUTURE)
#    - Responsible: Select a user with email
#    - Trainer Tags: Select one or more tags

# 3. Save the event

# 4. Check logs for immediate emails:
tail -f odoo.log | grep "Event"

# 5. Wait 1 minute for reminder email

# 6. Check logs again for reminder emails
```

### Option 2: Automated Testing
```bash
# 1. Edit test_event_email.py and update credentials:
#    USERNAME = 'your_email@example.com'
#    PASSWORD = 'your_password'

# 2. Run the test script:
python3 test_event_email.py

# 3. The script will:
#    - Create a test event
#    - Check immediate emails
#    - Wait 70 seconds
#    - Check reminder emails
#    - Display summary
```

### Option 3: Monitor Logs in Real-Time
```bash
# Run the monitoring script:
./monitor_event_emails.sh

# Then create an event in the browser
# Watch the logs update in real-time
```

## 📊 Expected Results

### Immediate Emails (On Event Creation)
```
✓ Responsible user receives email
✓ All trainer tag contacts receive emails
✓ Email subject: "You've been assigned to [Event Name] training event"
✓ Emails logged in Settings → Technical → Email → Emails
```

### Reminder Emails (1 Minute Later)
```
✓ Scheduled action created (ir.cron)
✓ Scheduled action runs after ~1 minute
✓ Responsible user receives reminder email
✓ All trainer tag contacts receive reminder emails
✓ Email subject: "Reminder: [Event Name] - One Week to Go!"
✓ Scheduled action deactivated after running
```

## 🔧 Production Deployment

⚠️ **CRITICAL**: Before deploying to production, change the reminder delay:

**File**: `addons/event/models/event_event.py`  
**Method**: `_create_reminder_scheduled_action()`  
**Line**: ~1897

**Change FROM**:
```python
# FOR TESTING: Calculate when to send reminder (1 minute from now)
reminder_datetime = fields.Datetime.now() + timedelta(minutes=1)
```

**Change TO**:
```python
# FOR PRODUCTION: Calculate when to send reminder (7 days before event)
reminder_datetime = self.date_begin - timedelta(days=7)
```

## 📝 System Architecture

```
Event Creation
    ↓
create() method called
    ↓
    ├─→ _send_trainer_assignment_email()
    │   └─→ Send immediate emails to trainer tag contacts
    │
    ├─→ _send_responsible_assignment_email()
    │   └─→ Send immediate email to responsible user
    │
    └─→ _create_reminder_scheduled_action()
        └─→ Create ir.cron scheduled action
            ↓
        (Wait 1 minute)
            ↓
        ir.cron triggers
            ↓
        _send_event_reminder() called
            ↓
        _send_one_week_reminder_emails()
            ├─→ Send reminder to trainer tag contacts
            └─→ Send reminder to responsible user
```

## 🐛 Troubleshooting

### No Emails Sent?
1. Check email server configuration in Odoo
2. Verify email addresses are valid
3. Check spam/junk folders
4. Review logs: `tail -f odoo.log | grep -i error`

### Reminder Not Triggered?
1. Ensure event date is in the FUTURE
2. Check if scheduled action was created:
   - Settings → Technical → Automation → Scheduled Actions
   - Search for "Event Reminder"
3. Wait 1-2 minutes (cron jobs may have slight delay)
4. Check if cron worker is running

### How to Verify Email Sending
```bash
# Check mail.mail records in database
# Go to: Settings → Technical → Email → Emails
# Filter by your event name
# Check status column (should be "Sent")
```

## 📞 Support

For issues or questions:
1. Check the logs first
2. Review the testing guide
3. Contact the development team

---

**Implementation Date**: 2025-11-27  
**Version**: 1.0 (Test Mode)  
**Status**: ✅ Ready for Testing  
**Next Step**: Test thoroughly, then deploy to production with updated timing

