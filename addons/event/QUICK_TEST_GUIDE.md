# Quick Test Guide - Event Notification System

## 🚀 Quick Start (5 Minutes)

This guide will help you test the event notification system in **5 minutes**.

---

## ✅ Prerequisites

- Odoo server is running on `http://localhost:8069`
- You have admin access
- Email server is configured (or check logs for email content)

---

## 📝 Step-by-Step Testing

### Step 1: Enable Test Mode (Optional - Already Configured)

The system is already configured in TEST MODE:
- Cron runs every **5 minutes**
- Looks for events **10 minutes** from now

To verify:
1. Go to **Settings** → **Technical** → **Automation** → **Scheduled Actions**
2. Search for "Event: Weekly Reminder Scheduler"
3. Verify:
   - **Interval Number:** 5
   - **Interval Unit:** Minutes
   - **Active:** ✓ Checked

---

### Step 2: Create Trainer Tags (If Not Exists)

1. Go to **Contacts** → **Configuration** → **Contact Tags**
2. Create a tag called **"Trainer"**
3. Save

---

### Step 3: Assign Trainer Tag to a Contact

1. Go to **Contacts** → **Contacts**
2. Select or create a contact (use your email for testing)
3. In the **Tags** field, add **"Trainer"**
4. Make sure the contact has a valid **Email** address
5. Save

---

### Step 4: Create a Test Event

1. Go to **Events** → **Events** → **Create**

2. Fill in the details:
   ```
   Event Name: Test Training - Email Notification
   Start Date: [Current time + 10 minutes]
   End Date: [Current time + 2 hours]
   Location: Select any location or create "Test Location"
   Responsible: Select yourself or another user with email
   Trainer Tags: Select "Trainer" tag
   ```

3. **Important:** Set the start date to **exactly 10 minutes from now**
   - Example: If current time is 10:00 AM, set start date to 10:10 AM

4. Click **Save**

---

### Step 5: Verify Immediate Notification (Email 1)

**Expected Result:** Email should be sent immediately after saving

**Check 1: Chatter**
- Scroll to the bottom of the event form
- Look in the **Chatter** section
- You should see messages like:
  - "Assignment email sent to trainer: [Contact Name]"
  - "Assignment email sent to responsible user: [User Name]"

**Check 2: Email Logs**
1. Go to **Settings** → **Technical** → **Email** → **Emails**
2. Look for emails with subject: "You've been assigned to Test Training - Email Notification training event"
3. Click to view the email content

**Check 3: Your Inbox**
- Check your email inbox
- You should receive the assignment email

---

### Step 6: Add Test Attendees

1. On the event form, go to **Registrations** tab
2. Click **Add a line** or **Create**
3. Add 2-3 registrations:
   ```
   Registration 1:
   - Name: John Doe
   - Email: john@example.com
   - Phone: +1234567890
   - State: Confirmed
   
   Registration 2:
   - Name: Jane Smith
   - Email: jane@example.com
   - Phone: +0987654321
   - State: Confirmed
   ```
4. Save

---

### Step 7: Wait for Weekly Reminder (Email 2)

**Timeline:**
- Cron runs every **5 minutes**
- Looks for events **10 minutes** from now (±5 minute window)
- So if you created event at 10:00 AM for 10:10 AM:
  - Cron will run at 10:00, 10:05, 10:10, etc.
  - Email should be sent around 10:00-10:05 AM

**What to do:**
1. Wait 5-10 minutes
2. Refresh the event form
3. Check the **Is Reminder Sent** field - it should be checked ✓

---

### Step 8: Verify Weekly Reminder Email

**Check 1: Chatter**
- Look for message: "One-week reminder emails sent successfully"

**Check 2: Email Logs**
1. Go to **Settings** → **Technical** → **Email** → **Emails**
2. Look for emails with subject: "Reminder: Test Training - Email Notification - One Week to Go!"
3. Click to view the email content
4. **Verify the email includes:**
   - ✅ Event details (title, date, time, location)
   - ✅ Number of booked attendees (should show "2")
   - ✅ **Attendee report table** with:
     - John Doe's details
     - Jane Smith's details
     - Email addresses
     - Phone numbers
     - Registration dates

**Check 3: Your Inbox**
- Check your email inbox
- You should receive the reminder email with the attendee report

---

### Step 9: Verify Cron Job Execution

1. Go to **Settings** → **Technical** → **Automation** → **Scheduled Actions**
2. Search for "Event: Weekly Reminder Scheduler"
3. Check:
   - **Last Run:** Should show recent timestamp
   - **Next Execution Date:** Should show next 5-minute interval

**Manual Test:**
- Click **Run Manually** button to trigger the cron immediately
- Check if emails are sent

---

## 🎯 Expected Results Summary

| Test | Expected Result | How to Verify |
|------|----------------|---------------|
| **Email 1 - Trainer** | Sent immediately when event is saved | Check Chatter, Email logs, Inbox |
| **Email 1 - Responsible** | Sent immediately when event is saved | Check Chatter, Email logs, Inbox |
| **Email 2 - Reminder** | Sent 10 minutes before event (±5 min) | Check after 5-10 minutes |
| **Attendee Report** | Included in Email 2 with all details | View email content |
| **Is Reminder Sent** | Checked after reminder is sent | Event form field |
| **Cron Execution** | Runs every 5 minutes | Scheduled Actions page |

---

## 🔍 Troubleshooting

### Problem: No emails received

**Solution 1: Check Email Server**
- Go to **Settings** → **Technical** → **Email** → **Outgoing Mail Servers**
- Click **Test Connection**

**Solution 2: Check Email Logs**
- Go to **Settings** → **Technical** → **Email** → **Emails**
- Look for failed emails
- Check error messages

**Solution 3: Check Odoo Logs**
- Look in terminal/console where Odoo is running
- Search for lines containing "Event" and "email"

### Problem: Reminder not sent after 10 minutes

**Check 1: Event Date**
- Make sure event start date is exactly 10 minutes from now
- The cron looks for events in a ±5 minute window

**Check 2: Is Reminder Sent**
- Check if `is_reminder_sent` is already True
- If yes, the system won't send duplicate emails

**Check 3: Cron Active**
- Verify cron is active in Scheduled Actions
- Try running manually

### Problem: Attendee report not showing

**Check 1: Registrations**
- Make sure you added registrations to the event
- Verify registrations are in "Confirmed" state

**Check 2: Email Content**
- View the email in Email logs
- The attendee report should be in HTML table format

---

## 📊 What Each Email Should Look Like

### Email 1: Assignment Notification

```
Subject: You've been assigned to Test Training - Email Notification training event

Body:
┌─────────────────────────────────────────────┐
│ You've been assigned to Test Training -    │
│ Email Notification training event          │
├─────────────────────────────────────────────┤
│ Training Event Title: Test Training -      │
│                       Email Notification    │
│ Training Date:        Nov 27, 2025          │
│ Event Start Time:     10:10 AM              │
│ Event End Time:       12:10 PM              │
│ Location:             Test Location         │
│ Responsible Person:   Admin User            │
│ Max Attendees:        Unlimited             │
└─────────────────────────────────────────────┘
```

### Email 2: Weekly Reminder

```
Subject: Reminder: Test Training - Email Notification - One Week to Go!

Body:
┌─────────────────────────────────────────────┐
│ ⏰ One Week to Go!                          │
├─────────────────────────────────────────────┤
│ Training Event Title: Test Training -      │
│                       Email Notification    │
│ Training Date:        Nov 27, 2025          │
│ Event Start Time:     10:10 AM              │
│ Event End Time:       12:10 PM              │
│ Location:             Test Location         │
│ Responsible Person:   Admin User            │
│ Booked Attendees:     2                     │
├─────────────────────────────────────────────┤
│ ATTENDEE REPORT:                            │
│                                             │
│ 1. John Doe                                 │
│    Email: john@example.com                  │
│    Phone: +1234567890                       │
│    Status: Confirmed                        │
│    Registered: Nov 27, 2025                 │
│                                             │
│ 2. Jane Smith                               │
│    Email: jane@example.com                  │
│    Phone: +0987654321                       │
│    Status: Confirmed                        │
│    Registered: Nov 27, 2025                 │
└─────────────────────────────────────────────┘
```

---

## ✨ Success Criteria

You've successfully tested the system if:

- ✅ Email 1 sent immediately to trainers
- ✅ Email 1 sent immediately to responsible user
- ✅ Email 2 sent 10 minutes before event
- ✅ Attendee report included in Email 2
- ✅ All email fields populated correctly
- ✅ Cron job running every 5 minutes
- ✅ No duplicate emails sent

---

## 🚀 Next Steps

After successful testing:

1. **Switch to Production Mode:**
   - Edit `addons/event/data/ir_cron_data.xml`
   - Change interval to 1 day
   - Upgrade module: `./odoo-venv/bin/python3 ./odoo-bin --config=./odoo.conf -u event --stop-after-init`

2. **Configure Email Server:**
   - Set up proper SMTP server for production
   - Test email delivery

3. **Train Users:**
   - Show them how to assign trainer tags
   - Explain the two-email flow

4. **Monitor:**
   - Check first few production runs
   - Review email logs regularly

---

**Happy Testing! 🎉**

