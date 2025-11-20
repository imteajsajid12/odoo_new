# -*- coding: utf-8 -*-
{
    'name': 'Events Clone',
    'version': '1.0',
    'website': 'https://www.odoo.com/app/events',
    'category': 'Marketing/Events',
    'summary': 'Events Organization Clone - Trainings, Conferences, Meetings, Exhibitions, Registrations',
    'description': """
Events Clone - Organization and management of Events
=====================================================

This is a clone of the Events module that allows you to efficiently organize events and all related tasks: 
planning, registration tracking, attendances, etc.

Key Features
------------
* Manage your Events and Registrations
* Use emails to automatically confirm and send acknowledgments for any event registration
* Track event stages and progress
* Manage event tickets and pricing
* Handle event registrations and attendees
* Support for event tags and categorization
""",
    'depends': ['barcodes', 'base_setup', 'mail', 'phone_validation', 'portal', 'utm'],
    'data': [
        'security/events_clone_security.xml',
        'security/ir.model.access.csv',
        'wizard/events_clone_email_wizard_views.xml',
        'views/events_clone_menu_views.xml',
        'views/events_clone_ticket_views.xml',
        'views/events_clone_registration_views.xml',
        'views/events_clone_stage_views.xml',
        'views/events_clone_event_views.xml',
        'views/events_clone_tag_views.xml',
        'data/events_clone_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'events_clone/static/src/scss/events_clone.scss',
        ],
    },
    'author': 'Your Company',
    'license': 'LGPL-3',
}

