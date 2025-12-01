# Event Email Notification System - Documentation

## Overview

This document describes the automated email notification system for training events in Odoo. The system sends two types of emails:

1. **Email 1 (Immediate)**: Sent immediately when an event is created to trainers and responsible person
2. **Email 2 (Reminder)**: Sent one week before the event (configurable for testing)

## Features Implemented

### 1. Immediate Email Notifications (Email 1)

When a new event is created, the system automatically sends assignment emails to:

- **All contacts with selected trainer tags** (via `trainer_tag_ids` field)
- **The responsible user** (via `user_id` field)

#### Email 1 Content:

- Training event title
- Training date
- Event start and end times
- Location
- Responsible person (assigned CSP)
- Max number of attendees

### 2. Scheduled Reminder Emails (Email 2)

One week before the event (or 4-5 minutes for testing), the system sends reminder emails to:

- **All contacts with selected trainer tags**
- **The responsible user**

#### Email 2 Content:

- Training event title
- Training date
- Event start and end times
- Location
- Responsible person (assigned CSP)
- Number of booked attendees
- **Attendee report** with additional event information (includes name, email, phone, status, registration date)

## Database Fields Added

The following fields were added to the `event.event` model:

```python
# Trainer Tags
trainer_tag_ids = fields.Many2many(
    'res.partner.category',
    'event_trainer_tag_rel',
    'event_id',
    'category_id',
    string='Trainer Tags',
    help='Select contact tags to filter trainers for email communication'
)

# Notification Tracking
is_reminder_sent = fields.Boolean(
    string='Reminder Email Sent',
    default=False,
    copy=False,
    help='Indicates if the one-week reminder email has been sent'
)

trainer_notified = fields.Boolean(
    string='Trainer Notified',
    default=False,
    copy=False,
    help='Indicates if trainers have been notified about this event'
)

responsible_notified = fields.Boolean(
    string='Responsible Notified',
    default=False,
    copy=False,
    help='Indicates if the responsible user has been notified about this event'
)

reminder_cron_id = fields.Many2one(
    'ir.cron',
    string='Reminder Scheduled Action',
    ondelete='cascade',
    copy=False,
    help='Scheduled action for sending one-week reminder email'
)
```

## How It Works

### Event Creation Flow

1. User creates a new event
2. User selects trainer tags (e.g., "my_contact")
3. User assigns a responsible user (e.g., imteajsajid1@gmail.com)
4. Upon saving:
   - System finds all contacts with the selected trainer tags
   - Sends Email 1 to all trainer tag contacts
   - Sends Email 1 to the responsible user
   - Creates a scheduled action (cron job) for Email 2

### Scheduled Reminder Flow

1. A scheduled action (cron job) is created for each event
2. The cron job is set to run at a specific time:
   - **TEST MODE**: 4-5 minutes after event creation
   - **PRODUCTION MODE**: 1 week before the event
3. When the cron job runs:
   - Checks if reminder was already sent (`is_reminder_sent`)
   - Checks if event is cancelled
   - Sends Email 2 to trainer tag contacts
   - Sends Email 2 to responsible user
   - Marks `is_reminder_sent = True`
   - Deactivates the cron job

## Testing Configuration

### Current Test Mode Settings

The system is currently configured for **TESTING** with the following settings:

**File**: `addons/event/models/event_event.py`

**Line 1901**: Reminder scheduled for 1 minute after creation

```python
reminder_datetime = fields.Datetime.now() + timedelta(minutes=1)
```

### Switching to Production Mode

To switch to production mode (1 week before event):

**Change Line 1901** from:

```python
reminder_datetime = fields.Datetime.now() + timedelta(minutes=1)
```

To:

```python
reminder_datetime = self.date_begin - timedelta(days=7)
```

## Key Methods

### Email Sending Methods

- `_send_trainer_assignment_email()`: Sends Email 1 to trainer tag contacts
- `_send_responsible_assignment_email()`: Sends Email 1 to responsible user
- `_send_one_week_reminder_emails()`: Sends Email 2 to both trainers and responsible
- `_prepare_assignment_email_body()`: Generates HTML for Email 1
- `_prepare_one_week_reminder_email_body()`: Generates HTML for Email 2
- `_generate_attendee_report_html()`: Generates attendee table for Email 2

### Scheduled Action Methods

- `_create_reminder_scheduled_action()`: Creates cron job for Email 2
- `_update_reminder_scheduled_action()`: Updates cron when event date changes
- `_delete_reminder_scheduled_action()`: Deletes cron when event is deleted
- `_send_event_reminder()`: Static method called by cron job

### Lifecycle Hooks

- `create()`: Overridden to send Email 1 and create reminder cron
- `write()`: Overridden to handle changes to trainer tags, responsible user, or event date
- `unlink()`: Overridden to clean up scheduled actions

## How to Test

### Step 1: Prepare Test Data

1. Create contact tags (e.g., "my_contact")
2. Assign tags to contacts in the system
3. Ensure contacts have valid email addresses

### Step 2: Create an Event

1. Navigate to Events module
2. Create a new event
3. Fill in required fields:
   - Event name
   - Start date/time
   - End date/time
   - Location
4. Select trainer tags (e.g., "my_contact")
5. Assign a responsible user
6. Save the event

### Step 3: Verify Email 1 (Immediate)

Check that emails were sent immediately:

- Go to Settings → Technical → Email → Emails
- Look for emails with subject: "You've been assigned to [Event Name] training event"
- Verify recipients include trainer tag contacts and responsible user

### Step 4: Verify Scheduled Action Created

1. Go to Settings → Technical → Automation → Scheduled Actions
2. Look for: "Event Reminder: [Event Name]"
3. Check the "Next Execution Date" (should be ~1 minute from creation in test mode)

### Step 5: Wait and Verify Email 2 (Reminder)

Wait 4-5 minutes, then check:

- Go to Settings → Technical → Email → Emails
- Look for emails with subject: "Reminder: [Event Name] - One Week to Go!"
- Verify the email contains:
  - Event details
  - Number of booked attendees
  - Attendee report table
- Check that the scheduled action is now inactive

## Troubleshooting

### Emails Not Sending

#### Check 1: Email Server Configuration

1. Go to Settings → Technical → Outgoing Mail Servers
2. Verify that an outgoing mail server is configured
3. Test the connection

#### Check 2: Contact Email Addresses

1. Verify that trainer tag contacts have valid email addresses
2. Verify that the responsible user has a valid email address
3. Check: Settings → Users & Companies → Users → [User] → Email

#### Check 3: Trainer Tags

1. Verify that trainer tags are selected on the event
2. Verify that contacts have the selected tags
3. Check: Contacts → [Contact] → Tags

#### Check 4: Check Logs

View the Odoo logs for detailed information:

```bash
# Look for log entries like:
# Event [Event Name]: Sending assignment emails
# Event [Event Name]: Sent assignment emails to X trainer tag contacts
# Event [Event Name]: Created reminder scheduled action
```

#### Check 5: Email Queue

1. Go to Settings → Technical → Email → Emails
2. Filter by State = "Outgoing" or "Exception"
3. Check for any failed emails

### Scheduled Action Not Running

#### Check 1: Verify Scheduled Action Exists

1. Go to Settings → Technical → Automation → Scheduled Actions
2. Search for "Event Reminder: [Event Name]"
3. Verify it exists and is active

#### Check 2: Check Next Execution Date

1. Open the scheduled action
2. Check "Next Execution Date"
3. Verify it's set to the correct time (1 minute from creation in test mode)

#### Check 3: Manually Trigger

1. Open the scheduled action
2. Click "Run Manually" button
3. Check if emails are sent

#### Check 4: Check Cron Worker

Ensure the Odoo cron worker is running:

```bash
# Check if --max-cron-threads is set (should be > 0)
# Default is 2
```

### Reminder Already Sent

If you need to resend the reminder:

1. Open the event
2. Set `is_reminder_sent` to False (via developer mode)
3. Manually trigger the scheduled action

## Email Templates

### Email 1 Template (Assignment)

- **Subject**: "You've been assigned to [Event Name] training event"
- **Styling**: Professional blue theme
- **Sections**:
  - Welcome message
  - Event details table
  - Event description (if available)
  - Call to action

### Email 2 Template (Reminder)

- **Subject**: "Reminder: [Event Name] - One Week to Go!"
- **Styling**: Professional orange/warning theme
- **Sections**:
  - Reminder banner
  - Event details table
  - Number of booked attendees (highlighted)
  - Attendee report table with:
    - Attendee number
    - Name
    - Email
    - Phone
    - Status (Confirmed/Attended)
    - Registration date
  - Event description (if available)
  - Action required message

## Database Queries for Verification

### Check if emails were sent for an event

```sql
SELECT
    mm.id,
    mm.subject,
    mm.email_to,
    mm.state,
    mm.create_date
FROM mail_mail mm
WHERE mm.model = 'event.event'
  AND mm.res_id = [EVENT_ID]
ORDER BY mm.create_date DESC;
```

### Check scheduled actions for events

```sql
SELECT
    ic.id,
    ic.name,
    ic.nextcall,
    ic.active,
    ic.numbercall
FROM ir_cron ic
WHERE ic.name LIKE 'Event Reminder:%'
ORDER BY ic.create_date DESC;
```

### Check reminder status for events

```sql
SELECT
    ee.id,
    ee.name,
    ee.is_reminder_sent,
    ee.trainer_notified,
    ee.responsible_notified,
    ee.reminder_cron_id
FROM event_event ee
WHERE ee.active = true
ORDER BY ee.create_date DESC;
```

## Architecture Diagram

```
Event Creation
     |
     v
[create() method]
     |
     +---> Send Email 1 to Trainers (_send_trainer_assignment_email)
     |
     +---> Send Email 1 to Responsible (_send_responsible_assignment_email)
     |
     +---> Create Scheduled Action (_create_reminder_scheduled_action)
                |
                v
        [ir.cron record created]
        Next Call: Now + 1 minute (test) or Event Date - 7 days (prod)
                |
                v
        [Cron worker executes at scheduled time]
                |
                v
        [_send_event_reminder() method]
                |
                +---> Check if already sent
                |
                +---> Check if event cancelled
                |
                +---> Send Email 2 (_send_one_week_reminder_emails)
                |
                +---> Mark is_reminder_sent = True
                |
                +---> Deactivate cron job
```

## Code Locations

### Main Implementation File

- **File**: `addons/event/models/event_event.py`
- **Lines**: 130-155 (Field definitions)
- **Lines**: 1200-1993 (Email methods and logic)

### Key Code Sections

1. **Field Definitions**: Lines 130-272
2. **Email Body Generators**: Lines 1200-1820
3. **Email Sending Methods**: Lines 1360-1452
4. **Lifecycle Hooks**: Lines 1453-1547
5. **Scheduled Action Management**: Lines 1887-1993

## Performance Considerations

### Email Sending

- Emails are sent using `mail.mail` model with `sudo()` for reliability
- `auto_delete=False` ensures email records are kept for auditing
- Emails are sent synchronously during event creation (consider async for large batches)

### Scheduled Actions

- One cron job per event (cleanup happens automatically on event deletion)
- Cron jobs are deactivated after execution to prevent re-runs
- `numbercall=1` ensures single execution

### Database Impact

- Minimal: 4 new boolean/reference fields per event
- Indexes on foreign keys for performance
- Scheduled actions are cleaned up on event deletion

## Future Enhancements

### Possible Improvements

1. **Email Templates**: Move to `mail.template` for easier customization
2. **Batch Processing**: Send emails asynchronously for large events
3. **Multiple Reminders**: Support for multiple reminder intervals
4. **Email Preferences**: Allow users to opt-out of certain notifications
5. **SMS Integration**: Add SMS notifications alongside emails
6. **Localization**: Support for multiple languages in emails
7. **Attachments**: Add event calendar (.ics) files to emails
8. **Analytics**: Track email open rates and click-through rates

## Support and Maintenance

### Logs Location

Check Odoo server logs for detailed information:

```bash
# Look for entries with:
# - "Event [Name]: ..."
# - "_send_event_reminder called for event ID: ..."
# - "Sent assignment emails to X trainer tag contacts"
```

### Common Log Messages

- `Event {name}: Sending assignment emails` - Email 1 being sent
- `Event {name}: Created reminder scheduled action` - Cron job created
- `Event {name}: Sending reminder emails (TEST MODE - 1 minute delay)` - Email 2 being sent
- `Event {name}: Marked is_reminder_sent = True` - Reminder completed

## Conclusion

This email notification system provides automated communication for training events, ensuring that trainers and responsible persons are notified both at event creation and one week before the event. The system is fully integrated with Odoo's email infrastructure and scheduled action framework, providing reliable and trackable email delivery.
