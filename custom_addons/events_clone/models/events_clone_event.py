# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.fields import Datetime


class EventsCloneEvent(models.Model):
    """Events Clone Event"""
    _name = 'events.clone.event'
    _description = 'Events Clone Event'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_begin, id'

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if 'date_begin' in fields and 'date_begin' not in result:
            now = Datetime.now()
            result['date_begin'] = now.replace(second=0, microsecond=0) + timedelta(minutes=-now.minute % 30)
        if 'date_end' in fields and 'date_end' not in result and result.get('date_begin'):
            result['date_end'] = result['date_begin'] + timedelta(days=1)
        return result

    def _get_default_stage_id(self):
        return self.env['events.clone.stage'].search([], limit=1)

    # Basic Information
    name = fields.Char(string='Event Name', translate=True, required=True, tracking=True)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one(
        'res.users', string='Responsible', tracking=True,
        default=lambda self: self.env.user)
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False)
    organizer_id = fields.Many2one(
        'res.partner', string='Organizer', tracking=True,
        default=lambda self: self.env.company.partner_id)
    
    # Description and Details
    description = fields.Html(string='Description', translate=True)
    note = fields.Html(string='Note')
    
    # Tags and Stage
    tag_ids = fields.Many2many('events.clone.tag', string="Tags")
    stage_id = fields.Many2one(
        'events.clone.stage', ondelete='restrict', default=_get_default_stage_id,
        tracking=True, copy=False, string='Stage')
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready for Next Stage'),
        ('blocked', 'Blocked'),
    ], default='normal', copy=False, tracking=True)

    # Contact Tags for Email Functionality
    contact_tag_ids = fields.Many2many(
        'res.partner.category',
        'events_clone_event_partner_category_rel',
        'event_id',
        'category_id',
        string='Contact Tags',
        help='Select contact tags to filter recipients for email communication'
    )
    
    # Date and Time
    date_begin = fields.Datetime(string='Start Date', required=True, tracking=True)
    date_end = fields.Datetime(string='End Date', required=True, tracking=True)
    date_tz = fields.Selection(
        '_tz_get', string='Timezone', required=True,
        default=lambda self: self.env.user.tz or 'UTC')
    
    # Location
    address_id = fields.Many2one(
        'res.partner', string='Venue', tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    country_id = fields.Many2one('res.country', string='Country', related='address_id.country_id', store=True)
    
    # Seats and Attendees
    seats_limited = fields.Boolean('Limit Attendees', default=False)
    seats_max = fields.Integer(
        string='Maximum Attendees', default=0,
        help="Maximum number of attendees. Set to 0 for unlimited.")
    seats_reserved = fields.Integer(
        string='Reserved Seats', compute='_compute_seats', store=True)
    seats_available = fields.Integer(
        string='Available Seats', compute='_compute_seats', store=True)
    seats_used = fields.Integer(
        string='Number of Attendees', compute='_compute_seats', store=True)
    
    # Relations
    event_ticket_ids = fields.One2many(
        'events.clone.ticket', 'event_id', string='Event Tickets', copy=True)
    registration_ids = fields.One2many(
        'events.clone.registration', 'event_id', string='Registrations')
    
    # Computed fields
    registration_count = fields.Integer(
        string='Registration Count', compute='_compute_registration_count')
    
    @api.model
    def _tz_get(self):
        return [(tz, tz) for tz in sorted(pytz.all_timezones)]
    
    @api.depends('registration_ids')
    def _compute_registration_count(self):
        for event in self:
            event.registration_count = len(event.registration_ids)
    
    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        for event in self:
            event.seats_reserved = len(event.registration_ids.filtered(lambda r: r.state in ['draft', 'open']))
            event.seats_used = len(event.registration_ids.filtered(lambda r: r.state == 'open'))
            if event.seats_max > 0:
                event.seats_available = event.seats_max - event.seats_reserved
            else:
                event.seats_available = 0
    
    @api.constrains('date_begin', 'date_end')
    def _check_dates(self):
        for event in self:
            if event.date_end < event.date_begin:
                raise models.ValidationError(_('The end date cannot be earlier than the start date.'))
    
    def action_view_registrations(self):
        action = self.env['ir.actions.act_window']._for_xml_id('events_clone.action_events_clone_registration')
        action['domain'] = [('event_id', '=', self.id)]
        action['context'] = {'default_event_id': self.id}
        return action

    def action_send_email(self):
        """Open email wizard to send emails to contacts based on selected tags"""
        self.ensure_one()
        return {
            'name': _('Send Email'),
            'type': 'ir.actions.act_window',
            'res_model': 'events.clone.email.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_event_id': self.id,
                'default_contact_tag_ids': self.contact_tag_ids.ids,
            },
        }


import pytz

