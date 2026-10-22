# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_ai',
    'name': 'Elevator AI — AI-coworkers för hisservice',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'AI coworkers for inspection analysis and fault triage',
    'description': '''
Elevator AI — AI-coworkers för hisservice
=========================================

    Two AI coworkers for elevator service, built on ai_agent_core.

    The bridge pattern: the AI capability lives here, never in the core
    modules. elevator_base, elevator_inspection and elevator_iot know
    nothing about AI — this module adds the coworkers that read their data.

    Included:

        Hissan­alytiker       analyses an elevator's inspection history and
                             sensor readings, and says what to look at next
        Felavhjälpning       reads a fault report and suggests a diagnosis
                             and a first action for the technician

    Both deliver proposals, never decisions. An inspection remark that takes
    an elevator out of service is a legal act, and a technician's diagnosis
    is a professional judgement — the AI drafts, the human decides. That is
    why hitl_threshold is 'always' on both.

    What the coworkers see
    ----------------------
    injection_level is summary_and_key: the coworker gets a summary of the
    record and the key fields, not the whole database. An elevator with ten
    years of inspections has more history than a prompt can hold, and most
    of it is irrelevant to the question being asked.

    Features:

        - Elevator analyst coworker on inspections
        - Fault triage coworker on work orders
        - Both HITL-gated: proposals, never automatic action
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        'elevator_inspection',
        'elevator_iot',
        'ai_agent_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ai_coworker_data.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
