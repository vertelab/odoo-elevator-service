# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    """Sensors as seen from the elevator."""

    _inherit = 'maintenance.equipment'

    sensor_ids = fields.One2many(
        'elevator.sensor',
        'equipment_id',
        string='Sensors',
    )
    sensor_count = fields.Integer(compute='_compute_sensor_stats', store=True)
    sensor_critical_count = fields.Integer(
        compute='_compute_sensor_stats', store=True)
    sensor_state = fields.Selection(
        selection=[
            ('ok', 'OK'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
            ('no_data', 'No Data'),
        ],
        string='Sensor State',
        compute='_compute_sensor_stats',
        store=True,
        help='The worst state among the elevator\'s sensors.',
    )

    @api.depends('sensor_ids', 'sensor_ids.sensor_state')
    def _compute_sensor_stats(self):
        for equipment in self:
            sensors = equipment.sensor_ids
            equipment.sensor_count = len(sensors)
            critical = sensors.filtered(lambda s: s.sensor_state == 'critical')
            equipment.sensor_critical_count = len(critical)
            if critical:
                equipment.sensor_state = 'critical'
            elif sensors.filtered(lambda s: s.sensor_state == 'warning'):
                equipment.sensor_state = 'warning'
            elif sensors:
                equipment.sensor_state = 'ok'
            else:
                equipment.sensor_state = 'no_data'

    def action_view_sensors(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Sensors — %s', self.name),
            'res_model': 'elevator.sensor',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }
