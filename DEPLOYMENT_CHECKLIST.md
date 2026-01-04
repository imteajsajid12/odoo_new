# Event Module Deployment Checklist

## ✅ What Was Done

### 1. Module Version Update
- ✅ Bumped version from 1.9 to 1.10
- ✅ Updated module description with new features
- ✅ File: `addons/event/__manifest__.py`

### 2. Documentation Created
- ✅ **EVENT_EMAIL_NOTIFICATION_DOCUMENTATION.md** - Complete technical documentation
- ✅ **INSTALLATION_GUIDE.md** - Installation and upgrade guide for new PC
- ✅ **README_EMAIL_SYSTEM.md** - Quick start guide
- ✅ **TEST_EMAIL_VERIFICATION.md** - Testing procedures and checklists
- ✅ **DEPLOYMENT_CHECKLIST.md** - This file

### 3. Git Commit & Push
- ✅ All changes committed to git
- ✅ Pushed to GitHub repository (branch: v1.0)
- ✅ Commit hash: c435046f

## 🚀 How to Deploy on New PC

### Quick Steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/imteajsajid12/odoo_new.git
   cd odoo_new
   git checkout v1.0
   ```

2. **Upgrade the Event module**:
   ```bash
   # Method 1: Command line (recommended)
   ./odoo-bin -d your_database_name -u event --stop-after-init
   
   # Method 2: UI
   # Apps → Events Organization → Upgrade
   ```

3. **Verify installation**:
   - Open Events module
   - Create new event
   - Check for "Trainers" and "Responsible" fields
   - Test email notifications

### Detailed Steps:
See **INSTALLATION_GUIDE.md** for complete instructions.

## 🔍 What Will Appear After Upgrade

### In Event Form:
- ✅ **Trainers** field (Many2many tags for contact categories)
- ✅ Contact count below trainer tags
- ✅ **Responsible** field (already existed, but now used for emails)

### Email Notifications:
- ✅ **Email 1**: Sent immediately when event is created
  - To: Trainer tag contacts + Responsible user
  - Subject: "You've been assigned to [Event] training event"
  
- ✅ **Email 2**: Sent 4-5 minutes later (test mode) or 1 week before (production)
  - To: Same recipients
  - Subject: "Reminder: [Event] - One Week to Go!"
  - Includes: Attendee report with names, emails, phones, status

### Backend Features:
- ✅ Scheduled actions created automatically (ir.cron)
- ✅ Email tracking in Settings → Technical → Email → Emails
- ✅ Comprehensive logging for debugging

## ⚙️ Configuration Required

### 1. Email Server (Required)
```
Settings → Technical → Outgoing Mail Servers
- Configure SMTP server
- Test connection
```

### 2. Contact Tags (Required)
```
Contacts → Configuration → Contact Tags
- Create tags (e.g., "my_contact", "trainers", etc.)
- Assign tags to contacts who should receive emails
```

### 3. User Emails (Required)
```
Settings → Users & Companies → Users
- Ensure all users have valid email addresses
- These users can be assigned as "Responsible"
```

### 4. Production Mode (Optional - for live use)
```
Edit: addons/event/models/event_event.py
Line: 1901
Change: timedelta(minutes=1) → timedelta(days=7)
Restart Odoo
```

## 🧪 Testing Checklist

After deployment on new PC:

### Installation Verification:
- [ ] Module version shows 1.10 (Apps → Events Organization)
- [ ] Trainer Tags field visible in event form
- [ ] Responsible field visible in event form
- [ ] Contact count shows below trainer tags
- [ ] No errors in Odoo logs

### Functional Testing:
- [ ] Create test event with trainer tags
- [ ] Create test event with responsible user
- [ ] Save event successfully
- [ ] Check immediate email sent (Settings → Technical → Email → Emails)
- [ ] Verify scheduled action created (Settings → Technical → Automation → Scheduled Actions)
- [ ] Wait 4-5 minutes
- [ ] Verify reminder email sent
- [ ] Check email content and formatting
- [ ] Verify scheduled action deactivated after reminder

### Email Content Verification:
- [ ] Email 1 contains: Event name, date, times, location, responsible, max attendees
- [ ] Email 2 contains: All Email 1 info + attendee count + attendee report
- [ ] Emails are HTML formatted and professional
- [ ] All recipients received emails

## 🐛 Common Issues & Solutions

### Issue 1: Fields Not Showing
**Problem**: Trainer tags and responsible fields not visible after upgrade

**Solution**:
```bash
# Clear cache and force upgrade
./odoo-bin -d DB -u event --stop-after-init --dev=all

# Clear browser cache
# Restart Odoo
```

### Issue 2: No Emails Sent
**Problem**: Event created but no emails in queue

**Solution**:
- Check email server configuration
- Verify contacts have valid emails
- Check trainer tags are assigned to contacts
- Review logs: `tail -f odoo.log | grep Event`

### Issue 3: Module Version Not Updated
**Problem**: Still shows version 1.9

**Solution**:
```bash
# Update module list
./odoo-bin shell -d DB
self.env['ir.module.module'].update_list()
exit()

# Upgrade again
./odoo-bin -d DB -u event --stop-after-init
```

## 📊 Database Changes

The following fields are automatically added to `event_event` table on upgrade:

| Field | Type | Purpose |
|-------|------|---------|
| `trainer_tag_ids` | Many2many | Store selected contact tags |
| `is_reminder_sent` | Boolean | Track if reminder was sent |
| `trainer_notified` | Boolean | Track if trainers were notified |
| `responsible_notified` | Boolean | Track if responsible was notified |
| `reminder_cron_id` | Many2one | Link to scheduled action |

**Note**: Odoo ORM handles all database schema updates automatically during module upgrade.

## 🎯 Success Criteria

Deployment is successful when:

1. ✅ Module version is 1.10
2. ✅ All new fields visible in UI
3. ✅ Email 1 sent on event creation
4. ✅ Scheduled action created
5. ✅ Email 2 sent after configured time
6. ✅ No errors in logs
7. ✅ All documentation accessible

## 📞 Support Resources

- **Installation Guide**: INSTALLATION_GUIDE.md
- **Testing Guide**: TEST_EMAIL_VERIFICATION.md
- **Quick Start**: README_EMAIL_SYSTEM.md
- **Technical Docs**: EVENT_EMAIL_NOTIFICATION_DOCUMENTATION.md

## 🎉 Ready to Deploy!

All changes have been committed and pushed to GitHub.
Follow the INSTALLATION_GUIDE.md on your new PC to get started.

**Repository**: https://github.com/imteajsajid12/odoo_new.git  
**Branch**: v1.0  
**Commit**: c435046f

