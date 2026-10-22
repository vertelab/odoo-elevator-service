# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    """The elevator.

    An elevator is an asset with a maintenance history, so it is a
    maintenance.equipment record rather than a model of its own. Odoo
    already gives it requests, teams, technicians and a lifecycle; this adds
    what makes it an elevator.

    The statutory fields are not decoration: an elevator that has not been
    inspected on time is out of service by law, and the inspection remark
    level decides whether it may keep running. Modelling them means the
    system can say so instead of a spreadsheet.
    """

    _inherit = 'maintenance.equipment'

    is_elevator = fields.Boolean(
        string='Is Elevator',
        default=False,
        help='Marks this record as an elevator. Non-elevator equipment '
             'leaves the elevator fields empty.',
    )

    # ── Identity ───────────────────────────────────────────────────────
    elevator_number = fields.Char(
        string='Elevator Number',
        copy=False,
        help='The number the elevator is known by — on the nameplate, in '
             'the inspection register, on the service sticker.',
    )
    manufacturing_number = fields.Char(
        string='Manufacturing Number',
        help='The serial number from the manufacturer.',
    )
    manufacturing_year = fields.Integer(string='Year of Manufacture')
    number_of_stops = fields.Integer(string='Number of Stops')

    # ── Technical configuration ────────────────────────────────────────
    elevator_type_id = fields.Many2one(
        'elevator.type',
        string='Elevator Type',
    )
    drive_type = fields.Selection(
        selection=[
            ('traction', 'Traction'),
            ('hydraulic', 'Hydraulic'),
            ('machine_room_less', 'Machine Room Less'),
            ('screw', 'Screw Drive'),
            ('other', 'Other'),
        ],
        string='Drive Type',
    )
    control_system_id = fields.Many2one(
        'elevator.control.system',
        string='Control System',
    )
    car_door_type_id = fields.Many2one(
        'elevator.door.type',
        string='Car Door Type',
    )
    shaft_door_type_id = fields.Many2one(
        'elevator.door.type',
        string='Shaft Door Type',
    )

    # ── Statutory inspection ───────────────────────────────────────────
    last_inspection = fields.Date(string='Last Inspection')
    next_inspection_date = fields.Date(
        string='Next Inspection Due',
        help='Set by the inspection body. An elevator past this date may '
             'not be in service.',
    )
    inspection_company_id = fields.Many2one(
        'res.partner',
        string='Inspection Body',
        domain="[('is_company', '=', True)]",
    )
    inspection_number = fields.Char(string='Inspection Case Number')
    inspection_remark = fields.Selection(
        selection=[
            ('none', 'No Remark'),
            ('remark', 'Remark'),
            ('red_remark', 'Red Remark — Out of Service'),
        ],
        string='Inspection Remark',
        default='none',
        tracking=True,
        help='A red remark means the elevator must be taken out of service '
             'until the fault is fixed.',
    )

    # ── Operational status ─────────────────────────────────────────────
    operational_status = fields.Selection(
        selection=[
            ('operational', 'In Service'),
            ('out_of_order', 'Out of Order'),
            ('maintenance', 'Under Maintenance'),
            ('decommissioned', 'Decommissioned'),
        ],
        string='Operational Status',
        default='operational',
        tracking=True,
    )
    out_of_order_reason = fields.Char(string='Out of Order Reason')
    out_of_order_date = fields.Date(string='Out of Order Since')

    # ── Authorisation ──────────────────────────────────────────────────
    authorisation_scheme = fields.Char(
        string='Authorisation Scheme',
        help='The scheme this elevator is serviced under, e.g. BFS 2011:12.',
    )
    authorised_partner_id = fields.Many2one(
        'res.partner',
        string='Authorised Service Provider',
        domain="[('is_company', '=', True)]",
    )

    # ── Service interval ───────────────────────────────────────────────
    service_interval_months = fields.Integer(
        string='Service Interval (months)',
        default=12,
        help='How often the service agreement says this elevator is visited.',
    )
    last_service_date = fields.Date(string='Last Service')
    next_service_date = fields.Date(
        string='Next Service Due',
        compute='_compute_next_service_date',
        store=True,
    )

    # ── Lifecycle ──────────────────────────────────────────────────────
    lifecycle_stage = fields.Selection(
        selection=[
            ('ok', 'OK'),
            ('inspection_due', 'Inspection Due'),
            ('inspection_overdue', 'Inspection Overdue'),
            ('service_due', 'Service Due'),
            ('out_of_service', 'Out of Service'),
            ('decommissioned', 'Decommissioned'),
        ],
        string='Lifecycle Stage',
        compute='_compute_lifecycle_stage',
        store=True,
        help='Derived from the inspection and service dates. An elevator '
             'past its inspection date is out of service by law, whatever '
             'the operational status says.',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.depends('last_service_date', 'service_interval_months')
    def _compute_next_service_date(self):
        for equipment in self:
            if not equipment.last_service_date or not equipment.service_interval_months:
                equipment.next_service_date = False
                continue
            equipment.next_service_date = fields.Date.add(
                equipment.last_service_date,
                months=equipment.service_interval_months,
            )

    @api.depends(
        'operational_status',
        'next_inspection_date',
        'next_service_date',
        'inspection_remark',
    )
    def _compute_lifecycle_stage(self):
        today = fields.Date.context_today(self)
        for equipment in self:
            if equipment.operational_status == 'decommissioned':
                equipment.lifecycle_stage = 'decommissioned'
                continue
            if (equipment.inspection_remark == 'red_remark'
                    or equipment.operational_status == 'out_of_order'):
                equipment.lifecycle_stage = 'out_of_service'
                continue
            if equipment.next_inspection_date:
                if equipment.next_inspection_date < today:
                    equipment.lifecycle_stage = 'inspection_overdue'
                    continue
                if (equipment.next_inspection_date - today).days <= 60:
                    equipment.lifecycle_stage = 'inspection_due'
                    continue
            if equipment.next_service_date and equipment.next_service_date < today:
                equipment.lifecycle_stage = 'service_due'
                continue
            equipment.lifecycle_stage = 'ok'

    def action_set_out_of_order(self):
        """Take the elevator out of service.

        Used when a red inspection remark comes in, or when a technician
        finds something that cannot wait. The reason and date are recorded
        because "why was it stopped, and since when?" is the first question
        asked afterwards.
        """
        for equipment in self:
            equipment.write({
                'operational_status': 'out_of_order',
                'out_of_order_date': fields.Date.context_today(equipment),
            })

    def action_set_operational(self):
        for equipment in self:
            equipment.write({
                'operational_status': 'operational',
                'out_of_order_reason': False,
                'out_of_order_date': False,
            })


class ElevatorType(models.Model):
    """Elevator type — the classification used for checklists and pricing."""

    _name = 'elevator.type'
    _description = 'Elevator Type'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    description = fields.Text()
    active = fields.Boolean(default=True)


class ElevatorControlSystem(models.Model):
    _name = 'elevator.control.system'
    _description = 'Elevator Control System'
    _order = 'name'

    name = fields.Char(required=True)
    manufacturer = fields.Char()
    active = fields.Boolean(default=True)


class ElevatorDoorType(models.Model):
    _name = 'elevator.door.type'
    _description = 'Elevator Door Type'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
