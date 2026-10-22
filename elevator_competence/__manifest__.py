# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_competence',
    'name': 'Elevator Competence — Hisscertifieringar',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'Elevator service certifications as hr.skill records',
    'description': '''
Elevator Competence — Hisscertifieringar
========================================

    The certifications an elevator technician has to hold, as hr.skill
    records on top of hr_skills_certificate.

    Industry bridge: the certifications are DATA. A fire protection company
    needs SBF Brandskyddskontrollant; an elevator company needs
    Hissinstallation and Elsäkerhet. That is why they live here and not in a
    generic module.

    Included:

        Hissinstallation          auktorisation per BFS 2011:12
        Elsäkerhet                ESA 2006:1
        Heta arbeten              AFS 2006:4
        Fallskydd / Höjdarbete    AFS 2001:1
        Första hjälpen / HLR
        Truckkort
        Tunga lyft
        Säkerhetsutbildning

    Each certification carries its statutory validity in the skill type, so
    Odoo's own expiration_status can flag it before it lapses. The periods
    are the ones the training schemes use in practice:

        Heta arbeten          5 years
        Fallskydd             2 years
        Elsäkerhet            5 years
        Hissinstallation      no fixed expiry — follows the auktorisation

    The certificate number, issuer and verification URL come from
    hr_skills_certificate. Without them an external certification is a
    claim; with them it can be checked against the issuer.

    Features:

        - One skill type for elevator certifications
        - Eight certifications seeded
        - Expiry tracked through Odoo's expiration_status
        - Certificate number and issuer on each CV line
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        # The certifications themselves live in odoo-hr as industry
        # bridges, so a company that already installs them for other
        # reasons does not get a second copy. This module only adds what is
        # specific to elevator service.
        'hr_certificate_hiss',
        'hr_certificate_esa',
        'hr_certificate_arbetsmiljo',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/elevator_competence_data.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
