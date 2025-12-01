# Event Module Installation & Upgrade Guide

## 🎯 Purpose
This guide explains how to install or upgrade the Event module with custom email notification features on a new PC or fresh Odoo installation.

## ⚠️ Important: Why You Need This Guide

When you clone this repository to a new PC, the custom changes (trainer tags, responsible user, email notifications) won't automatically appear in Odoo. You need to:

1. **Upgrade the module** if it's already installed
2. **Install the module** if it's a fresh database
3. **Update the database** to apply schema changes

## 📋 Prerequisites

- Odoo 17.0 or compatible version installed
- Git repository cloned to your PC
- Database created (or existing database)
- Admin access to Odoo

## 🚀 Installation Steps

### Option 1: Fresh Installation (New Database)

#### Step 1: Clone the Repository
```bash
cd /path/to/your/workspace
git clone <your-repository-url>
cd odoo
```

#### Step 2: Start Odoo with Addons Path
```bash
# Make sure Odoo can find the event module
./odoo-bin --addons-path=addons --database=your_database_name
```

#### Step 3: Install the Event Module
1. Open Odoo in browser: `http://localhost:8069`
2. Login as admin
3. Go to **Apps** menu
4. Remove the "Apps" filter to see all modules
5. Search for "Events Organization"
6. Click **Install**

#### Step 4: Verify Installation
1. Go to **Events** menu
2. Create a new event
3. Check if you see:
   - ✅ **Trainers** field (with tag selection)
   - ✅ **Responsible** field (user selection)
   - ✅ Contact count below trainer tags

### Option 2: Upgrade Existing Installation

#### Step 1: Pull Latest Changes
```bash
cd /path/to/your/odoo
git pull origin main  # or your branch name
```

#### Step 2: Enable Developer Mode
1. Go to Settings
2. Scroll to bottom
3. Click **Activate the developer mode**

#### Step 3: Upgrade the Module (Method A - UI)
1. Go to **Apps** menu
2. Remove the "Apps" filter
3. Search for "Events Organization"
4. Click the **⋮** (three dots) menu
5. Click **Upgrade**
6. Wait for upgrade to complete

#### Step 4: Upgrade the Module (Method B - Command Line)
```bash
# Stop Odoo if running
# Then run upgrade command
./odoo-bin -d your_database_name -u event --stop-after-init

# Restart Odoo normally
./odoo-bin --addons-path=addons --database=your_database_name
```

#### Step 5: Verify Upgrade
1. Go to **Events** menu
2. Create a new event or open existing event
3. Verify new fields are visible:
   - ✅ **Trainers** field
   - ✅ **Responsible** field
   - ✅ Contact count

### Option 3: Force Module Update (If Upgrade Doesn't Work)

#### Step 1: Update Module List
```bash
# In Odoo shell or command line
./odoo-bin shell -d your_database_name

# In the shell:
self.env['ir.module.module'].update_list()
exit()
```

#### Step 2: Upgrade with Force
```bash
./odoo-bin -d your_database_name -u event --stop-after-init --dev=all
```

## 🔍 Troubleshooting

### Issue 1: Fields Not Showing After Upgrade

**Symptoms**: Trainer tags and Responsible fields not visible in event form

**Solution**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Restart Odoo server
3. Upgrade module again
4. Check if view is customized (Settings → Technical → User Interface → Views)

**Command to force view update**:
```bash
./odoo-bin -d your_database_name -u event --stop-after-init --dev=all
```

### Issue 2: Module Version Not Updated

**Symptoms**: Module still shows old version (1.9 instead of 1.10)

**Solution**:
```bash
# Update module list
./odoo-bin shell -d your_database_name
self.env['ir.module.module'].update_list()
exit()

# Then upgrade
./odoo-bin -d your_database_name -u event --stop-after-init
```

### Issue 3: Database Schema Not Updated

**Symptoms**: Error when trying to save event with new fields

**Solution**:
```bash
# Force schema update
./odoo-bin -d your_database_name -u event --stop-after-init --dev=all

# If still not working, check database directly
psql your_database_name
\d event_event
# Look for columns: trainer_tag_ids, is_reminder_sent, etc.
```

### Issue 4: Email Notifications Not Working

**Symptoms**: Events created but no emails sent

**Solution**:
1. Check email server configuration (Settings → Technical → Outgoing Mail Servers)
2. Verify scheduled actions are created (Settings → Technical → Automation → Scheduled Actions)
3. Check logs for errors: `tail -f /var/log/odoo/odoo.log | grep Event`

## 📊 Verification Checklist

After installation/upgrade, verify:

- [ ] Event module version is 1.10 (Apps → Events Organization → Version)
- [ ] Trainer Tags field visible in event form
- [ ] Responsible field visible in event form
- [ ] Contact count shows below trainer tags
- [ ] Can create event with trainer tags
- [ ] Can create event with responsible user
- [ ] Email sent immediately on event creation
- [ ] Scheduled action created for reminder
- [ ] Reminder email sent after 4-5 minutes (test mode)

## 🗄️ Database Fields Added

The following fields are added to `event.event` model:

| Field Name | Type | Description |
|------------|------|-------------|
| `trainer_tag_ids` | Many2many | Contact tags for trainers |
| `trainer_tag_contact_ids` | Many2many (computed) | Contacts with selected tags |
| `trainer_tag_contact_count` | Integer (computed) | Count of contacts |
| `is_reminder_sent` | Boolean | Flag for reminder email status |
| `trainer_notified` | Boolean | Flag for trainer notification |
| `responsible_notified` | Boolean | Flag for responsible notification |
| `reminder_cron_id` | Many2one | Reference to scheduled action |

## 🔧 Manual Database Update (Advanced)

If automatic upgrade fails, you can manually verify database:

```sql
-- Connect to database
psql your_database_name

-- Check if columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'event_event' 
AND column_name IN ('is_reminder_sent', 'trainer_notified', 'responsible_notified');

-- If columns don't exist, Odoo should create them on upgrade
-- DO NOT manually create columns - let Odoo handle it
```

## 📝 Post-Installation Configuration

### 1. Configure Email Server
```
Settings → Technical → Outgoing Mail Servers
- SMTP Server: your.smtp.server
- SMTP Port: 587 (or 465 for SSL)
- Username: your_email@example.com
- Password: your_password
- Test Connection
```

### 2. Create Contact Tags
```
Contacts → Configuration → Contact Tags
- Create tag: "my_contact" (or your preferred name)
- Assign tag to contacts who should receive trainer emails
```

### 3. Set Responsible Users
```
Settings → Users & Companies → Users
- Ensure users have valid email addresses
- Assign users as responsible in events
```

### 4. Test the System
```
1. Create test event
2. Select trainer tags
3. Select responsible user
4. Save event
5. Check emails (Settings → Technical → Email → Emails)
6. Wait 4-5 minutes
7. Verify reminder email sent
```

## 🌐 Production Deployment

### Before Going Live:

1. **Switch to Production Mode** (7 days before event):
   - Edit `addons/event/models/event_event.py` line 1901
   - Change `timedelta(minutes=1)` to `timedelta(days=7)`
   - Restart Odoo

2. **Test Thoroughly**:
   - Create multiple test events
   - Verify all emails sent
   - Check email content and formatting
   - Test with different trainer tags
   - Test with different responsible users

3. **Monitor Logs**:
   ```bash
   tail -f /var/log/odoo/odoo.log | grep Event
   ```

## 📞 Support

If you encounter issues:

1. Check Odoo logs for errors
2. Verify module version (should be 1.10)
3. Clear browser cache and restart Odoo
4. Try force upgrade: `./odoo-bin -d DB -u event --stop-after-init --dev=all`
5. Check database schema for new columns

## 🎉 Success!

Once you see the Trainer Tags and Responsible fields in the event form, the installation is complete!

Create a test event to verify email notifications are working.

