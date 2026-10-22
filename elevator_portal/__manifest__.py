# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_portal',
    'name': 'Elevator Portal — Kundportal',
    'version': '18.0.1.0.1',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'Customer portal for elevators: status, inspections, fault reports',
    'description': '''
Elevator Portal — Kundportal
============================

    What a building owner needs to see about their elevators, and the one
    thing they need to do: report a fault.

    A fire extinguisher is passive — it is checked once a year. An elevator
    runs every day, and when it stops the tenants call the building owner,
    not the service company. That makes the fault report the most important
    part of the portal; the rest is information.

    Routes:

        /my/equipment                the elevators on my addresses
        /my/equipment/<id>           status, last inspection, agreement
        /my/equipment/<id>/report    fault report
        /my/equipment/<id>/inspection/<iid>/pdf   inspection protocol

    Fault reports create a fieldservice.order with the elevator attached, so
    they land in the technician's queue instead of in an inbox someone
    forgets. The order type is the repair type when it exists.

    Everything is scoped to the logged-in partner's commercial entity: a
    user sees the elevators of the company they belong to, never another
    customer's. Every route re-checks that the record belongs to that
    partner before rendering — a guessed id gives 404, not another
    customer's elevator.

    A tenant has no account. A QR code on the elevator opens the fault
    report for that elevator with a token in the URL, so the report can be
    filed without logging in. The token is per elevator and revocable: it
    identifies the elevator, not the person, and it cannot be used to read
    anything else.

    Features:

        - Elevator list and detail for the logged-in customer
        - Fault report form, creates a fieldservice order
        - Inspection protocol PDF
        - QR token for tenant fault reports without an account
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        'elevator_inspection',
        'elevator_contract',
        'fieldservice_vrtl',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
        'views/portal_menu.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
