# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import api, fields, models


class EventsCloneTagCategory(models.Model):
    _name = 'events.clone.tag.category'
    _description = "Events Clone Tag Category"
    _order = "sequence"

    def _default_sequence(self):
        return (self.search([], order="sequence desc", limit=1).sequence or 0) + 1

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer('Sequence', default=_default_sequence)
    tag_ids = fields.One2many('events.clone.tag', 'category_id', string="Tags")


class EventsCloneTag(models.Model):
    _name = 'events.clone.tag'
    _description = "Events Clone Tag"
    _order = "category_sequence, sequence, id"

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
    category_id = fields.Many2one("events.clone.tag.category", string="Category", required=True, index=True, ondelete='cascade')
    category_sequence = fields.Integer(related='category_id.sequence', string='Category Sequence', store=True)
    color = fields.Integer(
        string='Color Index', default=lambda self: self._default_color(),
        help='Tag color. No color means no display in kanban.')

