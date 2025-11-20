# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EventsCloneEmailWizard(models.TransientModel):
    """Wizard for sending emails to contacts based on selected tags"""
    _name = 'events.clone.email.wizard'
    _description = 'Events Clone Email Wizard'

    # Event reference
    event_id = fields.Many2one('events.clone.event', string='Event', required=True, readonly=True)
    
    # Email fields
    subject = fields.Char(string='Subject', required=True, default=lambda self: self._default_subject())
    body = fields.Html(string='Message', required=True, sanitize_style=True)
    
    # Contact tag selection (from event)
    contact_tag_ids = fields.Many2many(
        'res.partner.category', 
        string='Contact Tags',
        help='Select contact tags to filter recipients'
    )
    
    # Recipients display
    recipient_ids = fields.Many2many(
        'res.partner',
        string='Recipients',
        compute='_compute_recipient_ids',
        store=False,
        help='Contacts that will receive the email (active contacts with selected tags)'
    )
    recipient_count = fields.Integer(
        string='Number of Recipients',
        compute='_compute_recipient_ids',
        store=False
    )
    
    @api.model
    def _default_subject(self):
        """Generate default subject based on event"""
        if self.env.context.get('active_id'):
            event = self.env['events.clone.event'].browse(self.env.context.get('active_id'))
            if event:
                return f"Invitation: {event.name}"
        return "Event Invitation"
    
    @api.depends('contact_tag_ids')
    def _compute_recipient_ids(self):
        """Compute recipients based on selected contact tags"""
        for wizard in self:
            if wizard.contact_tag_ids:
                # Find all active contacts that have ANY of the selected tags
                recipients = self.env['res.partner'].search([
                    ('category_id', 'in', wizard.contact_tag_ids.ids),
                    ('active', '=', True),
                    ('email', '!=', False),  # Only contacts with email addresses
                ])
                wizard.recipient_ids = recipients
                wizard.recipient_count = len(recipients)
            else:
                wizard.recipient_ids = False
                wizard.recipient_count = 0
    
    def action_send_email(self):
        """Send email to all active recipients"""
        self.ensure_one()
        
        # Validate recipients
        if not self.recipient_ids:
            raise UserError(_('No recipients found. Please select contact tags that have associated contacts with email addresses.'))
        
        if not self.subject or not self.body:
            raise UserError(_('Subject and message body are required.'))
        
        # Get active recipients with email addresses
        active_recipients = self.recipient_ids.filtered(lambda p: p.active and p.email)
        
        if not active_recipients:
            raise UserError(_('No active recipients with email addresses found.'))
        
        # Prepare email values
        mail_values_list = []
        for recipient in active_recipients:
            mail_values = {
                'subject': self.subject,
                'body_html': self.body,
                'email_to': recipient.email,
                'email_from': self.env.user.email or self.env.company.email,
                'author_id': self.env.user.partner_id.id,
                'auto_delete': False,  # Keep email records for tracking
                'model': 'events.clone.event',
                'res_id': self.event_id.id,
            }
            mail_values_list.append(mail_values)
        
        # Create and send emails
        if mail_values_list:
            mails = self.env['mail.mail'].sudo().create(mail_values_list)
            mails.send()
            
            # Log activity on the event
            self.event_id.message_post(
                body=_('Email sent to %d recipients with subject: %s') % (len(active_recipients), self.subject),
                subject=_('Email Sent'),
                message_type='notification',
            )
        
        # Return success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Email sent successfully to %d recipients.') % len(active_recipients),
                'type': 'success',
                'sticky': False,
            }
        }
    
    @api.onchange('event_id')
    def _onchange_event_id(self):
        """Update contact tags when event changes"""
        if self.event_id and self.event_id.contact_tag_ids:
            self.contact_tag_ids = self.event_id.contact_tag_ids

