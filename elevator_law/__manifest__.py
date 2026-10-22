# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_law',
    'name': 'Elevator Law — Hisslagstiftning',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'Elevator legislation preloaded via document_law — BFS, AFS, ESA, auktorisation',
    'description': '''
Elevator Law — Hisslagstiftning
===============================

    The legislation an elevator service company has to comply with, as
    document.law records.

    Industry bridge: the laws are DATA, on top of document_law and
    mgmtsystem_law. A fire protection company needs LSO and BBR; an elevator
    company needs BFS and the auktorisation scheme. That is why they live
    here and not in a generic module.

    Included:

        Plan- och bygglagen (PBL)          SFS 2010:900
        Boverkets byggregler (BBR)         BBR 29, avsnitt 5
        BFS 2011:12                        Hissar — auktorisation och besiktning
        AFS 2023:1                         Systematiskt arbetsmiljöarbete
        AFS 2001:1                         Systematiskt arbetsmiljöarbete (ersatt)
        AFS 2006:4                         Heta arbeten
        AFS 2023:10                        Organisatorisk och social arbetsmiljö
        ESA 2006:1                          Elsäkerhet vid arbete i hiss
        Maskindirektivet                    EU 2006/42/EG

    The records carry name, code, description and a link to the source. They
    are deliberately short: the text belongs at the authority, not copied
    into Odoo where it would go stale.

    It does not decide which laws apply to which company. That is the law
    requirement proposal for odoo-knowledge — industry and size decide the
    set, and the customer subscribes. This module only ships the records.

    Features:

        - Nine statutes seeded with code, description and source link
        - Linked to mgmtsystem.system for management system tracking
        - Searchable by code and authority
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        'mgmtsystem_law',
        'document_law',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/elevator_law_data.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
