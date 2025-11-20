# Events Clone - Odoo Module

A comprehensive event management module for Odoo that allows you to organize and manage events, registrations, and tickets.

## Features

- **Event Management**: Create and manage events with detailed information
- **Registration Tracking**: Track attendee registrations and manage participants
- **Ticket Management**: Create multiple ticket types with different pricing
- **Stage Management**: Track event progress through customizable stages
- **Tag System**: Categorize events with tags
- **Kanban View**: Visual management of events through stages
- **Email Integration**: Built-in mail tracking and activity management

## Installation

### Step 1: Add Module to Odoo

The module is already located in `custom_addons/events_clone/`. You need to make sure Odoo knows about this custom addons path.

### Step 2: Update Odoo Configuration

1. Find your Odoo configuration file (usually `odoo.conf` or passed as command-line parameter)
2. Add or update the `addons_path` parameter to include the custom_addons directory:

```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/odoo/custom_addons
```

For this installation, it should be:
```ini
addons_path = /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/addons,/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/custom_addons
```

### Step 3: Restart Odoo Server

Restart your Odoo server to load the new addons path:

```bash
# If running Odoo directly
./odoo-bin -c /path/to/odoo.conf

# Or if using a service
sudo systemctl restart odoo
```

### Step 4: Update Apps List

1. Log in to Odoo as an administrator
2. Go to **Apps** menu
3. Click on the **Update Apps List** button (you may need to activate Developer Mode first)
4. In the dialog, click **Update**

### Step 5: Install the Module

1. In the **Apps** menu, remove the "Apps" filter to see all modules
2. Search for "Events Clone"
3. Click **Install** button

## Activating Developer Mode

To access the "Update Apps List" option, you need to activate Developer Mode:

1. Go to **Settings**
2. Scroll down to the bottom
3. Click on **Activate the developer mode**

Or use this URL: `http://localhost:8069/web?debug=1`

## Usage

### Creating an Event

1. Go to **Events Clone** → **Events** → **Events**
2. Click **Create**
3. Fill in the event details:
   - Event Name
   - Start and End Dates
   - Organizer
   - Venue/Location
   - Set seat limits if needed
4. Add tickets in the **Tickets** tab
5. Save the event

### Managing Registrations

1. Go to **Events Clone** → **Events** → **Registrations**
2. Create new registrations or view existing ones
3. Confirm registrations by changing their status
4. Mark attendees as "Attended" when they arrive

### Configuration

Access configuration options under **Events Clone** → **Configuration**:

- **Stages**: Customize event stages
- **Tag Categories**: Organize tags into categories
- **Tags**: Create and manage event tags

## Module Structure

```
events_clone/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── events_clone_event.py
│   ├── events_clone_registration.py
│   ├── events_clone_ticket.py
│   ├── events_clone_stage.py
│   └── events_clone_tag.py
├── views/
│   ├── events_clone_event_views.xml
│   ├── events_clone_registration_views.xml
│   ├── events_clone_ticket_views.xml
│   ├── events_clone_stage_views.xml
│   ├── events_clone_tag_views.xml
│   └── events_clone_menu_views.xml
├── security/
│   ├── events_clone_security.xml
│   └── ir.model.access.csv
├── data/
│   └── events_clone_data.xml
└── static/
    ├── description/
    │   ├── icon.png
    │   └── index.html
    └── src/
        └── scss/
            └── events_clone.scss
```

## Troubleshooting

### Module Not Appearing in Apps List

1. Make sure the `addons_path` in your configuration includes the `custom_addons` directory
2. Restart the Odoo server
3. Update the Apps List from the Apps menu
4. Check the Odoo logs for any errors

### Permission Errors

Make sure the Odoo user has read permissions on the custom_addons directory:

```bash
chmod -R 755 custom_addons/events_clone
```

## Support

For issues or questions, please check the Odoo logs located typically at:
- `/var/log/odoo/odoo-server.log` (Linux)
- Or check the console output if running Odoo directly

## License

LGPL-3

