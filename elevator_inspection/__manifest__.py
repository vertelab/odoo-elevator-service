# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_inspection',
    'name': 'Elevator Inspection — Hissbesiktning',
    'version': '18.0.1.0.3',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'Statutory elevator inspection on the generic inspection model',
    'description': '''
Elevator Inspection — Hissbesiktning
====================================

    Statutory inspection of elevators, on top of
    maintenance_equipment_inspection.

    The generic module records the protocol: check points, results, remark
    level. This adds what is specific to elevators — and one thing the
    generic module cannot do: act on the result.

    A red remark on an elevator means it must be taken out of service. That
    is not a suggestion, it is BFS 2011:12. So when an inspection is
    completed with a red remark, this module writes it onto the elevator:

        equipment.inspection_remark = 'red_remark'
            -> lifecycle_stage = 'out_of_service'

    The elevator then shows as out of service everywhere, without anyone
    having to remember to set it.

    Included:

        - Inspection remark written back to the elevator on completion
        - Inspection templates per elevator type, seeded from the nine
          types elevator_base ships
        - Year wheel view: all inspections by month, coloured by remark
          level, so the inspection season is visible at a glance
        - Inspection interval per elevator type (BFS: 1 year for most,
          2 years for some)

    Elevator inspection is seasonal in practice: the inspection bodies work
    through their portfolios in a fixed order, and a company with 400
    elevators needs to see when the load falls. The year wheel shows every
    inspection by month with the remark level as colour, which is exactly
    the question "when is our inspection peak, and how many will come back
    red?".

    Features:

        - Red remark takes the elevator out of service automatically
        - Inspection templates seeded per elevator type
        - Year wheel by inspection date, coloured by remark level
        - Inspection interval on the elevator type
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        'maintenance_equipment_inspection',
        'web_year_wheel',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/elevator_inspection_template_data.xml',
        'views/maintenance_equipment_inspection_views.xml',
        'views/elevator_type_views.xml',
        'views/year_wheel_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
