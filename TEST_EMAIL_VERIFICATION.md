# Email Notification System - Test Verification Guide

## Quick Test Checklist

### Pre-Test Setup
- [ ] Odoo server is running
- [ ] Email server is configured (Settings → Technical → Outgoing Mail Servers)
- [ ] Developer mode is enabled (for easier debugging)
- [ ] At least one contact tag exists (e.g., "my_contact")
- [ ] At least one contact has the tag and a valid email address
- [ ] A user with valid email exists to be assigned as responsible

### Test 1: Immediate Email (Email 1)

#### Steps:
1. Navigate to Events module
2. Click "Create" to create a new event
3. Fill in the form:
   - **Name**: "Test Training Event"
   - **Start Date**: Tomorrow at 10:00 AM
   - **End Date**: Tomorrow at 5:00 PM
   - **Location**: Select or create a venue
   - **Trainer Tags**: Select "my_contact" (or your test tag)
   - **Responsible**: Select a user (e.g., imteajsajid1@gmail.com)
4. Click "Save"

#### Expected Results:
- [ ] Event is created successfully
- [ ] No error messages appear
- [ ] Check logs for: "Event Test Training Event: Sending assignment emails"

#### Verification:
1. Go to Settings → Technical → Email → Emails
2. Filter by "Model" = "event.event"
3. Look for emails with subject: "You've been assigned to Test Training Event training event"
4. Verify:
   - [ ] At least 2 emails exist (one for trainer, one for responsible)
   - [ ] Email state is "Sent" or "Outgoing"
   - [ ] Recipients are correct

### Test 2: Scheduled Action Creation

#### Verification Steps:
1. Go to Settings → Technical → Automation → Scheduled Actions
2. Search for "Event Reminder: Test Training Event"
3. Open the scheduled action

#### Expected Results:
- [ ] Scheduled action exists
- [ ] Active = True
- [ ] Next Execution Date is approximately 1 minute from event creation time
- [ ] Number of Calls = 1
- [ ] Code contains: `model._send_event_reminder([EVENT_ID])`

### Test 3: Reminder Email (Email 2)

#### Steps:
1. Wait 4-5 minutes after creating the event
2. Refresh the scheduled actions page
3. Check the email queue

#### Expected Results:
- [ ] Scheduled action is now Active = False
- [ ] New emails appear in the email queue
- [ ] Subject: "Reminder: Test Training Event - One Week to Go!"
- [ ] Emails sent to both trainer tag contacts and responsible user

#### Verification:
1. Go to Settings → Technical → Email → Emails
2. Filter by subject containing "Reminder"
3. Open one of the emails
4. Verify email contains:
   - [ ] Event title
   - [ ] Training date
   - [ ] Start and end times
   - [ ] Location
   - [ ] Responsible person
   - [ ] Number of booked attendees
   - [ ] Attendee report table (may be empty if no registrations)

### Test 4: Event Field Verification

#### Steps:
1. Open the test event
2. Enable Developer Mode (if not already)
3. Check the following fields (may need to add to view):
   - `is_reminder_sent` = True
   - `trainer_notified` = True (if implemented)
   - `responsible_notified` = True (if implemented)
   - `reminder_cron_id` = [ID of the scheduled action]

## Troubleshooting Common Issues

### Issue 1: No Emails Sent

**Symptoms**: No emails appear in the email queue

**Checks**:
1. Check Odoo logs for errors
2. Verify email server configuration
3. Verify contacts have valid email addresses
4. Check if trainer tags are properly assigned to contacts

**Solution**:
```bash
# Check logs
tail -f /var/log/odoo/odoo.log | grep "Event"

# Or in Odoo shell
# Check if contacts have emails
self.env['res.partner'].search([('category_id', 'in', [TAG_ID])]).mapped('email')
```

### Issue 2: Scheduled Action Not Created

**Symptoms**: No scheduled action appears

**Checks**:
1. Check if event has a `date_begin`
2. Check Odoo logs for errors during event creation
3. Verify user has permission to create scheduled actions

**Solution**:
Manually create the scheduled action by calling:
```python
# In Odoo shell
event = self.env['event.event'].browse([EVENT_ID])
event._create_reminder_scheduled_action()
```

### Issue 3: Reminder Email Not Sent After 5 Minutes

**Symptoms**: Scheduled action still active after 5 minutes

**Checks**:
1. Check if cron worker is running
2. Check scheduled action's "Next Execution Date"
3. Check Odoo logs for cron execution

**Solution**:
Manually trigger the scheduled action:
1. Go to the scheduled action
2. Click "Run Manually"
3. Check if emails are sent

### Issue 4: Emails in "Exception" State

**Symptoms**: Emails exist but state is "Exception"

**Checks**:
1. Open the email record
2. Check the "Failure Reason" field
3. Common issues:
   - Invalid email address
   - Email server connection failed
   - Authentication failed

**Solution**:
1. Fix the underlying issue (email address, server config, etc.)
2. Click "Retry" on the email record

## Manual Testing Commands

### Check Event Email Logs
```python
# In Odoo shell
event_id = 27  # Replace with your event ID
event = self.env['event.event'].browse(event_id)

# Check trainer tag contacts
print("Trainer Tag Contacts:")
for contact in event.trainer_tag_contact_ids:
    print(f"  - {contact.name}: {contact.email}")

# Check responsible user
print(f"\nResponsible User: {event.user_id.name} ({event.user_id.partner_id.email})")

# Check emails sent
emails = self.env['mail.mail'].search([
    ('model', '=', 'event.event'),
    ('res_id', '=', event_id)
])
print(f"\nEmails sent: {len(emails)}")
for email in emails:
    print(f"  - To: {email.email_to}, Subject: {email.subject}, State: {email.state}")

# Check scheduled action
if event.reminder_cron_id:
    print(f"\nScheduled Action: {event.reminder_cron_id.name}")
    print(f"  Next Call: {event.reminder_cron_id.nextcall}")
    print(f"  Active: {event.reminder_cron_id.active}")
```

### Manually Send Reminder Email
```python
# In Odoo shell
event_id = 27  # Replace with your event ID
event = self.env['event.event'].browse(event_id)

# Reset reminder flag
event.write({'is_reminder_sent': False})

# Send reminder
event._send_one_week_reminder_emails()
```

### Check All Event Reminders
```python
# In Odoo shell
# Find all events with pending reminders
events = self.env['event.event'].search([
    ('is_reminder_sent', '=', False),
    ('date_begin', '!=', False),
    ('active', '=', True)
])

print(f"Events with pending reminders: {len(events)}")
for event in events:
    print(f"  - {event.name} (Date: {event.date_begin})")
    if event.reminder_cron_id:
        print(f"    Scheduled for: {event.reminder_cron_id.nextcall}")
```

## Success Criteria

The implementation is working correctly if:

1. ✅ Email 1 is sent immediately when event is created
2. ✅ Email 1 is sent to all trainer tag contacts with valid emails
3. ✅ Email 1 is sent to the responsible user
4. ✅ Scheduled action is created with correct execution time
5. ✅ Email 2 is sent 4-5 minutes after event creation (test mode)
6. ✅ Email 2 contains all required information including attendee report
7. ✅ Scheduled action is deactivated after sending Email 2
8. ✅ `is_reminder_sent` flag is set to True after Email 2
9. ✅ No errors in Odoo logs
10. ✅ All emails are in "Sent" state

## Next Steps After Testing

1. If all tests pass, switch to production mode:
   - Edit `addons/event/models/event_event.py` line 1901
   - Change `timedelta(minutes=1)` to `timedelta(days=7)`
   - Restart Odoo server

2. Monitor production usage:
   - Check email delivery rates
   - Monitor scheduled action execution
   - Review user feedback

3. Consider enhancements:
   - Add email templates for easier customization
   - Add email tracking (open rates, click rates)
   - Add SMS notifications
   - Add multiple reminder intervals

