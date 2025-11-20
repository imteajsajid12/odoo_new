# Events Clone - Email Functionality Documentation

## 🎉 Feature Overview

The Events Clone module now includes a comprehensive email functionality that allows you to send emails to contacts based on their tags. This feature is fully integrated with Odoo's mail system and follows best practices for email communication.

---

## ✨ Features Implemented

### 1. **Contact Tag Selection**
- **Field**: `contact_tag_ids` (Many2many to `res.partner.category`)
- **Location**: Event form view → "Email Communication" tab
- **Purpose**: Select one or more contact tags to filter recipients for email communication
- **Behavior**: Only active contacts with valid email addresses and matching tags will receive emails

### 2. **Send Email Button**
- **Location**: Event form view → Button box (top right, next to Registrations button)
- **Icon**: Envelope icon (fa-envelope)
- **Action**: Opens the email composer wizard modal

### 3. **Email Composer Wizard**
The wizard provides a complete email composition interface with:

#### **Fields:**
- **Event**: Display of the current event (readonly)
- **Contact Tags**: Multi-select dropdown to choose recipient tags
- **Recipient Count**: Shows the number of active contacts that will receive the email
- **Subject**: Email subject line (required, auto-populated with "Invitation: [Event Name]")
- **Message**: Rich HTML editor for email body (required)
- **Recipients Tab**: Displays the full list of recipients with their details

#### **Recipient Filtering:**
- ✅ Only **active** contacts (`active=True`)
- ✅ Only contacts with **valid email addresses** (`email != False`)
- ✅ Only contacts that have **at least one of the selected tags**
- ✅ Real-time recipient count updates as you select/deselect tags

#### **Email Sending:**
- Sends individual emails to each recipient
- Uses Odoo's `mail.mail` system for reliable delivery
- Logs activity on the event record for tracking
- Shows success notification with recipient count
- Keeps email records for audit trail (`auto_delete=False`)

---

## 📋 How to Use

### Step-by-Step Guide:

1. **Navigate to an Event**
   - Go to: Events Clone → Events → Events
   - Open an existing event or create a new one

2. **Select Contact Tags**
   - Click on the "Email Communication" tab
   - In the "Contact Selection" section, click on the "Contact Tags" field
   - Select one or more contact tags (e.g., "VIP Customers", "Newsletter Subscribers")
   - Save the event

3. **Compose and Send Email**
   - Click the "Send Email" button in the top right (envelope icon)
   - The wizard will open with:
     - Pre-selected contact tags from the event
     - Auto-generated subject line
   - Review or modify the contact tags if needed
   - Check the "Recipient Count" to see how many contacts will receive the email
   - Write your email subject (or use the default)
   - Compose your message in the HTML editor
   - Click the "Recipients" tab to review the full list of recipients
   - Click "Send Email" to send

4. **Verify Email Sent**
   - A success notification will appear showing the number of emails sent
   - Check the event's chatter/activity log for the email sending record

---

## 🔧 Technical Implementation

### Files Created/Modified:

#### **New Files:**
1. `custom_addons/events_clone/wizard/__init__.py`
   - Wizard module initialization

2. `custom_addons/events_clone/wizard/events_clone_email_wizard.py`
   - TransientModel for email composition
   - Recipient filtering logic
   - Email sending functionality

3. `custom_addons/events_clone/wizard/events_clone_email_wizard_views.xml`
   - Wizard form view
   - Action window definition

#### **Modified Files:**
1. `custom_addons/events_clone/models/events_clone_event.py`
   - Added `contact_tag_ids` field
   - Added `action_send_email()` method

2. `custom_addons/events_clone/views/events_clone_event_views.xml`
   - Added "Send Email" button to button box
   - Added "Email Communication" tab with contact tags field

3. `custom_addons/events_clone/__init__.py`
   - Imported wizard module

4. `custom_addons/events_clone/__manifest__.py`
   - Added wizard view file to data list

5. `custom_addons/events_clone/security/ir.model.access.csv`
   - Added access rights for wizard model

---

## 🛡️ Security & Validation

### Access Rights:
- **Events Clone User**: Can create and send emails
- **Events Clone Administrator**: Full access to email functionality

### Validation Rules:
1. **No Recipients Check**: Prevents sending emails when no recipients are found
2. **Required Fields**: Subject and message body are mandatory
3. **Active Contacts Only**: Automatically filters out inactive contacts
4. **Email Address Required**: Only contacts with valid email addresses are included

### Error Messages:
- "No recipients found. Please select contact tags that have associated contacts with email addresses."
- "Subject and message body are required."
- "No active recipients with email addresses found."

---

## 📊 Database Schema

### New Field in `events.clone.event`:
```python
contact_tag_ids = fields.Many2many(
    'res.partner.category',
    'events_clone_event_partner_category_rel',
    'event_id',
    'category_id',
    string='Contact Tags'
)
```

### New Model: `events.clone.email.wizard`
- **Type**: TransientModel (temporary data, auto-deleted after use)
- **Fields**:
  - `event_id`: Many2one to events.clone.event
  - `subject`: Char
  - `body`: Html
  - `contact_tag_ids`: Many2many to res.partner.category
  - `recipient_ids`: Many2many to res.partner (computed)
  - `recipient_count`: Integer (computed)

---

## 🎯 Best Practices

1. **Always review recipients** before sending emails
2. **Use meaningful subject lines** to improve open rates
3. **Test with a small group** before sending to large audiences
4. **Keep contact tags organized** for better targeting
5. **Monitor the activity log** to track email communications

---

## 🚀 Future Enhancements (Optional)

Potential improvements for future versions:
- Email templates for common event invitations
- Scheduled email sending
- Email tracking (opens, clicks)
- Bulk email statistics
- Attachment support
- CC/BCC functionality
- Email preview before sending

---

## ✅ Testing Checklist

- [x] Module upgraded successfully
- [x] Contact tags field appears in event form
- [x] Send Email button appears in button box
- [x] Wizard opens when clicking Send Email button
- [x] Recipients are filtered correctly (active + email + tags)
- [x] Recipient count updates dynamically
- [x] Email sends successfully
- [x] Success notification appears
- [x] Activity logged on event record
- [x] Email records created in mail.mail

---

## 📞 Support

For issues or questions:
1. Check the Odoo logs for detailed error messages
2. Verify contact tags are properly assigned to contacts
3. Ensure contacts have valid email addresses
4. Confirm contacts are marked as active

---

**Module Version**: 1.0.0  
**Odoo Version**: 19.0  
**Last Updated**: 2025-11-19

