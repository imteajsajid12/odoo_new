# Events Clone - Quick Installation Guide

## Prerequisites
- Odoo instance running at http://localhost:8069
- Administrator access to Odoo
- Access to Odoo configuration file

## Installation Steps

### 1. Configure Odoo to Recognize Custom Addons

**Option A: Using Configuration File**

Edit your Odoo configuration file (usually `odoo.conf`):

```bash
# Find the configuration file
cd /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo

# Edit the configuration file
nano odoo.conf  # or use your preferred editor
```

Add or modify the `addons_path` line:

```ini
[options]
addons_path = /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/addons,/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/custom_addons
```

**Option B: Using Command Line**

When starting Odoo, add the custom_addons path:

```bash
./odoo-bin --addons-path=/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/addons,/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/custom_addons
```

### 2. Restart Odoo Server

```bash
# Stop the current Odoo process (Ctrl+C if running in terminal)
# Then restart with the updated configuration

# If using odoo-bin directly:
./odoo-bin -c odoo.conf

# If using systemd service:
sudo systemctl restart odoo
```

### 3. Activate Developer Mode

1. Open your browser and go to: http://localhost:8069
2. Log in as Administrator
3. Go to **Settings** (gear icon in the top menu)
4. Scroll to the bottom of the page
5. Click **Activate the developer mode**

**Quick Method**: Navigate to http://localhost:8069/web?debug=1

### 4. Update Apps List

1. Click on the **Apps** icon in the main menu
2. Click the **⋮** (three dots) menu in the top-right
3. Select **Update Apps List**
4. Click **Update** in the confirmation dialog
5. Wait for the update to complete

### 5. Install Events Clone Module

1. In the **Apps** menu, click the **Filters** dropdown
2. Remove the "Apps" filter (click the ✕ on the "Apps" filter chip)
3. In the search bar, type: **Events Clone**
4. You should see the "Events Clone" module
5. Click the **Install** button

### 6. Verify Installation

After installation completes:

1. You should see a new menu item **Events Clone** in the main menu bar
2. Click on **Events Clone** → **Events** → **Events**
3. You should see the events list view
4. Try creating a test event to verify everything works

## Accessing the Module

Once installed, access the module at:
- **URL**: http://localhost:8069/odoo/events-clone
- **Menu**: Events Clone → Events → Events

## Default Data

The module comes with pre-configured:
- **5 Event Stages**: New, Confirmed, In Progress, Done, Cancelled
- **2 Tag Categories**: Event Type, Topic
- **7 Event Tags**: Conference, Seminar, Workshop, Training, Technology, Business, Marketing

## User Permissions

Two user groups are created:
- **Events Clone User**: Can create and manage events
- **Events Clone Administrator**: Full access including configuration

To assign permissions:
1. Go to **Settings** → **Users & Companies** → **Users**
2. Select a user
3. In the **Access Rights** tab, find **Events Clone** section
4. Assign appropriate role

## Troubleshooting

### Module Not Visible in Apps List

**Check 1**: Verify addons path
```bash
cd /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo
ls -la custom_addons/events_clone/
```

**Check 2**: Check Odoo logs for errors
```bash
# Look for errors related to events_clone
tail -f /var/log/odoo/odoo-server.log
# Or check console output if running odoo-bin directly
```

**Check 3**: Verify file permissions
```bash
chmod -R 755 custom_addons/events_clone
```

### Installation Fails

1. Check the error message in the Odoo interface
2. Common issues:
   - Missing dependencies (barcodes, mail, portal, utm)
   - Syntax errors in XML files
   - Database permission issues

3. Check Odoo logs for detailed error information

### Module Installed but Menu Not Showing

1. Refresh the browser (Ctrl+F5 or Cmd+Shift+R)
2. Clear browser cache
3. Log out and log back in
4. Verify you have the correct permissions

## Next Steps

After successful installation:

1. **Create Event Stages** (if you want custom stages)
   - Go to Events Clone → Configuration → Stages

2. **Create Tag Categories and Tags**
   - Go to Events Clone → Configuration → Tag Categories

3. **Create Your First Event**
   - Go to Events Clone → Events → Events
   - Click Create
   - Fill in event details
   - Add tickets
   - Save

4. **Test Registration Flow**
   - Create a test registration
   - Confirm the registration
   - Mark as attended

## Support

For issues:
1. Check the README.md file in the module directory
2. Review Odoo logs
3. Verify all dependencies are installed
4. Ensure database is properly configured

## Quick Command Reference

```bash
# Navigate to Odoo directory
cd /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo

# Start Odoo with custom addons
./odoo-bin --addons-path=addons,custom_addons

# Update module (after code changes)
./odoo-bin -u events_clone -d your_database_name

# Check module structure
tree custom_addons/events_clone/
```

