# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pytz
import textwrap
import urllib.parse
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from markupsafe import escape
from urllib.parse import urlparse

from odoo import _, api, Command, fields, models, tools
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError
from odoo.fields import Datetime, Domain
from odoo.tools import format_date, format_datetime, format_time, frozendict
from odoo.tools.mail import is_html_empty, html_to_inner_content
from odoo.tools.misc import formatLang
from odoo.tools.translate import html_translate

_logger = logging.getLogger(__name__)

try:
    import vobject
except ImportError:
    _logger.warning("`vobject` Python module not found, iCal file generation disabled. Consider installing this module if you want to generate iCal files")
    vobject = None


class EventEvent(models.Model):
    """Event"""
    _name = 'event.event'
    _description = 'Event'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_begin, id'

    # Maximum number of tickets that can be ordered at one time on a same line
    EVENT_MAX_TICKETS = 30

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if 'date_begin' in fields and 'date_begin' not in result:
            now = Datetime.now()
            # Round the datetime to the nearest half hour (e.g. 08:17 => 08:30 and 08:37 => 09:00)
            result['date_begin'] = now.replace(second=0, microsecond=0) + timedelta(minutes=-now.minute % 30)
        if 'date_end' in fields and 'date_end' not in result and result.get('date_begin'):
            result['date_end'] = result['date_begin'] + timedelta(days=1)
        return result

    def get_kiosk_url(self):
        return self.get_base_url() + "/odoo/registration-desk"

    def _get_default_stage_id(self):
        return self.env['event.stage'].search([], limit=1)

    def _default_description(self):
        # avoid template branding with rendering_bundle=True
        return self.env['ir.ui.view'].with_context(rendering_bundle=True) \
            ._render_template('event.event_default_descripton')

    def _default_event_mail_ids(self):
        return self.env['event.type']._default_event_mail_type_ids()

    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    def _default_question_ids(self):
        return self.env['event.type']._default_question_ids()

    name = fields.Char(string='Event', translate=True, required=True)
    note = fields.Html(string='Note', store=True, compute="_compute_note", readonly=False)
    description = fields.Html(string='Description', translate=html_translate, sanitize_attributes=False, sanitize_form=False, default=_default_description)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one(
        'res.users', string='Responsible', tracking=True,
        default=lambda self: self.env.user)
    use_barcode = fields.Boolean(compute='_compute_use_barcode')
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False)
    organizer_id = fields.Many2one(
        'res.partner', string='Organizer', tracking=True,
        default=lambda self: self.env.company.partner_id,
        check_company=True)
    event_type_id = fields.Many2one(
        'event.type', string='Template', ondelete='set null',
        help="Choose a template to auto-fill tickets, communications, descriptions and other fields.")
    event_mail_ids = fields.One2many(
        'event.mail', 'event_id', string='Mail Schedule', copy=True,
        compute='_compute_event_mail_ids', readonly=False, store=True)
    tag_ids = fields.Many2many(
        'event.tag', string="Tags", readonly=False,
        store=True, compute="_compute_tag_ids")
    # properties
    registration_properties_definition = fields.PropertiesDefinition('Registration Properties')
    # Kanban fields
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready for Next Stage'),
        ('blocked', 'Blocked'),
        ('cancel', 'Cancelled')
    ], default='normal', copy=False, compute='_compute_kanban_state', readonly=False, store=True, tracking=True)
    stage_id = fields.Many2one(
        'event.stage', ondelete='restrict', default=_get_default_stage_id,
        group_expand='_read_group_expand_full', tracking=True, copy=False)
    # Seats and computation
    seats_max = fields.Integer(
        string='Maximum Attendees',
        compute='_compute_seats_max', readonly=False, store=True,
        help="For each event you can define a maximum registration of seats(number of attendees), above this number the registrations are not accepted. "
        "If the event has multiple slots, this maximum number is applied per slot.")
    seats_limited = fields.Boolean('Limit Attendees', required=True, compute='_compute_seats_limited',
                                   precompute=True, readonly=False, store=True)
    seats_reserved = fields.Integer(
        string='Number of Registrations',
        store=False, readonly=True, compute='_compute_seats')
    seats_available = fields.Integer(
        string='Available Seats',
        store=False, readonly=True, compute='_compute_seats')
    seats_used = fields.Integer(
        string='Number of Attendees',
        store=False, readonly=True, compute='_compute_seats')
    seats_taken = fields.Integer(
        string='Number of Taken Seats',
        store=False, readonly=True, compute='_compute_seats')
    # Trainer
    trainer_id = fields.Many2one(
        'res.partner', string='Trainer',
        domain="[('is_company', '=', False)]",
        help="Select a contact to assign as the trainer for this event")
    trainer_tag_ids = fields.Many2many(
        'res.partner.category',
        'event_trainer_tag_rel',
        'event_id',
        'category_id',
        string='Trainer Tags',
        help='Select contact tags to filter trainers for email communication'
    )
    trainer_tag_contact_ids = fields.Many2many(
        'res.partner',
        string='Contacts with Trainer Tags',
        compute='_compute_trainer_tag_contact_ids',
        store=False,
        help='All contacts that have any of the selected trainer tags'
    )
    trainer_tag_contact_count = fields.Integer(
        string='Trainer Tag Contact Count',
        compute='_compute_trainer_tag_contact_ids',
        store=False
    )
    # Registration fields
    registration_ids = fields.One2many('event.registration', 'event_id', string='Attendees')
    contact_ids = fields.Many2many(
        'res.partner',
        'event_contact_rel',
        'event_id',
        'partner_id',
        string='Contacts',
        help='Contacts related to this event.'
    )
    contact_count = fields.Integer(
        string='Number of Contacts',
        compute='_compute_contact_count',
        store=False
    )
    contacts_available = fields.Boolean(
        string='Contacts Available', compute='_compute_contacts_available')
    is_multi_slots = fields.Boolean("Is Multi Slots", copy=True,
        help="Allow multiple time slots. "
        "The communications, the maximum number of attendees and the maximum number of tickets registrations "
        "are defined for each time slot instead of the whole event.")
    event_slot_ids = fields.One2many("event.slot", "event_id", "Slots", copy=True)
    event_slot_count = fields.Integer("Slots Count", compute="_compute_event_slot_count")
    event_ticket_ids = fields.One2many(
        'event.event.ticket', 'event_id', string='Event Ticket', copy=True,
        compute='_compute_event_ticket_ids', readonly=False, store=True, precompute=True)
    event_registrations_started = fields.Boolean(
        'Registrations started', compute='_compute_event_registrations_started',
        help="registrations have started if the current datetime is after the earliest starting date of tickets."
    )
    event_registrations_open = fields.Boolean(
        'Registration open', compute='_compute_event_registrations_open', compute_sudo=True,
        help="Registrations are open if:\n"
        "- the event is not ended or not cancelled\n"
        "- there are seats available on event\n"
        "- the tickets are sellable (if ticketing is used)")
    event_registrations_sold_out = fields.Boolean(
        'Sold Out', compute='_compute_event_registrations_sold_out', compute_sudo=True,
        help='The event is sold out if no more seats are available on event. If ticketing is used and all tickets are sold out, the event will be sold out.')
    start_sale_datetime = fields.Datetime(
        'Start sale date', compute='_compute_start_sale_date',
        help='If ticketing is used, contains the earliest starting sale date of tickets.')
    # Date fields
    date_tz = fields.Selection(
        _tz_get, string='Display Timezone', required=True,
        compute='_compute_date_tz', precompute=True, readonly=False, store=True,
        help="Indicates the timezone in which the event dates/times will be displayed on the website.")
    date_begin = fields.Datetime(string='Start Date', required=True, tracking=True,
        help="When the event is scheduled to take place (expressed in your local timezone on the form view).")
    date_end = fields.Datetime(string='End Date', required=True, tracking=True)
    is_ongoing = fields.Boolean('Is Ongoing', compute='_compute_is_ongoing', search='_search_is_ongoing')
    is_one_day = fields.Boolean(compute='_compute_field_is_one_day')
    is_finished = fields.Boolean(compute='_compute_is_finished', search='_search_is_finished')
    # Location and communication
    address_id = fields.Many2one(
        'res.partner', string='Venue', default=lambda self: self.env.company.partner_id.id,
        check_company=True,
        tracking=True
    )
    address_search = fields.Many2one(
        'res.partner', string='Address', compute='_compute_address_search', search='_search_address_search')
    address_inline = fields.Char(
        string='Venue (formatted for one line uses)', compute='_compute_address_inline',
        compute_sudo=True)
    country_id = fields.Many2one(
        'res.country', 'Country', related='address_id.country_id', readonly=False, store=True)
    event_url = fields.Char(
        string='Online Event URL', compute='_compute_event_url', readonly=False, store=True,
        help="Link where the online event will take place.",
    )
    event_share_url = fields.Char(string='Event Share URL', compute='_compute_event_share_url')
    lang = fields.Selection(_lang_get, string='Language',
        help="All the communication emails sent to attendees will be translated in this language.")
    # ticket reports
    badge_format = fields.Selection(
        string='Badge Dimension',
        selection=[
            ('A4_french_fold', 'A4 foldable'),
            ('A6', 'A6'),
            ('four_per_sheet', '4 per sheet'),
        ], default='A6', required=True)
    badge_image = fields.Image('Badge Background', max_width=1024, max_height=1024)
    ticket_instructions = fields.Html('Ticket Instructions', translate=True,
        compute='_compute_ticket_instructions', store=True, readonly=False,
        help="This information will be printed on your tickets.")
    # questions
    question_ids = fields.Many2many('event.question', 'event_event_event_question_rel',
        string='Questions', compute='_compute_question_ids', readonly=False, store=True, precompute=True)
    general_question_ids = fields.Many2many('event.question', 'event_event_event_question_rel',
        string='General Questions', domain=[('once_per_order', '=', True)])
    specific_question_ids = fields.Many2many('event.question', 'event_event_event_question_rel',
        string='Specific Questions', domain=[('once_per_order', '=', False)])
    # Notification tracking fields
    is_reminder_sent = fields.Boolean(
        string='Reminder Email Sent',
        default=False,
        copy=False,
        help='Indicates if the one-week reminder email has been sent'
    )
    trainer_notified = fields.Boolean(
        string='Trainer Notified',
        default=False,
        copy=False,
        help='Indicates if trainers have been notified about this event'
    )
    responsible_notified = fields.Boolean(
        string='Responsible Notified',
        default=False,
        copy=False,
        help='Indicates if the responsible user has been notified about this event'
    )
    reminder_cron_id = fields.Many2one(
        'ir.cron',
        string='Reminder Scheduled Action',
        ondelete='cascade',
        copy=False,
        help='Scheduled action for sending one-week reminder email'
    )

    def _compute_use_barcode(self):
        use_barcode = self.env['ir.config_parameter'].sudo().get_param('event.use_event_barcode') == 'True'
        for record in self:
            record.use_barcode = use_barcode

    def _compute_contacts_available(self):
        """Check if contacts (res.partner) are available in the system"""
        for event in self:
            try:
                # Check if we can access res.partner model
                partner_count = self.env['res.partner'].search_count([('is_company', '=', False)], limit=1)
                event.contacts_available = True
            except Exception:
                event.contacts_available = False

    @api.depends('trainer_tag_ids')
    def _compute_trainer_tag_contact_ids(self):
        """Compute all contacts that have any of the selected trainer tags"""
        for event in self:
            if event.trainer_tag_ids:
                # Find all partners that have any of the selected tags
                contacts = self.env['res.partner'].search([
                    ('category_id', 'in', event.trainer_tag_ids.ids),
                    ('is_company', '=', False)
                ])
                event.trainer_tag_contact_ids = contacts
                event.trainer_tag_contact_count = len(contacts)
            else:
                event.trainer_tag_contact_ids = False
                event.trainer_tag_contact_count = 0

    def _compute_event_share_url(self):
        """Get the URL to use to redirect to the event, overriden in website for fallback."""
        for event in self:
            event.event_share_url = event.event_url

    @api.depends('event_type_id')
    def _compute_question_ids(self):
        """ Update event questions from its event type. Depends are set only on
        event_type_id itself to emulate an onchange. Changing event type content
        itself should not trigger this method.

        When synchronizing questions:

          * lines with no registered answers for the event are removed;
          * type lines are added;
        """
        for event in self:
            questions_tokeep_ids = []
            if self._origin.question_ids:
                # Keep questions with attendee answers for the event.
                questions_tokeep_ids.extend(
                    (event.registration_ids.registration_answer_ids.question_id & self._origin.question_ids).ids
                )

            if not event.event_type_id and not questions_tokeep_ids:
                event.question_ids = self._default_question_ids()
                continue

            if questions_tokeep_ids:
                questions_toremove = event._origin.question_ids.filtered(
                    lambda question: question.id not in questions_tokeep_ids)
                command = [(3, question.id) for question in questions_toremove]
            else:
                command = [(5, 0)]
            event.question_ids = command
            event.question_ids = [Command.link(question_id.id) for question_id in event.event_type_id.question_ids]

    @api.depends('event_slot_count', 'is_multi_slots', 'seats_max', 'registration_ids.state', 'registration_ids.active')
    def _compute_seats(self):
        """ Determine available, reserved, used and taken seats. """
        # initialize fields to 0
        for event in self:
            event.seats_reserved = event.seats_used = event.seats_available = 0
        # aggregate registrations by event and by state
        state_field = {
            'open': 'seats_reserved',
            'done': 'seats_used',
        }
        base_vals = dict((fname, 0) for fname in state_field.values())
        results = dict((event_id, dict(base_vals)) for event_id in self.ids)
        if self.ids:
            query = """ SELECT event_id, state, count(event_id)
                        FROM event_registration
                        WHERE event_id IN %s AND state IN ('open', 'done') AND active = true
                        GROUP BY event_id, state
                    """
            self.env['event.registration'].flush_model(['event_id', 'state', 'active'])
            self.env.cr.execute(query, (tuple(self.ids),))
            res = self.env.cr.fetchall()
            for event_id, state, num in res:
                results[event_id][state_field[state]] = num

        # compute seats_available and expected
        for event in self:
            event.update(results.get(event._origin.id or event.id, base_vals))
            seats_max = event.seats_max * event.event_slot_count if event.is_multi_slots else event.seats_max
            if seats_max > 0:
                event.seats_available = seats_max - (event.seats_reserved + event.seats_used)

            event.seats_taken = event.seats_reserved + event.seats_used

    @api.depends('date_tz', 'start_sale_datetime')
    def _compute_event_registrations_started(self):
        for event in self:
            event = event._set_tz_context()
            if event.start_sale_datetime:
                current_datetime = fields.Datetime.context_timestamp(event, fields.Datetime.now())
                start_sale_datetime = fields.Datetime.context_timestamp(event, event.start_sale_datetime)
                event.event_registrations_started = (current_datetime >= start_sale_datetime)
            else:
                event.event_registrations_started = True

    @api.depends('date_tz', 'event_registrations_started', 'date_end', 'seats_available', 'seats_limited', 'seats_max',
                 'event_ticket_ids.sale_available')
    def _compute_event_registrations_open(self):
        """ Compute whether people may take registrations for this event

          * for cancelled events, registrations are not open;
          * event.date_end -> if event is done, registrations are not open anymore;
          * event.start_sale_datetime -> lowest start date of tickets (if any; start_sale_datetime
            is False if no ticket are defined, see _compute_start_sale_date);
          * any ticket is available for sale (seats available) if any;
          * seats are unlimited or seats are available;
        """
        for event in self:
            event = event._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(event, fields.Datetime.now())
            date_end_tz = event.date_end.astimezone(pytz.timezone(event.date_tz or 'UTC')) if event.date_end else False
            event.event_registrations_open = event.kanban_state != 'cancel' and \
                event.event_registrations_started and \
                (date_end_tz >= current_datetime if date_end_tz else True) and \
                (not event.seats_limited or not event.seats_max or event.seats_available) and \
                (
                    # Not multi slots: open if no tickets or at least a sale available ticket
                    (not event.is_multi_slots and
                        (not event.event_ticket_ids or any(ticket.sale_available for ticket in event.event_ticket_ids)))
                    or
                    # Multi slots: open if at least a slot and no tickets or at least an ongoing ticket with availability
                    (event.is_multi_slots and event.event_slot_count and (
                        not event.event_ticket_ids or any(
                            ticket.is_launched and not ticket.is_expired and (
                                any(availability is None or availability > 0
                                    for availability in event._get_seats_availability([
                                        (slot, ticket)
                                        for slot in event.event_slot_ids
                                    ])
                                )
                            ) for ticket in event.event_ticket_ids
                        )
                    ))
                )

    @api.depends('event_ticket_ids.start_sale_datetime')
    def _compute_start_sale_date(self):
        """ Compute the start sale date of an event. Currently lowest starting sale
        date of tickets if they are used, of False. """
        for event in self:
            start_dates = [ticket.start_sale_datetime for ticket in event.event_ticket_ids if not ticket.is_expired]
            event.start_sale_datetime = min(start_dates) if start_dates and all(start_dates) else False

    @api.depends('event_slot_ids', 'event_ticket_ids.sale_available', 'seats_available', 'seats_limited')
    def _compute_event_registrations_sold_out(self):
        """Note that max seats limits for events and sum of limits for all its tickets may not be
        equal to enable flexibility.
        E.g. max 20 seats for ticket A, 20 seats for ticket B
            * With max 20 seats for the event
            * Without limit set on the event (=40, but the customer didn't explicitly write 40)
        When the event is multi slots, instead of checking if every tickets is sold out,
        checking if every slot-ticket combination is sold out.
        """
        for event in self:
            event.event_registrations_sold_out = (
                (event.seats_limited and event.seats_max and not event.seats_available > 0)
                or (event.event_ticket_ids and (
                    not any(availability is None or availability > 0
                        for availability in event._get_seats_availability([
                            (slot, ticket)
                            for slot in event.event_slot_ids
                            for ticket in event.event_ticket_ids
                        ])
                    )
                    if event.is_multi_slots else
                    all(ticket.is_sold_out for ticket in event.event_ticket_ids)
                ))
            )

    @api.depends('date_begin', 'date_end')
    def _compute_is_ongoing(self):
        now = fields.Datetime.now()
        for event in self:
            event.is_ongoing = event.date_begin <= now < event.date_end

    def _search_is_ongoing(self, operator, value):
        if operator != 'in':
            return NotImplemented
        now = fields.Datetime.now()
        return [('date_begin', '<=', now), ('date_end', '>', now)]

    @api.depends('date_begin', 'date_end', 'date_tz')
    def _compute_field_is_one_day(self):
        for event in self:
            # Need to localize because it could begin late and finish early in
            # another timezone
            event = event._set_tz_context()
            begin_tz = fields.Datetime.context_timestamp(event, event.date_begin)
            end_tz = fields.Datetime.context_timestamp(event, event.date_end)
            event.is_one_day = (begin_tz.date() == end_tz.date())

    @api.depends('date_end')
    def _compute_is_finished(self):
        for event in self:
            if not event.date_end:
                event.is_finished = False
                continue
            event = event._set_tz_context()
            current_datetime = fields.Datetime.context_timestamp(event, fields.Datetime.now())
            datetime_end = fields.Datetime.context_timestamp(event, event.date_end)
            event.is_finished = datetime_end <= current_datetime

    def _search_is_finished(self, operator, value):
        if operator != 'in':
            return NotImplemented
        return [('date_end', '<=', fields.Datetime.now())]

    @api.depends('event_type_id')
    def _compute_date_tz(self):
        for event in self:
            if event.event_type_id.default_timezone:
                event.date_tz = event.event_type_id.default_timezone
            if not event.date_tz:
                event.date_tz = self.env.user.tz or 'UTC'

    @api.depends("event_slot_ids")
    def _compute_event_slot_count(self):
        slot_count_per_event = dict(self.env['event.slot']._read_group(
            domain=[('event_id', 'in', self.ids)],
            groupby=['event_id'],
            aggregates=['__count']
        ))
        for event in self:
            event.event_slot_count = slot_count_per_event.get(event, 0)

    @api.depends('contact_ids')
    def _compute_contact_count(self):
        """Compute the number of contacts associated with the event."""
        for event in self:
            event.contact_count = len(event.contact_ids)

    @api.depends('address_id')
    def _compute_address_search(self):
        for event in self:
            event.address_search = event.address_id

    def _search_address_search(self, operator, value):
        def make_codomain(value):
            return Domain.OR(
                Domain(field, 'ilike', value)
                for field in ('name', 'street', 'street2', 'city', 'zip', 'state_id', 'country_id')
            )
        if isinstance(value, Domain):
            domain = value.map_conditions(lambda cond: cond if cond.field_expr != 'display_name' else make_codomain(cond.value))
            return Domain('address_id', operator, domain)
        if operator == 'ilike' and isinstance(value, str):
            return Domain('address_id', 'any', make_codomain(value))
        # for the trivial "empty" case, there is no empty address
        if operator == 'in' and (not value or not any(value)):
            return Domain(False)
        return NotImplemented

    # seats

    @api.depends('event_type_id')
    def _compute_seats_max(self):
        """ Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method. """
        for event in self:
            if not event.event_type_id:
                event.seats_max = event.seats_max or 0
            else:
                event.seats_max = event.event_type_id.seats_max or 0

    @api.depends('event_type_id')
    def _compute_seats_limited(self):
        """ Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method. """
        for event in self:
            if event.event_type_id.has_seats_limitation != event.seats_limited:
                event.seats_limited = event.event_type_id.has_seats_limitation
            if not event.seats_limited:
                event.seats_limited = False

    @api.depends('event_type_id')
    def _compute_event_mail_ids(self):
        """ Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method.

        When synchronizing mails:

          * lines that are not sent and have no registrations linked are remove;
          * type lines are added;
        """
        for event in self:
            if not event.event_type_id and not event.event_mail_ids:
                event.event_mail_ids = self._default_event_mail_ids()
                continue

            # lines to keep: those with already sent emails or registrations
            mails_to_remove = event.event_mail_ids.filtered(
                lambda mail: not(mail._origin.mail_done) and not(mail._origin.mail_registration_ids)
            )
            command = [Command.unlink(mail.id) for mail in mails_to_remove]

            # lines to add: those which do not have the exact copy available in lines to keep
            if event.event_type_id.event_type_mail_ids:
                mails_to_keep_vals = {frozendict(mail._prepare_event_mail_values()) for mail in event.event_mail_ids - mails_to_remove}
                for mail in event.event_type_id.event_type_mail_ids:
                    mail_values = frozendict(mail._prepare_event_mail_values())
                    if mail_values not in mails_to_keep_vals:
                        command.append(Command.create(mail_values))
            if command:
                event.event_mail_ids = command

    @api.depends('event_type_id')
    def _compute_tag_ids(self):
        """ Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method. """
        for event in self:
            if not event.tag_ids and event.event_type_id.tag_ids:
                event.tag_ids = event.event_type_id.tag_ids

    @api.depends('event_type_id')
    def _compute_event_ticket_ids(self):
        """ Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method.

        When synchronizing tickets:

          * lines that have no registrations linked are remove;
          * type lines are added;

        Note that updating event_ticket_ids triggers _compute_start_sale_date
        (start_sale_datetime computation) so ensure result to avoid cache miss.
        """
        for event in self:
            if not event.event_type_id and not event.event_ticket_ids:
                event.event_ticket_ids = False
                continue

            # lines to keep: those with existing registrations
            tickets_to_remove = event.event_ticket_ids.filtered(lambda ticket: not ticket._origin.registration_ids)
            command = [Command.unlink(ticket.id) for ticket in tickets_to_remove]
            if event.event_type_id.event_type_ticket_ids:
                command += [
                    Command.create({
                        attribute_name: line[attribute_name] if not isinstance(line[attribute_name], models.BaseModel) else line[attribute_name].id
                        for attribute_name in self.env['event.type.ticket']._get_event_ticket_fields_whitelist()
                    }) for line in event.event_type_id.event_type_ticket_ids
                ]
            event.event_ticket_ids = command

    @api.depends('event_type_id')
    def _compute_note(self):
        for event in self:
            if event.event_type_id and not is_html_empty(event.event_type_id.note):
                event.note = event.event_type_id.note

    @api.depends('stage_id')
    def _compute_kanban_state(self):
        for task in self:
            if task.kanban_state != 'cancel':
                task.kanban_state = 'normal'

    @api.depends('event_type_id')
    def _compute_ticket_instructions(self):
        for event in self:
            if is_html_empty(event.ticket_instructions) and not \
               is_html_empty(event.event_type_id.ticket_instructions):
                event.ticket_instructions = event.event_type_id.ticket_instructions

    @api.depends('address_id')
    def _compute_address_inline(self):
        """Use venue address if available, otherwise its name, finally ''. """
        for event in self:
            if (event.address_id.contact_address or '').strip():
                event.address_inline = ', '.join(
                    frag.strip()
                    for frag in event.address_id.contact_address.split('\n') if frag.strip()
                )
            else:
                event.address_inline = event.address_id.name or ''

    @api.depends('address_id')
    def _compute_event_url(self):
        """Reset url field as it should only be used for events with no physical location."""
        self.filtered('address_id').event_url = ''

    @api.constrains("date_begin", "date_end", "event_slot_ids", "is_multi_slots")
    def _check_slots_dates(self):
        multi_slots_event_ids = self.filtered(lambda event: event.is_multi_slots).ids
        if not multi_slots_event_ids:
            return
        min_max_slot_dates_per_event = {
            event: (min_start, max_end)
            for event, min_start, max_end in self.env['event.slot']._read_group(
                domain=[('event_id', 'in', multi_slots_event_ids)],
                groupby=['event_id'],
                aggregates=['start_datetime:min', 'end_datetime:max']
            )
        }
        events_w_slots_outside_bounds = []
        for event, (min_start, max_end) in min_max_slot_dates_per_event.items():
            if (not (event.date_begin <= min_start <= event.date_end) or
                not (event.date_begin <= max_end <= event.date_end)):
                events_w_slots_outside_bounds.append(event)
        if events_w_slots_outside_bounds:
            raise ValidationError(_(
                "These events cannot have slots scheduled outside of their time range:\n%(event_names)s",
                event_names="\n".join(f"- {event.name}" for event in events_w_slots_outside_bounds)
            ))

    @api.constrains('date_begin', 'date_end')
    def _check_closing_date(self):
        for event in self:
            if event.date_end < event.date_begin:
                raise ValidationError(_('The closing date cannot be earlier than the beginning date.'))

    @api.constrains('event_url')
    def _check_event_url(self):
        for event in self.filtered('event_url'):
            url = urlparse(event.event_url)
            if not (url.scheme and url.netloc):
                raise ValidationError(_('Please enter a valid event URL.'))

    @api.onchange('event_url')
    def _onchange_event_url(self):
        """Correct the url by adding scheme if it is missing."""
        for event in self.filtered('event_url'):
            parsed_url = urlparse(event.event_url)
            if parsed_url.scheme not in ('http', 'https'):
                event.event_url = 'https://' + event.event_url

    @api.onchange('seats_max')
    def _onchange_seats_max(self):
        for event in self:
            if event.seats_limited and event.seats_max and event.seats_available <= 0 and \
                (event.event_slot_ids if event.is_multi_slots else True):
                return {
                    'warning': {
                        'title': _("Update the limit of registrations?"),
                        'message': _("There are more registrations than this limit, "
                                    "the event will be sold out and the extra registrations will remain."),
                    }
                }

    @api.depends('event_registrations_sold_out', 'seats_limited', 'seats_max', 'seats_available')
    @api.depends_context('name_with_seats_availability')
    def _compute_display_name(self):
        """Adds ticket seats availability if requested by context."""
        if not self.env.context.get('name_with_seats_availability'):
            return super()._compute_display_name()
        for event in self:
            # event or its tickets are sold out
            if event.event_registrations_sold_out:
                name = _('%(event_name)s (Sold out)', event_name=event.name)
            elif event.seats_limited and event.seats_max:
                name = _(
                    '%(event_name)s (%(count)s seats remaining)',
                    event_name=event.name,
                    count=formatLang(self.env, event.seats_available, digits=0),
                )
            else:
                name = event.name
            event.display_name = name

    def copy_data(self, default=None):
        vals_list = super().copy_data(default=default)
        return [dict(vals, name=self.env._("%s (copy)", event.name)) for event, vals in zip(self, vals_list)]

    def _mail_get_operation_for_mail_message_operation(self, message_operation):
        if (message_operation == 'create' and self.env.user.has_group('event.group_event_registration_desk')):
            # allow the registration desk users to post messages on Event
            # can not be done with "_mail_post_access" otherwise public user will be
            # able to post on published Event (see website_event)
            return dict.fromkeys(self, 'read')
        return super()._mail_get_operation_for_mail_message_operation(message_operation)

    def _set_tz_context(self):
        self.ensure_one()
        return self.with_context(tz=self.date_tz or 'UTC')

    def _get_seats_availability(self, slot_tickets):
        """ Get availabilities for given combinations of slot / ticket. Returns
        a list following input order. None denotes no limit. """
        self.ensure_one()
        if not (all(len(item) == 2 for item in slot_tickets)):
            raise ValueError('Input should be a list of tuples containing slot, ticket')

        if any(slot for (slot, _ticket) in slot_tickets):
            slot_tickets_nb_registrations = {
                (slot.id, ticket.id): count
                for (slot, ticket, count) in self.env['event.registration'].sudo()._read_group(
                    domain=[('event_slot_id', '!=', False), ('event_id', 'in', self.ids),
                            ('state', 'in', ['open', 'done']), ('active', '=', True)],
                    groupby=['event_slot_id', 'event_ticket_id'],
                    aggregates=['__count']
                )
            }

        availabilities = []
        for slot, ticket in slot_tickets:
            available = None
            # event is constrained: max stands for either each slot, either global (no slots)
            if self.seats_limited and self.seats_max:
                if slot:
                    available = slot.seats_available
                else:
                    available = self.seats_available
            # ticket is constrained: max standard for either each slot / ticket, either global (no slots)
            if available != 0 and ticket and ticket.seats_max:
                if slot:
                    ticket_available = ticket.seats_max - slot_tickets_nb_registrations.get((slot.id, ticket.id), 0)
                else:
                    ticket_available = ticket.seats_available
                available = ticket_available if available is None else min(available, ticket_available)
            availabilities.append(available)
        return availabilities

    def _verify_seats_availability(self, slot_tickets):
        """ Check event seats availability, for combinations of slot / ticket.

        :param slot_tickets: a list of tuples(slot, ticket, count). Slot and
          ticket are optional, depending on event configuration. If count is 0
          it is a simple check current values do not overflow limit. If count
          is given, it serves as a check there are enough remaining seats.
        :raises ValidationError: if the event / slot / ticket do not have
          enough available seats
        """
        self.ensure_one()
        if not (all(len(item) == 3 for item in slot_tickets)):
            raise ValueError('Input should be a list of tuples containing slot, ticket, count')

        sold_out = []
        availabilities = self._get_seats_availability([(item[0], item[1]) for item in slot_tickets])
        for (slot, ticket, count), available in zip(slot_tickets, availabilities, strict=True):
            if available is None:  # unconstrained
                continue
            if available < count:
                if slot and ticket:
                    name = f'{ticket.name} - {slot.display_name}'
                elif slot:
                    name = slot.display_name
                elif ticket:
                    name = ticket.name
                else:
                    name = self.name
                sold_out.append((name, count - available))

        if sold_out:
            info = []  # note: somehow using list comprehension make translate.py crash in default lang
            for item in sold_out:
                info.append(_('%(slot_name)s: missing %(count)s seat(s)', slot_name=item[0], count=item[1]))
            raise ValidationError(
                _('There are not enough seats available for %(event_name)s:\n%(sold_out_info)s',
                  event_name=self.name,
                  sold_out_info='\n'.join(info),
                )
            )

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    def action_open_slot_calendar(self):
        self.ensure_one()
        now = datetime.now().astimezone(pytz.timezone(self.env.user.tz or 'UTC'))
        next_hour = now + timedelta(hours=1)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Slots'),
            'view_mode': 'calendar,list,form',
            'mobile_view_mode': 'list',
            'res_model': 'event.slot',
            'target': 'current',
            'domain': [('event_id', '=', self.id)],
            'context': {
                'default_event_id': self.id,
                # Default hours for the list view and mobile quick create.
                # Desktop calendar multi create using defaults in local storage
                # (= the last selected time range or fallback on 12PM-1PM).
                'default_start_hour': next_hour.hour,
                'default_end_hour': (next_hour + timedelta(hours=1)).hour,
                # To disable calendar days outside of event date range.
                'event_calendar_range_start_date': self.date_begin.astimezone(pytz.timezone(self.date_tz)).date(),
                'event_calendar_range_end_date': self.date_end.astimezone(pytz.timezone(self.date_tz)).date(),
                # Calendar view initial date.
                'initial_date': min(max(datetime.now(), self.date_begin), self.date_end),
            },
        }

    def action_view_contacts(self):
        """Open the list of contacts associated with this event."""
        self.ensure_one()
        return {
            'name': _('Event Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.contact_ids.ids)],
            'context': {
                'default_event_id': self.id,
                'search_default_customer': 1,
            },
        }

    def action_send_email_to_contacts(self):
        """Open email composer to send email to selected contacts."""
        self.ensure_one()

        # Check if event is saved
        if not self.id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Event Not Saved'),
                    'message': _('Please save the event before sending emails to contacts.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Check if contacts exist
        if not self.contact_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Contacts'),
                    'message': _('Please add contacts to this event before sending emails.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Get the email composer form view
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=False)

        return {
            'name': _('Send Email to Event Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_id': compose_form.id if compose_form else False,
            'target': 'new',
            'context': {
                'default_composition_mode': 'mass_mail',
                'default_model': 'res.partner',
                'default_res_ids': self.contact_ids.ids,
                'default_partner_ids': self.contact_ids.ids,
                'default_subject': _('Event: %s', self.name),
                'default_body': self._get_default_email_body(),
                'mail_post_autofollow': True,
            },
        }

    def _get_default_email_body(self):
        """Generate default email body for event contacts."""
        self.ensure_one()
        body = f"""
        <p>Dear Contact,</p>
        <p>We would like to inform you about our upcoming event:</p>
        <p><strong>{escape(self.name)}</strong></p>
        """

        if self.date_begin:
            date_str = format_datetime(self.env, self.date_begin, dt_format='medium')
            body += f"<p><strong>Date:</strong> {date_str}</p>"

        if self.address_id:
            body += f"<p><strong>Location:</strong> {escape(self.address_id.name)}</p>"

        if self.description:
            body += f"<p><strong>Description:</strong></p>{self.description}"

        body += """
        <p>We look forward to seeing you there!</p>
        <p>Best regards,</p>
        """

        return body

    def action_set_done(self):
        """
        Action which will move the events
        into the first next (by sequence) stage defined as "Ended"
        (if they are not already in an ended stage)
        """
        first_ended_stage = self.env['event.stage'].search([('pipe_end', '=', True)], limit=1, order='sequence')
        if first_ended_stage:
            self.write({'stage_id': first_ended_stage.id})

    def _get_date_range_str(self, start_datetime=False, lang_code=False):
        self.ensure_one()
        datetime = start_datetime or self.date_begin
        today_tz = pytz.utc.localize(fields.Datetime.now()).astimezone(pytz.timezone(self.date_tz))
        event_date_tz = pytz.utc.localize(datetime).astimezone(pytz.timezone(self.date_tz))
        diff = (event_date_tz.date() - today_tz.date())
        if diff.days <= 0:
            return _('today')
        if diff.days == 1:
            return _('tomorrow')
        if (diff.days < 7):
            return _('in %d days', diff.days)
        if (diff.days < 14):
            return _('next week')
        if event_date_tz.month == (today_tz + relativedelta(months=+1)).month:
            return _('next month')
        return _('on %(date)s', date=format_date(self.env, datetime, lang_code=lang_code, date_format='medium'))

    def _get_external_description(self):
        """
        Description of the event shortened to maximum 1900 characters to
        leave some space for addition by sub-modules.
        Meant to be used for external content (ics/icalc/Gcal).

        Reference Docs for URL limit -: https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
        """
        self.ensure_one()
        description = ''
        if self.event_share_url:
            description = f'<a href="{escape(self.event_share_url)}">{escape(self.name)}</a>\n'
        description += textwrap.shorten(html_to_inner_content(self.description), 1900)
        return description

    def _get_external_description_url_encoded(self):
        """Get a url-encoded version of the description for mail templates."""
        return urllib.parse.quote_plus(self._get_external_description())

    def _get_ics_file(self, slot=False):
        """ Returns iCalendar file for the event invitation.
            :param slot: If a slot is given, schedule with the given slot datetimes
            :returns a dict of .ics file content for each event
        """
        result = {}
        if not vobject:
            return result

        for event in self:
            cal = vobject.iCalendar()
            cal_event = cal.add('vevent')
            start = slot.start_datetime or event.date_begin
            end = slot.end_datetime or event.date_end

            cal_event.add('created').value = fields.Datetime.now().replace(tzinfo=pytz.timezone('UTC'))
            cal_event.add('dtstart').value = start.astimezone(pytz.timezone(event.date_tz))
            cal_event.add('dtend').value = end.astimezone(pytz.timezone(event.date_tz))
            cal_event.add('summary').value = event.name
            cal_event.add('description').value = event._get_external_description()
            if event.address_id:
                cal_event.add('location').value = event.address_inline

            result[event.id] = cal.serialize().encode('utf-8')
        return result

    def _get_tickets_access_hash(self, registration_ids):
        """ Returns the ground truth hash for accessing the tickets in route /event/<int:event_id>/my_tickets.
        The dl links are always made event-dependant, hence the method linked to the record in self.
        """
        self.ensure_one()
        return tools.hmac(self.env(su=True), 'event-registration-ticket-report-access', (self.id, sorted(registration_ids)))

    def action_send_email_to_trainer(self):
        """Open email composer to send email to the trainer."""
        self.ensure_one()

        # Check if event is saved
        if not self.id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Event Not Saved'),
                    'message': _('Please save the event before sending emails to the trainer.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Check if trainer exists
        if not self.trainer_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Trainer'),
                    'message': _('Please assign a trainer to this event before sending emails.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Get the email composer form view
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=False)

        return {
            'name': _('Send Email to Trainer'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_id': compose_form.id if compose_form else False,
            'target': 'new',
            'context': {
                'default_composition_mode': 'comment',
                'default_model': 'res.partner',
                'default_res_ids': [self.trainer_id.id],
                'default_partner_ids': [self.trainer_id.id],
                'default_subject': _('Event: %s - Trainer Information', self.name),
                'default_body': self._get_default_email_body_for_trainer(),
                'mail_post_autofollow': True,
            },
        }

    def _get_default_email_body_for_trainer(self):
        """Generate default email body for trainer."""
        self.ensure_one()
        body = f"""
        <p>Dear {escape(self.trainer_id.name)},</p>
        <p>You have been assigned as a trainer for the following event:</p>
        <p><strong>{escape(self.name)}</strong></p>
        """

        if self.date_begin:
            date_str = format_datetime(self.env, self.date_begin, dt_format='medium')
            body += f"<p><strong>Date & Time:</strong> {date_str}</p>"

        if self.address_id:
            body += f"<p><strong>Location:</strong> {escape(self.address_id.name)}</p>"

        if self.description:
            body += f"<p><strong>Event Description:</strong></p>{self.description}"

        body += """
        <p>Please confirm your availability and let us know if you have any questions.</p>
        <p>Best regards,</p>
        """

        return body

    def action_send_email_to_trainer_tags(self):
        """Open email composer to send email to contacts with selected trainer tags."""
        self.ensure_one()

        # Check if event is saved
        if not self.id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Event Not Saved'),
                    'message': _('Please save the event before sending emails to trainer tag contacts.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Check if trainer tags are selected
        if not self.trainer_tag_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Trainer Tags Selected'),
                    'message': _('Please select trainer tags before sending emails.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Check if there are contacts with the selected tags
        if not self.trainer_tag_contact_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Contacts Found'),
                    'message': _('No contacts found with the selected trainer tags.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Get the email composer form view
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=False)

        return {
            'name': _('Send Email to Trainer Tag Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_id': compose_form.id if compose_form else False,
            'target': 'new',
            'context': {
                'default_composition_mode': 'mass_mail',
                'default_model': 'res.partner',
                'default_res_ids': self.trainer_tag_contact_ids.ids,
                'default_partner_ids': self.trainer_tag_contact_ids.ids,
                'default_subject': _('Event: %s - Trainer Information', self.name),
                'default_body': self._get_default_email_body_for_trainer_tags(),
                'mail_post_autofollow': True,
            },
        }

    def _get_default_email_body_for_trainer_tags(self):
        """Generate default email body for trainer tag contacts."""
        self.ensure_one()
        
        tag_names = ', '.join(self.trainer_tag_ids.mapped('name'))
        
        body = f"""
        <p>Dear Trainer,</p>
        <p>We would like to inform you about an upcoming event that may be of interest to you:</p>
        <p><strong>{escape(self.name)}</strong></p>
        """

        if self.date_begin:
            date_str = format_datetime(self.env, self.date_begin, dt_format='medium')
            body += f"<p><strong>Date & Time:</strong> {date_str}</p>"

        if self.address_id:
            body += f"<p><strong>Location:</strong> {escape(self.address_id.name)}</p>"

        if self.description:
            body += f"<p><strong>Event Description:</strong></p>{self.description}"

        body += f"""
        <p><em>You are receiving this email because you are tagged with: {escape(tag_names)}</em></p>
        <p>Please let us know if you have any questions or would like to participate.</p>
        <p>Best regards,</p>
        """

        return body

    def _prepare_assignment_email_body(self, recipient_type='trainer'):
        """Generate HTML email body for event assignment notifications.
        
        Args:
            recipient_type: 'trainer' or 'responsible'
        """
        self.ensure_one()
        
        # Format dates and times
        if self.date_begin:
            self = self._set_tz_context()
            date_begin_tz = fields.Datetime.context_timestamp(self, self.date_begin)
            date_end_tz = fields.Datetime.context_timestamp(self, self.date_end)
            
            training_date = format_date(self.env, self.date_begin, date_format='medium')
            start_time = format_time(self.env, self.date_begin, time_format='short')
            end_time = format_time(self.env, self.date_end, time_format='short')
        else:
            training_date = _('Not set')
            start_time = _('Not set')
            end_time = _('Not set')
        
        # Get location
        if self.address_id:
            location = escape(self.address_id.name)
            if self.address_id.city:
                location += f", {escape(self.address_id.city)}"
        elif self.event_url:
            location = f'Online Event: <a href="{escape(self.event_url)}">{escape(self.event_url)}</a>'
        else:
            location = _('Online Event')
        
        # Get responsible person
        responsible_person = escape(self.user_id.name) if self.user_id else _('Not assigned')
        
        # Get max attendees
        if self.seats_limited and self.seats_max:
            max_attendees = str(self.seats_max)
            if self.is_multi_slots:
                max_attendees += _(' per slot')
        else:
            max_attendees = _('Unlimited')
        
        # Build email body
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">You've been assigned to {escape(self.name)} training event</h2>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e; width: 200px;">
                            Training Event Title:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {escape(self.name)}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Training Date:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {training_date}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Event Start Time:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {start_time}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Event End Time:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {end_time}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Location:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {location}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Responsible Person:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {responsible_person}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Max Number of Attendees:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {max_attendees}
                        </td>
                    </tr>
                </table>
            </div>
        """
        
        if self.description and not is_html_empty(self.description):
            body += f"""
            <div style="margin: 20px 0;">
                <h3 style="color: #34495e;">Event Description:</h3>
                <div style="color: #2c3e50;">
                    {self.description}
                </div>
            </div>
            """
        
        body += """
            <p style="color: #2c3e50; margin-top: 20px;">
                We look forward to your participation in this training event.
            </p>
            <p style="color: #7f8c8d;">
                Best regards,<br/>
                Event Management Team
            </p>
        </div>
        """
        
        return body

    def _send_trainer_assignment_email(self):
        """Send assignment email to all contacts with selected trainer tags."""
        self.ensure_one()
        
        _logger.info(f"Event {self.name}: _send_trainer_assignment_email called")
        _logger.info(f"Event {self.name}: trainer_tag_ids = {self.trainer_tag_ids}")
        _logger.info(f"Event {self.name}: trainer_tag_contact_ids = {self.trainer_tag_contact_ids}")
        
        if not self.trainer_tag_ids or not self.trainer_tag_contact_ids:
            _logger.info(f"Event {self.name}: No trainer tags or contacts, skipping email")
            return
        
        # Get valid recipients (contacts with email addresses)
        recipients = self.trainer_tag_contact_ids.filtered(lambda p: p.email)
        
        if not recipients:
            _logger.warning(f"Event {self.name}: No valid email addresses found for trainer tag contacts")
            return
        
        _logger.info(f"Event {self.name}: Found {len(recipients)} recipients with emails")
        
        try:
            # Prepare email values
            subject = _("You've been assigned to %s training event", self.name)
            body = self._prepare_assignment_email_body(recipient_type='trainer')
            
            _logger.info(f"Event {self.name}: Email subject: {subject}")
            
            # Create mail for each recipient
            mail_values = []
            for recipient in recipients:
                mail_values.append({
                    'subject': subject,
                    'body_html': body,
                    'email_to': recipient.email,
                    'email_from': self.env.user.email or self.env.company.email,
                    'auto_delete': False,
                    'model': 'event.event',
                    'res_id': self.id,
                })
                _logger.info(f"Event {self.name}: Preparing email to {recipient.email}")
            
            # Create and send emails
            if mail_values:
                _logger.info(f"Event {self.name}: Creating {len(mail_values)} mail records")
                mails = self.env['mail.mail'].sudo().create(mail_values)
                _logger.info(f"Event {self.name}: Mail records created: {mails}")
                mails.send()
                _logger.info(f"Event {self.name}: Sent assignment emails to {len(recipients)} trainer tag contacts")
                
        except Exception as e:
            _logger.error(f"Event {self.name}: Failed to send trainer assignment emails: {str(e)}", exc_info=True)

    def _send_responsible_assignment_email(self):
        """Send assignment email to the responsible user."""
        self.ensure_one()
        
        _logger.info(f"Event {self.name}: _send_responsible_assignment_email called")
        _logger.info(f"Event {self.name}: user_id = {self.user_id}")
        
        if not self.user_id or not self.user_id.partner_id or not self.user_id.partner_id.email:
            _logger.info(f"Event {self.name}: No responsible user or email, skipping")
            return
        
        _logger.info(f"Event {self.name}: Responsible user email: {self.user_id.partner_id.email}")
        
        try:
            # Prepare email values
            subject = _("You've been assigned to %s training event", self.name)
            body = self._prepare_assignment_email_body(recipient_type='responsible')
            
            _logger.info(f"Event {self.name}: Email subject: {subject}")
            
            # Create and send email
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': self.user_id.partner_id.email,
                'email_from': self.env.company.email or 'noreply@example.com',
                'auto_delete': False,
                'model': 'event.event',
                'res_id': self.id,
            }
            
            _logger.info(f"Event {self.name}: Creating mail record for responsible user")
            mail = self.env['mail.mail'].sudo().create(mail_values)
            _logger.info(f"Event {self.name}: Mail record created: {mail}")
            mail.send()
            _logger.info(f"Event {self.name}: Sent assignment email to responsible user {self.user_id.name}")
            
        except Exception as e:
            _logger.error(f"Event {self.name}: Failed to send responsible user assignment email: {str(e)}", exc_info=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to send assignment emails after event creation."""
        _logger.info(f"EventEvent.create called with {len(vals_list)} events")
        events = super(EventEvent, self).create(vals_list)
        _logger.info(f"EventEvent.create: {len(events)} events created")
        
        # Send emails for each created event
        for event in events:
            _logger.info(f"Event {event.name}: Processing email notifications")
            try:
                # Send email to trainer tag contacts if tags are selected
                if event.trainer_tag_ids:
                    _logger.info(f"Event {event.name}: Has trainer tags, sending emails")
                    event._send_trainer_assignment_email()
                else:
                    _logger.info(f"Event {event.name}: No trainer tags")
                
                # Send email to responsible user if assigned
                if event.user_id:
                    _logger.info(f"Event {event.name}: Has responsible user, sending email")
                    event._send_responsible_assignment_email()
                else:
                    _logger.info(f"Event {event.name}: No responsible user")
                
                # Create scheduled action for one-week reminder
                if event.date_begin:
                    _logger.info(f"Event {event.name}: Creating reminder scheduled action")
                    event._create_reminder_scheduled_action()
                else:
                    _logger.info(f"Event {event.name}: No date_begin, skipping scheduled action")
                    
            except Exception as e:
                _logger.error(f"Event {event.name}: Error sending assignment emails on create: {str(e)}", exc_info=True)
        
        return events

    def write(self, vals):
        """Override write to send assignment emails when trainer tags or responsible user changes."""
        # Store old values before update
        old_trainer_tags = {event.id: event.trainer_tag_ids.ids for event in self}
        old_responsible_users = {event.id: event.user_id.id if event.user_id else False for event in self}
        old_date_begins = {event.id: event.date_begin for event in self}
        
        # Perform the write operation
        result = super(EventEvent, self).write(vals)
        
        # Check if trainer_tag_ids or user_id changed and send emails
        for event in self:
            try:
                # Check if trainer tags changed
                if 'trainer_tag_ids' in vals:
                    new_trainer_tags = set(event.trainer_tag_ids.ids)
                    old_tags = set(old_trainer_tags.get(event.id, []))
                    
                    # Send email if tags were added or changed
                    if new_trainer_tags != old_tags and event.trainer_tag_ids:
                        event._send_trainer_assignment_email()
                
                # Check if responsible user changed
                if 'user_id' in vals:
                    new_user_id = event.user_id.id if event.user_id else False
                    old_user_id = old_responsible_users.get(event.id, False)
                    
                    # Send email if user changed and new user exists
                    if new_user_id != old_user_id and event.user_id:
                        event._send_responsible_assignment_email()
                
                # Check if date_begin changed - update scheduled action
                if 'date_begin' in vals:
                    old_date = old_date_begins.get(event.id)
                    new_date = event.date_begin
                    
                    # If date changed, recreate the scheduled action
                    if old_date != new_date:
                        _logger.info(f"Event {event.name}: date_begin changed, updating scheduled action")
                        event._update_reminder_scheduled_action()
                        
            except Exception as e:
                _logger.error(f"Event {event.name}: Error sending assignment emails on write: {str(e)}")
        
        return result

    def unlink(self):
        """Override unlink to delete associated scheduled actions before deleting events."""
        # Delete scheduled actions for all events being deleted
        for event in self:
            try:
                if event.reminder_cron_id:
                    _logger.info(f"Event {event.name}: Deleting reminder scheduled action before unlink")
                    event.reminder_cron_id.unlink()
            except Exception as e:
                _logger.error(f"Event {event.name}: Error deleting scheduled action on unlink: {str(e)}")
        
        return super(EventEvent, self).unlink()

    def _generate_attendee_report_html(self):
        """Generate HTML table of all registered attendees with additional event information.
        
        Returns:
            str: HTML formatted attendee report
        """
        self.ensure_one()
        
        # Get all confirmed and done registrations
        registrations = self.registration_ids.filtered(lambda r: r.state in ['open', 'done'])
        
        if not registrations:
            return """
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <p style="color: #6c757d; margin: 0;"><em>No attendees registered yet.</em></p>
            </div>
            """
        
        # Build HTML table
        html = """
        <div style="margin: 20px 0;">
            <h3 style="color: #34495e; margin-bottom: 15px;">Attendee Report</h3>
            <table style="width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background-color: #3498db; color: white;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">#</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Name</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Email</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Phone</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Status</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Registration Date</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for idx, reg in enumerate(registrations, 1):
            # Alternate row colors
            bg_color = '#f8f9fa' if idx % 2 == 0 else 'white'
            
            # Status badge color
            status_color = '#28a745' if reg.state == 'done' else '#17a2b8'
            status_text = 'Attended' if reg.state == 'done' else 'Confirmed'
            
            html += f"""
                <tr style="background-color: {bg_color};">
                    <td style="padding: 10px; border: 1px solid #ddd;">{idx}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>{escape(reg.name or 'N/A')}</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{escape(reg.email or 'N/A')}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{escape(reg.phone or 'N/A')}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">
                        <span style="background-color: {status_color}; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px;">
                            {status_text}
                        </span>
                    </td>
                    <td style="padding: 10px; border: 1px solid #ddd;">
                        {format_datetime(self.env, reg.create_date, dt_format='short') if reg.create_date else 'N/A'}
                    </td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        # Add additional event information section
        html += """
        <div style="margin: 20px 0; background-color: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; border-radius: 3px;">
            <h4 style="color: #2c3e50; margin-top: 0;">Additional Event Information</h4>
        """
        
        # Add event-specific details
        if self.note and not is_html_empty(self.note):
            html += f"""
            <div style="margin: 10px 0;">
                <strong style="color: #34495e;">Internal Notes:</strong>
                <div style="margin-top: 5px; color: #2c3e50;">
                    {self.note}
                </div>
            </div>
            """
        
        # Add ticket information if available
        if self.event_ticket_ids:
            html += """
            <div style="margin: 10px 0;">
                <strong style="color: #34495e;">Ticket Types:</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
            """
            for ticket in self.event_ticket_ids:
                ticket_registrations = registrations.filtered(lambda r: r.event_ticket_id == ticket)
                html += f"""
                <li style="color: #2c3e50; margin: 5px 0;">
                    {escape(ticket.name)}: {len(ticket_registrations)} registered
                    {f' / {ticket.seats_max} max' if ticket.seats_max else ''}
                </li>
                """
            html += """
                </ul>
            </div>
            """
        
        # Add organizer contact info
        if self.organizer_id:
            html += f"""
            <div style="margin: 10px 0;">
                <strong style="color: #34495e;">Organizer Contact:</strong>
                <div style="margin-top: 5px; color: #2c3e50;">
                    {escape(self.organizer_id.name)}
                    {f' - {escape(self.organizer_id.email)}' if self.organizer_id.email else ''}
                    {f' - {escape(self.organizer_id.phone)}' if self.organizer_id.phone else ''}
                </div>
            </div>
            """
        
        html += """
        </div>
        """
        
        return html

    def _prepare_one_week_reminder_email_body(self, recipient_type='trainer'):
        """Generate HTML email body for one-week reminder notifications.
        
        Args:
            recipient_type: 'trainer' or 'responsible'
            
        Returns:
            str: HTML formatted email body
        """
        self.ensure_one()
        
        # Format dates and times
        if self.date_begin:
            self = self._set_tz_context()
            date_begin_tz = fields.Datetime.context_timestamp(self, self.date_begin)
            date_end_tz = fields.Datetime.context_timestamp(self, self.date_end)
            
            training_date = format_date(self.env, self.date_begin, date_format='medium')
            start_time = format_time(self.env, self.date_begin, time_format='short')
            end_time = format_time(self.env, self.date_end, time_format='short')
        else:
            training_date = _('Not set')
            start_time = _('Not set')
            end_time = _('Not set')
        
        # Get location
        if self.address_id:
            location = escape(self.address_id.name)
            if self.address_id.city:
                location += f", {escape(self.address_id.city)}"
        elif self.event_url:
            location = f'Online Event: <a href="{escape(self.event_url)}">{escape(self.event_url)}</a>'
        else:
            location = _('Online Event')
        
        # Get responsible person
        responsible_person = escape(self.user_id.name) if self.user_id else _('Not assigned')
        
        # Get number of booked attendees
        booked_attendees = self.seats_used
        
        # Build email body
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #ff9800; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
                <h2 style="margin: 0;">⏰ One Week to Go!</h2>
            </div>
            
            <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ff9800; margin-bottom: 20px;">
                <p style="margin: 0; color: #856404;">
                    <strong>Reminder:</strong> The event <strong>{escape(self.name)}</strong> is happening in one week!
                </p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Event Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e; width: 200px;">
                            Training Event Title:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {escape(self.name)}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Training Date:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {training_date}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Event Start Time:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {start_time}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Event End Time:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {end_time}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Location:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {location}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Responsible Person:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            {responsible_person}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; font-weight: bold; color: #34495e;">
                            Number of Booked Attendees:
                        </td>
                        <td style="padding: 10px 0; color: #2c3e50;">
                            <strong style="color: #28a745; font-size: 18px;">{booked_attendees}</strong>
                        </td>
                    </tr>
                </table>
            </div>
        """
        
        # Add attendee report
        body += self._generate_attendee_report_html()
        
        if self.description and not is_html_empty(self.description):
            body += f"""
            <div style="margin: 20px 0;">
                <h3 style="color: #34495e;">Event Description:</h3>
                <div style="color: #2c3e50; background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                    {self.description}
                </div>
            </div>
            """
        
        body += """
            <div style="background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; border-radius: 3px; margin: 20px 0;">
                <p style="margin: 0; color: #155724;">
                    <strong>Action Required:</strong> Please review the attendee list and ensure all preparations are complete for the upcoming event.
                </p>
            </div>
            
            <p style="color: #2c3e50; margin-top: 20px;">
                We look forward to a successful event!
            </p>
            <p style="color: #7f8c8d;">
                Best regards,<br/>
                Event Management Team
            </p>
        </div>
        """
        
        return body

    def _send_one_week_reminder_emails(self):
        """Send one-week reminder emails to trainers and responsible user."""
        self.ensure_one()
        
        _logger.info(f"Event {self.name}: Sending one-week reminder emails")
        
        # Send to trainer tag contacts
        if self.trainer_tag_ids and self.trainer_tag_contact_ids:
            recipients = self.trainer_tag_contact_ids.filtered(lambda p: p.email)
            
            if recipients:
                try:
                    subject = _("Reminder: %s - One Week to Go!", self.name)
                    body = self._prepare_one_week_reminder_email_body(recipient_type='trainer')
                    
                    mail_values = []
                    for recipient in recipients:
                        mail_values.append({
                            'subject': subject,
                            'body_html': body,
                            'email_to': recipient.email,
                            'email_from': self.env.user.email or self.env.company.email,
                            'auto_delete': False,
                            'model': 'event.event',
                            'res_id': self.id,
                        })
                    
                    if mail_values:
                        mails = self.env['mail.mail'].sudo().create(mail_values)
                        mails.send()
                        _logger.info(f"Event {self.name}: Sent one-week reminder to {len(recipients)} trainers")
                        
                except Exception as e:
                    _logger.error(f"Event {self.name}: Failed to send trainer reminder emails: {str(e)}", exc_info=True)
        
        # Send to responsible user
        if self.user_id and self.user_id.partner_id and self.user_id.partner_id.email:
            try:
                subject = _("Reminder: %s - One Week to Go!", self.name)
                body = self._prepare_one_week_reminder_email_body(recipient_type='responsible')
                
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_to': self.user_id.partner_id.email,
                    'email_from': self.env.company.email or 'noreply@example.com',
                    'auto_delete': False,
                    'model': 'event.event',
                    'res_id': self.id,
                }
                
                mail = self.env['mail.mail'].sudo().create(mail_values)
                mail.send()
                _logger.info(f"Event {self.name}: Sent one-week reminder to responsible user")
                
            except Exception as e:
                _logger.error(f"Event {self.name}: Failed to send responsible user reminder email: {str(e)}", exc_info=True)
        
        # Mark reminder as sent
        self.write({'is_reminder_sent': True})
        _logger.info(f"Event {self.name}: Marked is_reminder_sent = True")

    def _create_reminder_scheduled_action(self):
        """Create a dedicated scheduled action for this event's one-week reminder.
        
        The scheduled action will run exactly 7 days before the event starts.
        """
        self.ensure_one()
        
        if not self.date_begin:
            _logger.warning(f"Event {self.name}: Cannot create reminder scheduled action without date_begin")
            return
        
        # Calculate when to send reminder (7 days before event)
        reminder_datetime = self.date_begin - timedelta(days=7)
        
        # Don't create if reminder time is in the past
        if reminder_datetime < fields.Datetime.now():
            _logger.info(f"Event {self.name}: Reminder time is in the past, skipping scheduled action creation")
            return
        
        # Delete existing scheduled action if any
        if self.reminder_cron_id:
            _logger.info(f"Event {self.name}: Deleting existing reminder scheduled action")
            self.reminder_cron_id.unlink()
        
        try:
            # Create new scheduled action
            cron_vals = {
                'name': f'Event Reminder: {self.name}',
                'model_id': self.env.ref('event.model_event_event').id,
                'state': 'code',
                'code': f'model._send_event_reminder({self.id})',
                'interval_number': 1,
                'interval_type': 'days',
                'numbercall': 1,  # Run only once
                'doall': False,
                'active': True,
                'nextcall': reminder_datetime,
                'user_id': self.env.ref('base.user_root').id,
            }
            
            cron = self.env['ir.cron'].sudo().create(cron_vals)
            self.write({'reminder_cron_id': cron.id})
            
            _logger.info(f"Event {self.name}: Created reminder scheduled action (ID: {cron.id}) for {reminder_datetime}")
            
        except Exception as e:
            _logger.error(f"Event {self.name}: Failed to create reminder scheduled action: {str(e)}", exc_info=True)

    def _update_reminder_scheduled_action(self):
        """Update the scheduled action when event date changes."""
        self.ensure_one()
        
        # Simply recreate the scheduled action
        self._create_reminder_scheduled_action()

    def _delete_reminder_scheduled_action(self):
        """Delete the scheduled action for this event."""
        self.ensure_one()
        
        if self.reminder_cron_id:
            try:
                _logger.info(f"Event {self.name}: Deleting reminder scheduled action (ID: {self.reminder_cron_id.id})")
                self.reminder_cron_id.unlink()
                self.write({'reminder_cron_id': False})
            except Exception as e:
                _logger.error(f"Event {self.name}: Failed to delete reminder scheduled action: {str(e)}", exc_info=True)

    @api.model
    def _send_event_reminder(self, event_id):
        """Static method called by scheduled action to send reminder for a specific event.
        
        Args:
            event_id: ID of the event to send reminder for
        """
        _logger.info(f"_send_event_reminder called for event ID: {event_id}")
        
        try:
            event = self.browse(event_id)
            
            if not event.exists():
                _logger.warning(f"Event ID {event_id} not found, skipping reminder")
                return
            
            if event.is_reminder_sent:
                _logger.info(f"Event {event.name}: Reminder already sent, skipping")
                return
            
            if event.kanban_state == 'cancel':
                _logger.info(f"Event {event.name}: Event is cancelled, skipping reminder")
                return
            
            # Send the reminder emails
            _logger.info(f"Event {event.name}: Sending one-week reminder emails")
            event._send_one_week_reminder_emails()
            
            # Deactivate the scheduled action after it runs
            if event.reminder_cron_id:
                event.reminder_cron_id.write({'active': False})
                _logger.info(f"Event {event.name}: Deactivated reminder scheduled action")
            
        except Exception as e:
            _logger.error(f"Failed to send reminder for event ID {event_id}: {str(e)}", exc_info=True)

    @api.model
    def send_weekly_event_reminders(self, test_mode=False):
        """Cron job method to send one-week reminder emails for upcoming events.

        This method is called by a scheduled action (cron job) to find all events
        that are exactly 7 days away and haven't received reminder emails yet.

        Args:
            test_mode: If True, looks for events 10 minutes from now instead of 7 days.
                      This is useful for testing the email functionality.
        """
        _logger.info("Starting weekly event reminder cron job")

        # Check if test mode is enabled via system parameter
        test_mode_param = self.env['ir.config_parameter'].sudo().get_param('event.reminder_test_mode', 'False')
        test_mode = test_mode or (test_mode_param.lower() == 'true')

        # Calculate the date range based on mode
        now = fields.Datetime.now()

        if test_mode:
            # TEST MODE: Look for events 10 minutes from now (±5 minutes window)
            target_time = now + timedelta(minutes=10)
            time_window_start = target_time - timedelta(minutes=5)
            time_window_end = target_time + timedelta(minutes=5)
            _logger.info(f"TEST MODE: Looking for events between {time_window_start} and {time_window_end}")
        else:
            # PRODUCTION MODE: Look for events 7 days from now
            seven_days_from_now = now + timedelta(days=7)
            seven_days_date = seven_days_from_now.date()
            time_window_start = datetime.combine(seven_days_date, datetime.min.time())
            time_window_end = datetime.combine(seven_days_date, datetime.max.time())
            _logger.info(f"PRODUCTION MODE: Looking for events between {time_window_start} and {time_window_end}")

        # Find events that:
        # 1. Start date is within the target window
        # 2. Haven't received reminder email yet
        # 3. Are not cancelled
        events = self.search([
            ('date_begin', '>=', time_window_start),
            ('date_begin', '<=', time_window_end),
            ('is_reminder_sent', '=', False),
            ('kanban_state', '!=', 'cancel'),
        ])

        mode_str = "TEST MODE" if test_mode else "PRODUCTION MODE"
        _logger.info(f"{mode_str}: Found {len(events)} events requiring reminders")

        # Send reminder emails for each event
        for event in events:
            try:
                _logger.info(f"Processing reminder for event: {event.name} (ID: {event.id})")
                event._send_one_week_reminder_emails()
            except Exception as e:
                _logger.error(f"Failed to send reminder for event {event.name}: {str(e)}", exc_info=True)

        _logger.info(f"Completed weekly event reminder cron job. Processed {len(events)} events")
        return True

    @api.autovacuum
    def _gc_mark_events_done(self):
        """ move every ended events in the next 'ended stage' """
        ended_events = self.env['event.event'].search([
            ('date_end', '<', fields.Datetime.now()),
            ('stage_id.pipe_end', '=', False),
        ])
        if ended_events:
            ended_events.action_set_done()
