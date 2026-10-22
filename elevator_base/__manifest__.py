# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Elevator Base',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'summary': 'Elevators — register, types, lifecycle, authorisation',
    'category': 'Elevator Service',
    'description': """
        Core module for elevator service management.

        The elevator is a maintenance.equipment record, not a separate model:
        an elevator is an asset with a maintenance history, and Odoo already
        has that. This module adds what makes it an elevator — identity,
        technical configuration, statutory inspection dates and
        authorisation status.

        Included:
        - Elevator identity: number, manufacturing number, year, stops
        - Technical configuration: drive type, control system, doors
        - Statutory inspection: last, next, inspection body, remark level
        - Authorisation: who may service this elevator and under which scheme
        - Lifecycle stage derived from inspection and service dates

        Built on Odoo maintenance and the Vertel field service fork.

        Industry modules build on this one:
            elevator_law          BFS, AFS, ESA as document.law records
            elevator_competence   certifications as hr.skill records
            elevator_inspection   inspection rounds and remarks
            elevator_contract     service agreements
            elevator_portal       customer portal
    """,
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
        'maintenance',
        'fieldservice_vrtl',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/elevator_type_data.xml',
        'views/maintenance_equipment_views.xml',
        'views/elevator_type_views.xml',
        'views/elevator_menu.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
