# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MaintenanceEquipmentInspection(models.Model):
    """Act on the inspection result.

    The generic module records the remark level. This one writes it onto
    the elevator, because a red remark on an elevator is not a note — it is
    a legal requirement to stop using it.
    """

    _inherit = 'maintenance.equipment.inspection'

    is_elevator_inspection = fields.Boolean(
        related='equipment_id.is_elevator',
        string='Elevator Inspection',
    )
    elevator_inspection_remark = fields.Selection(
        selection=[
            ('none', 'No Remark'),
            ('remark', 'Remark'),
            ('red_remark', 'Red Remark'),
        ],
        string='Elevator Remark',
        compute='_compute_elevator_inspection_remark',
        store=True,
        help='The remark level written onto the elevator. Same as the '
             'generic level, kept separately so the elevator history is not '
             'rewritten when the generic field changes meaning.',
    )
    out_of_service_applied = fields.Boolean(
        string='Out of Service Applied',
        readonly=True,
        help='Set when a red remark was written onto the elevator.',
    )

    @api.depends('remark_level')
    def _compute_elevator_inspection_remark(self):
        for inspection in self:
            inspection.elevator_inspection_remark = inspection.remark_level

    def action_complete(self):
        """Complete the inspection, and stop the elevator if it went red.

        Done after super() so the state is already 'done' when the elevator
        is written: a half-completed inspection should not take an asset out
        of service.
        """
        result = super().action_complete()
        for inspection in self:
            if not inspection.equipment_id.is_elevator:
                continue
            if inspection.remark_level != 'red_remark':
                continue
            inspection._apply_out_of_service()
        return result

    def _apply_out_of_service(self):
        """Write the red remark onto the elevator.

        The reason and date are recorded because "why was it stopped, and
        since when?" is the first question asked afterwards — and the
        inspection number is the answer to "on what grounds?".
        """
        self.ensure_one()
        equipment = self.equipment_id
        equipment.write({
            'inspection_remark': 'red_remark',
            'inspection_number': self.name,
            'last_inspection': self.date,
            'operational_status': 'out_of_order',
            'out_of_order_reason': _(
                'Red remark at inspection %s', self.name),
            'out_of_order_date': self.date,
        })
        self.out_of_service_applied = True

    def action_reset_draft(self):
        """Reopening an inspection does not put the elevator back in service.

        Taking an elevator out of service is a physical act with a legal
        basis; undoing the protocol does not undo the fault. The elevator
        has to be released separately, by whoever fixed it.
        """
        return super().action_reset_draft()


class MaintenanceInspectionTemplate(models.Model):
    """Elevator inspection templates are tied to the elevator type."""

    _inherit = 'maintenance.inspection.template'

    elevator_type_id = fields.Many2one(
        'elevator.type',
        string='Elevator Type',
        help='Leave empty to apply to all elevator types.',
    )
    interval_months = fields.Integer(
        string='Inspection Interval (months)',
        default=12,
        help='BFS 2011:12 sets one year for most elevators and two for '
             'some. Set it per type rather than per elevator.',
    )

class ElevatorType(models.Model):
    """Inspection settings on the elevator type.

    BFS 2011:12 sets one year for most elevators and two for some. The
    interval belongs on the type, not on each elevator: 400 elevators of the
    same type share it.
    """

    _inherit = 'elevator.type'

    inspection_template_id = fields.Many2one(
        'maintenance.inspection.template',
        string='Inspection Template',
        help='Used when creating an inspection for an elevator of this type.',
    )
    inspection_interval_months = fields.Integer(
        string='Inspection Interval (months)',
        default=12,
    )
