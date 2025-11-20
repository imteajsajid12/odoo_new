# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class EventsCloneTicket(models.Model):
    _name = 'events.clone.ticket'
    _description = 'Events Clone Ticket'
    _order = "event_id, sequence, name, id"

    # Basic Information
    name = fields.Char(string='Ticket Name', required=True, translate=True)
    event_id = fields.Many2one(
        'events.clone.event', string="Event",
        ondelete='cascade', required=True, index=True)
    company_id = fields.Many2one('res.company', related='event_id.company_id', store=True)
    
    # Description
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Pricing
    price = fields.Float(string='Price', digits='Product Price', default=0.0)
    
    # Seats Management
    seats_max = fields.Integer(
        string='Maximum Available Seats',
        help='Maximum number of seats for this ticket. Set to 0 for unlimited.')
    seats_limited = fields.Boolean(string='Limited Seats', default=False)
    seats_reserved = fields.Integer(
        string='Reserved Seats', compute='_compute_seats', store=True)
    seats_available = fields.Integer(
        string='Available Seats', compute='_compute_seats', store=True)
    seats_used = fields.Integer(
        string='Used Seats', compute='_compute_seats', store=True)
    
    # Sale Period
    start_sale_datetime = fields.Datetime(string="Sale Start Date")
    end_sale_datetime = fields.Datetime(string="Sale End Date")
    is_launched = fields.Boolean(string='Sales Launched', compute='_compute_is_launched')
    is_expired = fields.Boolean(string='Is Expired', compute='_compute_is_expired')
    
    # Relations
    registration_ids = fields.One2many(
        'events.clone.registration', 'event_ticket_id', string='Registrations')
    
    @api.depends('start_sale_datetime')
    def _compute_is_launched(self):
        now = fields.Datetime.now()
        for ticket in self:
            if not ticket.start_sale_datetime:
                ticket.is_launched = True
            else:
                ticket.is_launched = ticket.start_sale_datetime <= now
    
    @api.depends('end_sale_datetime')
    def _compute_is_expired(self):
        now = fields.Datetime.now()
        for ticket in self:
            if not ticket.end_sale_datetime:
                ticket.is_expired = False
            else:
                ticket.is_expired = ticket.end_sale_datetime < now
    
    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        for ticket in self:
            ticket.seats_reserved = len(ticket.registration_ids.filtered(
                lambda r: r.state in ['draft', 'open']))
            ticket.seats_used = len(ticket.registration_ids.filtered(
                lambda r: r.state == 'done'))
            if ticket.seats_max > 0:
                ticket.seats_available = ticket.seats_max - ticket.seats_reserved
            else:
                ticket.seats_available = 0

