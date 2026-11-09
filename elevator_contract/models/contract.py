# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ContractContract(models.Model):
    """The service agreement.

    contract.contract already owns the recurrence, the invoicing and the
    renewal. This adds what an elevator service agreement has that a generic
    contract does not: which elevator, how often the technician comes, and
    how fast the company has to respond.
    """

    _inherit = 'contract.contract'

    is_elevator_contract = fields.Boolean(
        string='Elevator Service Agreement',
        default=False,
    )
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Elevator',
        domain="[('is_elevator', '=', True)]",
        index=True,
        tracking=True,
        help='The elevator this agreement covers.',
    )
    visits_per_year = fields.Integer(
        string='Visits per Year',
        default=1,
        tracking=True,
        help='How often the technician comes. Drives the maintenance plan.',
    )
    response_time_hours = fields.Integer(
        string='Response Time (hours)',
        tracking=True,
        help='Contractual response time for a call-out. A broken elevator '
             'with someone inside is not the same as a squeaking door.',
    )
    includes_inspection = fields.Boolean(
        string='Includes Statutory Inspection',
        default=False,
        tracking=True,
        help='Whether the statutory BFS inspection is part of this '
             'agreement or billed separately.',
    )
    coverage = fields.Selection(
        selection=[
            ('full', 'Full Service'),
            ('parts', 'Service and Parts'),
            ('labour', 'Labour Only'),
            ('emergency', 'Emergency Call-out Only'),
        ],
        string='Coverage',
        default='full',
        tracking=True,
    )

    @api.constrains('equipment_id', 'is_elevator_contract')
    def _check_one_active_per_elevator(self):
        """One active agreement per elevator.

        Two active agreements on the same elevator bill it twice and send
        the technician two orders for the same visit. The check runs on
        both fields because an agreement can become an elevator agreement
        after it was created.
        """
        for contract in self:
            if not contract.is_elevator_contract or not contract.equipment_id:
                continue
            if not contract.active:
                continue
            others = self.search([
                ('id', '!=', contract.id),
                ('equipment_id', '=', contract.equipment_id.id),
                ('is_elevator_contract', '=', True),
                ('active', '=', True),
            ])
            if others:
                raise ValidationError(_(
                    'Elevator %(elevator)s already has an active service '
                    'agreement: %(contract)s. Terminate it first.',
                    elevator=contract.equipment_id.display_name,
                    contract=others[0].display_name,
                ))

    @api.model_create_multi
    def create(self, vals_list):
        """Refresh the elevator's agreement pointer after creating.

        The compute on maintenance.equipment depends on service_contract_ids,
        but that One2many is on the equipment side: creating a contract does
        not invalidate the equipment's cache, so the pointer stays empty
        until something else touches it.
        """
        contracts = super().create(vals_list)
        contracts._refresh_equipment_contract()
        return contracts

    def write(self, vals):
        result = super().write(vals)
        if {'equipment_id', 'active', 'is_elevator_contract'} & set(vals):
            self._refresh_equipment_contract()
        return result

    def _refresh_equipment_contract(self):
        for equipment in self.mapped('equipment_id'):
            equipment.invalidate_recordset(['elevator_service_contract_id'])
            equipment._compute_elevator_service_contract()

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        """Flag it and prefill the customer from the elevator's owner."""
        if self.equipment_id:
            self.is_elevator_contract = True
            if not self.partner_id and self.equipment_id.partner_id:
                self.partner_id = self.equipment_id.partner_id


class MaintenanceEquipment(models.Model):
    """The agreement as seen from the elevator."""

    _inherit = 'maintenance.equipment'

    # No domain on the One2many: a domain filters what the form shows but
    # makes @api.depends on the field unreliable, and the compute below
    # searched anyway. The view filters on is_elevator_contract instead.
    service_contract_ids = fields.One2many(
        'contract.contract',
        'equipment_id',
        string='Service Agreements',
    )
    elevator_service_contract_id = fields.Many2one(
        'contract.contract',
        string='Active Service Agreement',
        compute='_compute_elevator_service_contract',
    )
    # Computed rather than related: a related field resolves at model
    # setup, and contract.contract is extended in the same module. Odoo
    # then fails with "Field visits_per_year ... does not exist" because
    # the source field is not registered yet when maintenance.equipment is
    # set up.
    contract_visits_per_year = fields.Integer(
        string='Visits per Year',
        compute='_compute_contract_service_level',
    )
    contract_response_time_hours = fields.Integer(
        string='Response Time (hours)',
        compute='_compute_contract_service_level',
    )

    @api.depends('service_contract_ids', 'service_contract_ids.active',
                 'service_contract_ids.is_elevator_contract')
    def _compute_elevator_service_contract(self):
        """Find the active agreement for this elevator.

        Searched rather than read from service_contract_ids: that field has
        a domain, and a domain filters what the form shows without
        guaranteeing the compute sees the same records.
        """
        Contract = self.env['contract.contract']
        for equipment in self:
            equipment.elevator_service_contract_id = Contract.search([
                ('equipment_id', '=', equipment.id),
                ('is_elevator_contract', '=', True),
                ('active', '=', True),
            ], limit=1)

    @api.depends('elevator_service_contract_id')
    def _compute_contract_service_level(self):
        for equipment in self:
            contract = equipment.elevator_service_contract_id
            equipment.contract_visits_per_year = (
                contract.visits_per_year if contract else 0)
            equipment.contract_response_time_hours = (
                contract.response_time_hours if contract else 0)

    def action_view_service_contracts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Service Agreements — %s', self.name),
            'res_model': 'contract.contract',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {
                'default_equipment_id': self.id,
                'default_is_elevator_contract': True,
            },
        }


class ProductTemplate(models.Model):
    """Which contract template a product sells.

    A service product is not just a price: selling it should create a
    contract with the right recurrence, the right lines and the right
    terms. OCA's contract.template already carries that, and
    contract.contract.contract_template_id already fills a contract from
    it. What is missing is the link from the product, so the salesperson
    does not have to remember which template belongs to which service.
    """

    _inherit = 'product.template'

    elevator_contract_template_id = fields.Many2one(
        'contract.template',
        string='Contract Template',
        domain="[('contract_type', '=', 'sale')]",
        help='The contract template this product creates when it is sold '
             'as a service agreement. Leave empty for products that do not '
             'sell a contract.',
    )

class SaleOrderLine(models.Model):
    """Selling a service product creates the agreement.

    The product names its contract template; confirming a sale order with
    such a line creates the contract from it. This is where OCA's
    contract.template actually pays off — the recurrence and the lines come
    from the template, not from a second implementation.
    """

    _inherit = 'sale.order.line'

    def _prepare_elevator_contract_vals(self):
        """Contract values from the line and its template."""
        self.ensure_one()
        template = self.product_id.product_tmpl_id.elevator_contract_template_id
        if not template:
            return False
        return {
            'name': '%s - %s' % (self.order_id.name, self.product_id.name),
            'partner_id': self.order_id.partner_id.id,
            'company_id': self.order_id.company_id.id,
            'contract_template_id': template.id,
            'is_elevator_contract': True,
        }

    def _create_elevator_contract(self):
        """Create the agreement for this line, once."""
        self.ensure_one()
        Contract = self.env['contract.contract']
        existing = Contract.search([
            ('name', '=', '%s - %s' % (self.order_id.name, self.product_id.name)),
            ('partner_id', '=', self.order_id.partner_id.id),
        ], limit=1)
        if existing:
            return existing
        vals = self._prepare_elevator_contract_vals()
        if not vals:
            return False
        contract = Contract.create(vals)
        # The template's lines are copied by the onchange, which does not
        # run on create. Replay it so the contract is not born empty.
        contract._onchange_contract_template_id()
        return contract
