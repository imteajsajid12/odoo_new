# Event Notification System Documentation

## 📋 Overview

This document describes the automated email notification system for Odoo Events. The system sends two types of emails:

1. **Email 1: Immediate Assignment Notification** - Sent when an event is created or when trainers/responsible persons are assigned
2. **Email 2: One Week Reminder** - Sent one week before the event starts

---

## 🎯 Features

### 1. Immediate Assignment Notifications (Email 1)

**Trigger:** When an event is created or updated with trainer tags or responsible user

**Recipients:**
- Trainers (contacts with selected trainer tags)
- Responsible person (assigned CSP user)

**Email Content:**
1. Training event title
2. Training date
3. Event start and end times
4. Location
5. Responsible person (assigned CSP)
6. Max number of attendees

**When it's sent:**
- Immediately after event creation (if trainer tags or responsible user are set)
- When trainer tags are added/changed on an existing event
- When responsible user is assigned/changed on an existing event

---

### 2. Weekly Reminder Notifications (Email 2)

**Trigger:** Automated cron job runs every 5 minutes (TEST MODE) or daily (PRODUCTION MODE)

**Recipients:**
- Trainers (contacts with selected trainer tags)
- Responsible person (assigned CSP user)

**Email Content:**
1. Training event title
2. Training date
3. Event start and end times
4. Location
5. Responsible person (assigned CSP)
6. Number of booked attendees
7. **Attendee report** with the 'Additional Event Information' including:
   - Attendee name
   - Email
   - Phone
   - Status (Confirmed/Attended)
   - Registration date

**When it's sent:**
- **TEST MODE:** 10 minutes before event (±5 minute window)
- **PRODUCTION MODE:** 7 days before event

---

## ⚙️ Configuration

### Test Mode vs Production Mode

The system supports two modes for testing and production:

#### **TEST MODE (Current Configuration)**
- Cron runs every **5 minutes**
- Looks for events **10 minutes** from now (±5 minute window)
- Perfect for testing email functionality

#### **PRODUCTION MODE**
- Cron runs every **24 hours** (1 day)
- Looks for events **7 days** from now
- Standard production configuration

---

## 🔧 How to Switch Between Modes

### Method 1: Update Cron Configuration (Recommended for Production)

Edit `addons/event/data/ir_cron_data.xml`:

```xml
<!-- For PRODUCTION MODE -->
<record model="ir.cron" forcecreate="True" id="event_weekly_reminder_cron">
    <field name="name">Event: Weekly Reminder Scheduler</field>
    <field name="model_id" ref="model_event_event"/>
    <field name="state">code</field>
    <field name="code">model.send_weekly_event_reminders()</field>
    <field name="user_id" ref="base.user_root"/>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="nextcall" eval="(DateTime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')" />
</record>
```

After editing, upgrade the module:
```bash
./odoo-venv/bin/python3 ./odoo-bin --config=./odoo.conf -u event --stop-after-init
```

### Method 2: Use System Parameter (Dynamic)

1. Go to **Settings** → **Technical** → **Parameters** → **System Parameters**
2. Create a new parameter:
   - **Key:** `event.reminder_test_mode`
   - **Value:** `True` (for test mode) or `False` (for production mode)

This allows switching modes without code changes or module upgrades.

---

## 📧 Email Templates

### Assignment Email (Email 1)

**Subject:** "You've been assigned to [Event Name] training event"

**Body includes:**
- Professional HTML formatting
- Event details table
- Event description (if available)

### Weekly Reminder Email (Email 2)

**Subject:** "Reminder: [Event Name] - One Week to Go!"

**Body includes:**
- Eye-catching orange header with "⏰ One Week to Go!"
- Warning banner highlighting the reminder
- Complete event details table
- **Full attendee report** with:
  - Numbered list of all confirmed attendees
  - Contact information (name, email, phone)
  - Registration status
  - Registration date
- Event description (if available)
- Action required notice

---

## 🧪 Testing the System

### Step 1: Enable Test Mode

Option A - Via System Parameter:
1. Go to Settings → Technical → Parameters → System Parameters
2. Create parameter: `event.reminder_test_mode` = `True`

Option B - Already configured in cron (current setup)

### Step 2: Create a Test Event

1. Go to **Events** → **Events** → **Create**
2. Fill in the required fields:
   - **Event Name:** "Test Training Event"
   - **Start Date:** Set to **10 minutes from now** (for test mode)
   - **End Date:** Set to 2 hours after start date
   - **Location:** Select or create a location
   - **Responsible:** Assign yourself or another user
   - **Trainer Tags:** Select contact tags (e.g., "Trainer", "Instructor")

3. **Save** the event

### Step 3: Verify Immediate Notification (Email 1)

After saving, check:
- Email should be sent immediately to:
  - All contacts with selected trainer tags
  - The responsible user

Check the **Chatter** (bottom of event form) for email sending logs.

### Step 4: Add Some Attendees

1. Go to **Registrations** tab
2. Click **Add a line** or **Create**
3. Add 2-3 test registrations with:
   - Name
   - Email
   - Phone
   - Confirm the registrations

### Step 5: Wait for Weekly Reminder (Email 2)

- **Test Mode:** Wait 10 minutes (cron runs every 5 minutes)
- **Production Mode:** Wait until 7 days before event

The cron job will automatically:
1. Find events in the target time window
2. Check if reminder was already sent (`is_reminder_sent` field)
3. Send reminder emails to trainers and responsible person
4. Mark the event as reminder sent

### Step 6: Verify Reminder Email

Check that the reminder email includes:
- ✅ Event details
- ✅ Number of booked attendees
- ✅ Complete attendee report table
- ✅ All attendee information

---

## 📊 Monitoring

### Check Cron Job Status

1. Go to **Settings** → **Technical** → **Automation** → **Scheduled Actions**
2. Search for "Event: Weekly Reminder Scheduler"
3. Check:
   - **Active:** Should be checked
   - **Next Execution Date:** Shows when it will run next
   - **Last Run:** Shows when it last ran

### Check Event Reminder Status

On each event form, you can see:
- **Is Reminder Sent:** Boolean field indicating if weekly reminder was sent
- **Reminder Cron:** Link to the scheduled action (if using individual event reminders)

### View Email Logs

1. Go to **Settings** → **Technical** → **Email** → **Emails**
2. Filter by:
   - **Model:** event.event
   - **Subject:** Contains "Reminder" or "assigned"

---

## 🔍 Troubleshooting

### Emails Not Being Sent

**Check 1: Email Configuration**
- Go to Settings → Technical → Email → Outgoing Mail Servers
- Verify SMTP server is configured correctly
- Test the connection

**Check 2: Cron Job**
- Verify cron is active
- Check "Next Execution Date"
- Manually run: Settings → Technical → Scheduled Actions → Select cron → "Run Manually"

**Check 3: Event Configuration**
- Verify event has `date_begin` set
- Check if `is_reminder_sent` is already True
- Verify trainer tags have contacts with email addresses
- Verify responsible user has email address

**Check 4: Logs**
- Check Odoo logs for errors
- Look for lines containing "Event" and "reminder"

### Reminder Sent Too Early/Late

**Test Mode:**
- Event should be 10 minutes from now (±5 minute window)
- Cron runs every 5 minutes

**Production Mode:**
- Event should be 7 days from now
- Cron runs every 24 hours

### Duplicate Emails

The system prevents duplicates by:
- Checking `is_reminder_sent` field before sending
- Only sending assignment emails when tags/responsible user changes
- Marking events after reminder is sent

---

## 🎓 Technical Details

### Database Fields

**event.event model:**
- `trainer_tag_ids`: Many2many to res.partner.category
- `trainer_tag_contact_ids`: Computed field - contacts with selected tags
- `is_reminder_sent`: Boolean - tracks if weekly reminder was sent
- `trainer_notified`: Boolean - tracks if trainers were notified
- `responsible_notified`: Boolean - tracks if responsible was notified
- `reminder_cron_id`: Many2one to ir.cron (for individual event reminders)

### Key Methods

**Immediate Notifications:**
- `_send_trainer_assignment_email()`: Sends to trainer tag contacts
- `_send_responsible_assignment_email()`: Sends to responsible user
- `_prepare_assignment_email_body()`: Generates Email 1 HTML

**Weekly Reminders:**
- `send_weekly_event_reminders()`: Cron job entry point
- `_send_one_week_reminder_emails()`: Sends reminder to all recipients
- `_prepare_one_week_reminder_email_body()`: Generates Email 2 HTML
- `_generate_attendee_report_html()`: Creates attendee table

### Cron Job

**ID:** `event.event_weekly_reminder_cron`
**Model:** `event.event`
**Method:** `send_weekly_event_reminders()`
**Interval:** 5 minutes (TEST) / 1 day (PRODUCTION)

---

## 📝 Best Practices

1. **Always test in TEST MODE first** before deploying to production
2. **Set up proper email server** configuration before going live
3. **Monitor the first few runs** to ensure emails are sent correctly
4. **Keep trainer tags organized** - use clear, descriptive names
5. **Train users** on how to assign trainer tags and responsible persons
6. **Review attendee data** before the reminder is sent
7. **Switch to PRODUCTION MODE** after testing is complete

---

## 🚀 Going Live Checklist

- [ ] Test mode verified working
- [ ] Email server configured and tested
- [ ] Sample events created and emails received
- [ ] Attendee reports display correctly
- [ ] Switch to PRODUCTION MODE (update cron to 1 day interval)
- [ ] Remove or set `event.reminder_test_mode` parameter to `False`
- [ ] Upgrade event module
- [ ] Restart Odoo server
- [ ] Monitor first production run
- [ ] Document any customizations

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Odoo logs for error messages
3. Verify all configuration steps were followed
4. Test with a simple event first

---

**Last Updated:** 2025-11-27
**Version:** 1.0
**Odoo Version:** 19.0

