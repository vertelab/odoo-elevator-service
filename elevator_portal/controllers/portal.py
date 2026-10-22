# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http, _
from odoo.http import request
from odoo.addons.fieldservice_portal.controllers.portal import EquipmentPortal


class ElevatorPortal(EquipmentPortal):
    """Elevator additions to the generic equipment portal.

    The list, the fault report and the QR token come from
    fieldservice_portal. What this adds is what a building owner needs about
    an elevator specifically: the inspection history and the service
    agreement, and the protocol as a PDF.
    """

    # ── Detail, with elevator data ───────────────────────────────────────
    @http.route('/my/equipment/<int:equipment_id>',
                type='http', auth='user', website=True)
    def portal_equipment_detail(self, equipment_id, **kwargs):
        equipment = self._get_equipment(equipment_id)
        if not equipment:
            return request.not_found()
        inspections = equipment.inspection_ids.filtered(
            lambda i: i.state == 'done')
        return request.render('elevator_portal.portal_equipment_detail', {
            'equipment': equipment,
            'inspections': inspections,
            'contract': equipment.elevator_service_contract_id,
            'page_name': 'equipment',
        })

    # ── Inspection protocol PDF ──────────────────────────────────────────
    @http.route('/my/equipment/<int:equipment_id>/inspection/<int:inspection_id>/pdf',
                type='http', auth='user', website=True)
    def portal_inspection_pdf(self, equipment_id, inspection_id, **kwargs):
        equipment = self._get_equipment(equipment_id)
        if not equipment:
            return request.not_found()
        inspection = request.env[
            'maintenance.equipment.inspection'].browse(inspection_id)
        if (not inspection.exists()
                or inspection.equipment_id.id != equipment.id):
            return request.not_found()

        pdf_content, _unused = request.env['ir.actions.report'].sudo(
        )._render_qweb_pdf(
            'elevator_portal.report_inspection_protocol', [inspection_id])
        filename = 'Besiktningsprotokoll-%s.pdf' % (
            inspection.name.replace('/', '-'))
        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename="%s"' % filename),
            ],
        )
