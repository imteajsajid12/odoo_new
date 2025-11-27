# Event Email Notification System - Testing Guide

## Overview
This document provides a comprehensive guide to test the automated email notification system for Odoo Events.

## System Features

### 1. **Immediate Email on Event Creation**
When a new event is created, the system automatically sends emails to:
- **Responsible User**: The user assigned in the "Responsible" field
- **Trainer Tag Contacts**: All contacts that have the selected trainer tags

### 2. **Reminder Email (1 Minute After Creation - TEST MODE)**
⚠️ **IMPORTANT**: For testing purposes, the reminder is set to **1 MINUTE** after event creation.
- In production, this should be changed to **1 WEEK (7 days)** before the event date.
- The reminder sends emails to both Responsible User and Trainer Tag Contacts.

## Testing Instructions

### Step 1: Create a Test Event

1. **Open the Event Creation Form**
   - Navigate to: http://localhost:8069/odoo/events/new
   - Or go to Events menu → Create

2. **Fill in Event Details**
   - **Event Name**: "Email Test Event - [Your Name]"
   - **Start Date**: Set to a **FUTURE DATE** (e.g., tomorrow or next week)
   - **End Date**: Set after the start date
   - **Responsible**: Select a user with a valid email address
   - **Trainer Tags**: Select one or more trainer tags (e.g., "Trainer", "Instructor")
   
3. **Save the Event**
   - Click "Save" button
   - The system will immediately send emails to:
     - Responsible user
     - All contacts with the selected trainer tags

### Step 2: Verify Immediate Emails

1. **Check the Odoo Logs**
   - Look for log entries like:
     ```
     Event [Event Name]: _send_trainer_assignment_email called
     Event [Event Name]: Sent assignment emails to X trainer tag contacts
     Event [Event Name]: _send_responsible_assignment_email called
     Event [Event Name]: Sent assignment email to responsible user
     ```

2. **Check Email Inbox**
   - Check the email inbox of the Responsible user
   - Check the email inboxes of contacts with trainer tags
   - Subject: "You've been assigned to [Event Name] training event"

3. **Verify Email Content**
   - Email should contain:
     - Event name
     - Event dates
     - Event location (if set)
     - Event description
     - Professional HTML formatting

### Step 3: Wait for 1-Minute Reminder

1. **Wait 1 Minute**
   - After creating the event, wait for approximately 1 minute
   - The scheduled action (cron job) will trigger automatically

2. **Monitor the Logs**
   - Watch for log entries like:
     ```
     Event [Event Name]: Sending reminder emails (TEST MODE - 1 minute delay)
     Event [Event Name]: Sent one-week reminder to X trainers
     Event [Event Name]: Sent one-week reminder to responsible user
     ```

3. **Check Email Inbox Again**
   - Check for new emails with subject: "Reminder: [Event Name] - One Week to Go!"
   - Both Responsible user and Trainer tag contacts should receive this email

### Step 4: Verify Scheduled Action

1. **Check Scheduled Actions**
   - Go to Settings → Technical → Automation → Scheduled Actions
   - Search for: "Event Reminder: [Your Event Name]"
   - Verify that:
     - The action exists
     - Next Execution Date is set to ~1 minute after event creation
     - Status shows as "Active" or "Done"

2. **Check Mail Records**
   - Go to Settings → Technical → Email → Emails
   - Filter by your event
   - Verify that all emails were sent successfully

## Expected Results

### Immediate Emails (On Event Creation)
- ✅ Responsible user receives assignment email
- ✅ All trainer tag contacts receive assignment emails
- ✅ Emails are logged in the system
- ✅ Email status shows as "Sent"

### Reminder Emails (1 Minute Later)
- ✅ Scheduled action is created
- ✅ Scheduled action runs after 1 minute
- ✅ Responsible user receives reminder email
- ✅ All trainer tag contacts receive reminder emails
- ✅ Scheduled action is deactivated after running

## Troubleshooting

### No Emails Received?
1. Check if email server is configured in Odoo
2. Check spam/junk folders
3. Verify email addresses are valid
4. Check Odoo logs for errors

### Reminder Not Sent?
1. Verify event date is in the FUTURE
2. Check if scheduled action was created
3. Wait for cron job to run (may take 1-2 minutes)
4. Check Settings → Technical → Automation → Scheduled Actions

### How to Check Logs
```bash
# In terminal, navigate to Odoo directory
cd /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo

# View real-time logs
tail -f odoo.log | grep -E "Event|email|mail"
```

## Production Deployment

⚠️ **BEFORE DEPLOYING TO PRODUCTION**, change the reminder delay:

1. Open file: `addons/event/models/event_event.py`
2. Find method: `_create_reminder_scheduled_action()`
3. Change line:
   ```python
   # FROM (TEST MODE):
   reminder_datetime = fields.Datetime.now() + timedelta(minutes=1)
   
   # TO (PRODUCTION):
   reminder_datetime = self.date_begin - timedelta(days=7)
   ```

## Contact Information
For issues or questions, contact the development team.

---
**Last Updated**: 2025-11-27
**Version**: 1.0 (Test Mode)

