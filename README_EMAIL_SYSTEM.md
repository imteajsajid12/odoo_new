# Event Email Notification System - Quick Start Guide

## 🎯 What This System Does

This system automatically sends emails when you create training events in Odoo:

1. **Email 1 (Immediate)**: Sent right away to trainers and responsible person
2. **Email 2 (Reminder)**: Sent 4-5 minutes later (test mode) or 1 week before event (production mode)

## 📧 Email Details

### Email 1: Assignment Notification
**Subject**: "You've been assigned to [Event Name] training event"

**Contains**:
- Training event title
- Training date
- Event start and end times
- Location
- Responsible person (CSP)
- Max number of attendees

### Email 2: One Week Reminder
**Subject**: "Reminder: [Event Name] - One Week to Go!"

**Contains**:
- All information from Email 1, PLUS:
- **Number of booked attendees** (highlighted)
- **Attendee report table** with:
  - Attendee name
  - Email
  - Phone
  - Status (Confirmed/Attended)
  - Registration date

## 🚀 How to Use

### Step 1: Create an Event
1. Go to Events module
2. Click "Create"
3. Fill in the form:
   - **Name**: Your event name
   - **Start Date**: When the event starts
   - **End Date**: When the event ends
   - **Location**: Where the event takes place
   - **Trainer Tags**: Select tags (e.g., "my_contact")
   - **Responsible**: Select a user (e.g., imteajsajid1@gmail.com)
4. Click "Save"

### Step 2: Verify Immediate Emails
1. Go to Settings → Technical → Email → Emails
2. Look for emails with subject: "You've been assigned to..."
3. Verify emails were sent to:
   - All contacts with selected trainer tags
   - The responsible user

### Step 3: Wait for Reminder
- **Test Mode**: Wait 4-5 minutes
- **Production Mode**: Reminder sent 1 week before event

### Step 4: Verify Reminder Emails
1. Go to Settings → Technical → Email → Emails
2. Look for emails with subject: "Reminder: ... - One Week to Go!"
3. Verify the email contains attendee report

## 🔍 How to Check if It's Working

### Check 1: Immediate Emails Sent
```
Settings → Technical → Email → Emails
Filter by: Model = "event.event"
Look for: Subject contains "You've been assigned"
Status should be: "Sent"
```

### Check 2: Scheduled Action Created
```
Settings → Technical → Automation → Scheduled Actions
Search for: "Event Reminder: [Your Event Name]"
Check: Next Execution Date (should be ~1 minute from now in test mode)
```

### Check 3: Reminder Emails Sent
```
Wait 4-5 minutes, then:
Settings → Technical → Email → Emails
Look for: Subject contains "Reminder"
Status should be: "Sent"
```

### Check 4: Scheduled Action Deactivated
```
Settings → Technical → Automation → Scheduled Actions
Find your event's scheduled action
Check: Active = False (after reminder is sent)
```

## 📚 Documentation Files

1. **EVENT_EMAIL_NOTIFICATION_DOCUMENTATION.md** - Complete technical documentation
2. **TEST_EMAIL_VERIFICATION.md** - Detailed testing guide
3. **IMPLEMENTATION_SUMMARY.md** - Implementation details
4. **README_EMAIL_SYSTEM.md** - This file (quick start)

## ⚙️ Current Configuration

**Mode**: TEST MODE  
**Reminder Timing**: 4-5 minutes after event creation  
**Purpose**: Quick testing and verification

## 🔄 Switching to Production Mode

When ready for production, change line 1901 in `addons/event/models/event_event.py`:

**FROM**:
```python
reminder_datetime = fields.Datetime.now() + timedelta(minutes=1)
```

**TO**:
```python
reminder_datetime = self.date_begin - timedelta(days=7)
```

Then restart Odoo.

## ❓ Troubleshooting

### Problem: No emails sent
**Solution**: 
- Check email server configuration (Settings → Technical → Outgoing Mail Servers)
- Verify contacts have valid email addresses
- Check trainer tags are assigned to contacts

### Problem: Reminder not sent after 5 minutes
**Solution**:
- Check if scheduled action exists
- Manually trigger: Open scheduled action → Click "Run Manually"
- Check Odoo logs for errors

### Problem: Emails in "Exception" state
**Solution**:
- Open the email record
- Check "Failure Reason"
- Fix the issue (usually invalid email or server problem)
- Click "Retry"

## 📞 Need Help?

1. Check the logs: `tail -f /var/log/odoo/odoo.log | grep "Event"`
2. Review **EVENT_EMAIL_NOTIFICATION_DOCUMENTATION.md** for detailed troubleshooting
3. Review **TEST_EMAIL_VERIFICATION.md** for testing procedures

## ✅ Success Criteria

The system is working correctly if:

- ✅ Email 1 sent immediately when event is created
- ✅ Email 1 sent to all trainer tag contacts
- ✅ Email 1 sent to responsible user
- ✅ Scheduled action created
- ✅ Email 2 sent after 4-5 minutes (test mode)
- ✅ Email 2 contains attendee report
- ✅ Scheduled action deactivated after Email 2
- ✅ No errors in logs

## 🎉 You're All Set!

The email notification system is ready to use. Just create an event and the emails will be sent automatically!

For detailed information, see the other documentation files.

