# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_report',
    'name': 'Elevator Report — Brandade rapporter',
    'version': '18.0.1.0.1',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'Branded inspection protocol, service report and elevator sheet',
    'description': '''
Elevator Report — Brandade rapporter
====================================

    The three documents a service company hands to a customer.

    The portal ships a plain protocol so it works without this module. This
    one overrides it with the branded version and adds the two other
    documents:

        Besiktningsprotokoll    the inspection, point by point, with the
                                remark level and a signature line
        Servicerapport          what the technician did on a work order
        Hisskort                a one-page sheet per elevator: identity,
                                technical data, last inspection, agreement

    The protocol is the one that matters legally. It is what the inspection
    body signs and what the supervisory authority asks for when something
    goes wrong. It therefore carries the inspection number, the inspector,
    the body, every point with its result, and the aggregated remark level
    spelled out — "Röd anmärkning — hissen får inte användas" rather than a
    colour code someone has to interpret.

    The elevator sheet is what a technician carries: identity, technical
    configuration, inspection dates, agreement terms, emergency phone. One
    page, because it is read standing in a stairwell.

    Features:

        - Branded inspection protocol (overrides the portal template)
        - Service report per work order
        - Elevator sheet per elevator
        - Print buttons on the inspection, order and elevator forms
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        'elevator_inspection',
        'elevator_contract',
        'elevator_portal',
        'fieldservice_vrtl',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/report_templates.xml',
        'views/report_actions.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
