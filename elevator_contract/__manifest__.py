# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_contract',
    'name': 'Elevator Contract — Serviceavtal',
    'version': '18.0.1.0.6',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'Service agreements on elevators, built on contract.contract',
    'description': '''
Elevator Contract — Serviceavtal
================================

    Service agreements for elevators, on top of OCA contract.

    The agreement is a contract.contract record with the elevator attached,
    not a model of its own: contract already owns the recurrence, the
    invoicing and the renewal, and a second implementation would drift.

    What this adds is what is specific to elevator service:

        equipment_id          which elevator the agreement covers
        visits_per_year       how often the technician comes
        response_time_hours   the contractual response time
        includes_inspection   whether statutory inspection is included
        coverage              what is covered: full service, parts,
                              emergency call-out

    The overlap check matters: an elevator cannot have two active service
    agreements at the same time. Without it, two agreements bill the same
    elevator and the technician gets two orders for the same visit.

    Features:

        - Service agreement fields on contract.contract
        - One active agreement per elevator, enforced
        - Visits per year drives the maintenance plan
        - Response time and coverage visible on the elevator
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        'contract',
        'maintenance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/elevator_menu.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
