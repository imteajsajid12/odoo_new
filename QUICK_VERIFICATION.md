# Quick Verification Checklist

## ✅ Implementation Status

### Code Changes
- [x] Modified `_create_reminder_scheduled_action()` method
- [x] Changed reminder delay from 7 days to 1 minute
- [x] Updated docstrings to indicate TEST MODE
- [x] Server restarted with new code

### Testing Tools Created
- [x] `EVENT_EMAIL_TESTING_GUIDE.md` - Comprehensive testing guide
- [x] `test_event_email.py` - Automated test script
- [x] `monitor_event_emails.sh` - Real-time log monitor
- [x] `IMPLEMENTATION_SUMMARY.md` - Complete documentation

## 🧪 How to Verify the System is Working

### Step 1: Check Server Status
```bash
# Check if Odoo is running
ps aux | grep odoo-bin | grep -v grep

# Expected: Should show a running process
```

### Step 2: Create a Test Event

1. **Open Browser**: http://localhost:8069/odoo/events/new

2. **Fill in Event Details**:
   - Event Name: "Email Test - [Your Name]"
   - Start Date: **TOMORROW** (very important - must be future date)
   - End Date: Tomorrow + 2 hours
   - Responsible: Select yourself or any user with email
   - Trainer Tags: Select "Trainer" or any available tag

3. **Save the Event**

### Step 3: Verify Immediate Emails

**Check the terminal where Odoo is running** (Terminal ID 38)

Look for these log entries:
```
Event [Event Name]: _send_trainer_assignment_email called
Event [Event Name]: Sent assignment emails to X trainer tag contacts
Event [Event Name]: _send_responsible_assignment_email called
Event [Event Name]: Sent assignment email to responsible user
Event [Event Name]: TEST MODE - Reminder scheduled for 1 minute from now
```

### Step 4: Wait 1 Minute

**Set a timer for 70 seconds** and watch the terminal.

Look for these log entries:
```
_send_event_reminder called for event ID: X
Event [Event Name]: Sending reminder emails (TEST MODE - 1 minute delay)
Event [Event Name]: Sent one-week reminder to X trainers
Event [Event Name]: Sent one-week reminder to responsible user
```

### Step 5: Verify in Odoo UI

1. **Check Scheduled Actions**:
   - Go to: Settings → Technical → Automation → Scheduled Actions
   - Search for: "Event Reminder"
   - You should see your event's scheduled action

2. **Check Emails**:
   - Go to: Settings → Technical → Email → Emails
   - Filter by your event name
   - You should see multiple emails with status "Sent"

3. **Check Your Email Inbox**:
   - Check the email address of the Responsible user
   - Check the email addresses of contacts with trainer tags
   - You should receive 2 emails per recipient:
     - Assignment email (immediate)
     - Reminder email (after 1 minute)

## 📊 Expected Timeline

```
Time 0:00 - Event Created
    ↓
    Immediate emails sent to:
    - Responsible user
    - Trainer tag contacts
    ↓
    Scheduled action created
    ↓
Time 1:00 - Scheduled action triggers
    ↓
    Reminder emails sent to:
    - Responsible user
    - Trainer tag contacts
    ↓
    Scheduled action deactivated
```

## 🎯 Success Criteria

### ✅ System is Working If:
1. Immediate emails are sent when event is created
2. Scheduled action is created with nextcall = ~1 minute from now
3. After 1 minute, reminder emails are sent
4. All emails show status "Sent" in Odoo
5. Recipients receive emails in their inbox

### ❌ System Needs Debugging If:
1. No emails are sent on event creation
2. No scheduled action is created
3. Reminder emails are not sent after 1 minute
4. Emails show status "Exception" or "Error"

## 🔍 Debugging Commands

```bash
# Check if Odoo is running
ps aux | grep odoo-bin

# Monitor logs in real-time
./monitor_event_emails.sh

# Check recent log entries (if log file exists)
tail -100 odoo.log | grep Event

# Check Python processes
ps aux | grep python | grep odoo
```

## 📧 Email Server Configuration

**Important**: Make sure Odoo has a working email server configured.

To check:
1. Go to: Settings → Technical → Email → Outgoing Mail Servers
2. Verify at least one server is configured
3. Test the connection

If no email server is configured, emails will be queued but not sent.

## 🎬 Demo Video Script

If you want to record a demo:

1. **Start**: Show the event creation form
2. **Create**: Fill in event details with future date
3. **Save**: Click save and show the terminal logs
4. **Verify**: Show immediate emails in Odoo UI
5. **Wait**: Set timer for 1 minute
6. **Show**: Display reminder emails after 1 minute
7. **Inbox**: Show actual emails received

## 📝 Notes

- **Test Mode**: Currently set to 1 minute delay
- **Production Mode**: Change to 7 days before deployment
- **Email Content**: Professional HTML with event details
- **Auto-cleanup**: Scheduled actions are deactivated after running

## ✨ Key Features Demonstrated

1. **Automatic Email Sending**: No manual intervention needed
2. **Multiple Recipients**: Supports both responsible user and trainer tag contacts
3. **Scheduled Reminders**: Uses Odoo's cron system
4. **Professional Emails**: HTML formatted with event details
5. **Robust Error Handling**: Comprehensive logging and error handling

---

**Last Updated**: 2025-11-27  
**Status**: ✅ Ready for Testing  
**Next Action**: Create a test event and verify emails are sent

