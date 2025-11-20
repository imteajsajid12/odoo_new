# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventsCloneRegistration(models.Model):
    _name = 'events.clone.registration'
    _description = 'Events Clone Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def _get_random_barcode(self):
        """Generate a random barcode for registration"""
        return str(int.from_bytes(os.urandom(8), 'little'))

    # Event Information
    event_id = fields.Many2one(
        'events.clone.event', string='Event', required=True, 
        tracking=True, index=True, ondelete='cascade')
    event_ticket_id = fields.Many2one(
        'events.clone.ticket', string='Ticket Type', 
        ondelete='restrict', tracking=True, index=True)
    
    # Attendee Information
    partner_id = fields.Many2one(
        'res.partner', string='Booked by', tracking=True, index=True)
    name = fields.Char(
        string='Attendee Name', required=True, index=True,
        compute='_compute_name', readonly=False, store=True, tracking=True)
    email = fields.Char(
        string='Email', compute='_compute_email', 
        readonly=False, store=True, tracking=True)
    phone = fields.Char(
        string='Phone', compute='_compute_phone', 
        readonly=False, store=True, tracking=True)
    company_name = fields.Char(
        string='Company Name', compute='_compute_company_name', 
        readonly=False, store=True)
    
    # Status and Tracking
    active = fields.Boolean(default=True)
    barcode = fields.Char(
        string='Barcode', default=lambda self: self._get_random_barcode(), 
        readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('open', 'Registered'),
        ('done', 'Attended'),
        ('cancel', 'Cancelled')],
        string='Status', default='draft',
        readonly=True, copy=False, tracking=True)
    
    # Dates
    date_closed = fields.Datetime(string='Attended Date', readonly=True)
    create_date = fields.Datetime(string='Registration Date', readonly=True)
    
    # Company
    company_id = fields.Many2one(
        'res.company', string='Company', 
        related='event_id.company_id', store=True, readonly=True)
    
    # UTM Tracking
    utm_campaign_id = fields.Many2one('utm.campaign', 'Campaign', ondelete='set null')
    utm_source_id = fields.Many2one('utm.source', 'Source', ondelete='set null')
    utm_medium_id = fields.Many2one('utm.medium', 'Medium', ondelete='set null')
    
    @api.depends('partner_id')
    def _compute_name(self):
        for registration in self:
            if registration.partner_id and not registration.name:
                registration.name = registration.partner_id.name
    
    @api.depends('partner_id')
    def _compute_email(self):
        for registration in self:
            if registration.partner_id and not registration.email:
                registration.email = registration.partner_id.email
    
    @api.depends('partner_id')
    def _compute_phone(self):
        for registration in self:
            if registration.partner_id and not registration.phone:
                registration.phone = registration.partner_id.phone
    
    @api.depends('partner_id')
    def _compute_company_name(self):
        for registration in self:
            if registration.partner_id and not registration.company_name:
                if registration.partner_id.parent_id:
                    registration.company_name = registration.partner_id.parent_id.name
                elif registration.partner_id.is_company:
                    registration.company_name = registration.partner_id.name
    
    def action_confirm(self):
        self.write({'state': 'open'})
    
    def action_set_done(self):
        self.write({'state': 'done', 'date_closed': fields.Datetime.now()})
    
    def action_cancel(self):
        self.write({'state': 'cancel'})
    
    def action_set_draft(self):
        self.write({'state': 'draft'})
    
    @api.constrains('event_id', 'state')
    def _check_seats_availability(self):
        for registration in self:
            if registration.state in ['open', 'done'] and registration.event_id.seats_limited:
                if registration.event_id.seats_available < 0:
                    raise ValidationError(_('No more seats available for this event.'))

