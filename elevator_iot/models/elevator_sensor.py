# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ElevatorSensor(models.Model):
    """A measured value on an elevator.

    The connector writes readings here; thresholds and alarms are handled
    by this model. Keeping the two apart means a new gateway protocol only
    needs to call add_reading() — it does not need to know what an alarm is.
    """

    _name = 'elevator.sensor'
    _description = 'Elevator Sensor'
    _inherit = ['mail.thread']
    _order = 'equipment_id, sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Elevator',
        required=True,
        index=True,
        ondelete='cascade',
        domain="[('is_elevator', '=', True)]",
    )
    sensor_type = fields.Selection(
        selection=[
            ('door_cycles', 'Door Cycles'),
            ('run_hours', 'Run Hours'),
            ('fault_code', 'Fault Code'),
            ('state', 'Car State'),
            ('temperature', 'Machine Temperature'),
            ('vibration', 'Vibration'),
            ('other', 'Other'),
        ],
        string='Sensor Type',
        required=True,
        default='other',
    )
    unit = fields.Char(help='Cycles, hours, °C, mm/s — whatever the sensor '
                            'reports in.')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    # ── Thresholds ─────────────────────────────────────────────────────
    threshold_direction = fields.Selection(
        selection=[
            ('above', 'Above'),
            ('below', 'Below'),
        ],
        string='Alarm When',
        default='above',
        help='Whether a high or a low value is the problem. Run hours and '
             'temperature alarm above; a car state might alarm below.',
    )
    warning_threshold = fields.Float(
        string='Warning Threshold',
        help='Crossing this raises a notification. 0 = no warning.',
    )
    critical_threshold = fields.Float(
        string='Critical Threshold',
        help='Crossing this opens a work order. 0 = no critical alarm.',
    )

    # ── Latest reading ─────────────────────────────────────────────────
    last_value = fields.Float(
        string='Last Value',
        compute='_compute_last_reading',
        store=True,
    )
    last_reading_date = fields.Datetime(
        string='Last Reading',
        compute='_compute_last_reading',
        store=True,
    )
    sensor_state = fields.Selection(
        selection=[
            ('ok', 'OK'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
            ('no_data', 'No Data'),
        ],
        string='State',
        compute='_compute_last_reading',
        store=True,
    )
    reading_ids = fields.One2many(
        'elevator.sensor.reading',
        'sensor_id',
        string='Readings',
    )
    reading_count = fields.Integer(compute='_compute_reading_count')

    @api.depends('reading_ids', 'reading_ids.value', 'reading_ids.timestamp',
                 'threshold_direction', 'warning_threshold', 'critical_threshold')
    def _compute_last_reading(self):
        for sensor in self:
            latest = sensor.reading_ids.sorted('timestamp', reverse=True)[:1]
            if not latest:
                sensor.last_value = 0.0
                sensor.last_reading_date = False
                sensor.sensor_state = 'no_data'
                continue
            sensor.last_value = latest.value
            sensor.last_reading_date = latest.timestamp
            sensor.sensor_state = sensor._evaluate(latest.value)

    @api.depends('reading_ids')
    def _compute_reading_count(self):
        for sensor in self:
            sensor.reading_count = len(sensor.reading_ids)

    def _evaluate(self, value):
        """Which state a value puts the sensor in.

        Above/below is a per-sensor choice: run hours alarm when high, a
        pressure sensor might alarm when low. A threshold of 0 means "not
        set" — a sensor with no critical threshold never goes critical.
        """
        self.ensure_one()
        if self.threshold_direction == 'below':
            if self.critical_threshold and value < self.critical_threshold:
                return 'critical'
            if self.warning_threshold and value < self.warning_threshold:
                return 'warning'
        else:
            if self.critical_threshold and value > self.critical_threshold:
                return 'critical'
            if self.warning_threshold and value > self.warning_threshold:
                return 'warning'
        return 'ok'

    def add_reading(self, value, timestamp=None):
        """Record a measurement. The connector calls this.

        Returns the reading. Alarms are raised here rather than in the
        connector: the connector's job is to deliver the number, not to
        decide what it means.
        """
        self.ensure_one()
        reading = self.env['elevator.sensor.reading'].create({
            'sensor_id': self.id,
            'value': value,
            'timestamp': timestamp or fields.Datetime.now(),
        })
        state = self._evaluate(value)
        if state == 'critical':
            self._raise_critical(reading)
        elif state == 'warning':
            self._raise_warning(reading)
        return reading

    def _raise_warning(self, reading):
        self.ensure_one()
        self.message_post(body=_(
            'Sensor %(sensor)s reported %(value)s %(unit)s — above the '
            'warning threshold.',
            sensor=self.name, value=reading.value, unit=self.unit or ''))

    def _raise_critical(self, reading):
        """Open a work order: a critical reading is a fault waiting to happen.

        Not a notification — a critical reading on an elevator means someone
        has to go there. The reading is recorded on the order so the
        technician sees the value, not just the fact that something happened.
        """
        self.ensure_one()
        if reading.fieldservice_order_id:
            return reading.fieldservice_order_id

        order_type = self.env['fieldservice.order.type'].search(
            [('name', 'ilike', 'repair')], limit=1)
        vals = {
            'name': _('Alarm: %(sensor)s on %(elevator)s', sensor=self.name,
                      elevator=self.equipment_id.display_name),
            'equipment_id': self.equipment_id.id,
            'partner_id': self.equipment_id.partner_id.id,
            'description': _(
                'Sensor %(sensor)s reported %(value)s %(unit)s at '
                '%(time)s.\nCritical threshold: %(threshold)s.',
                sensor=self.name, value=reading.value, unit=self.unit or '',
                time=reading.timestamp, threshold=self.critical_threshold),
        }
        if order_type:
            vals['product_type'] = order_type.id
        order = self.env['fieldservice.order'].create(vals)
        reading.fieldservice_order_id = order
        return order


class ElevatorSensorReading(models.Model):
    """One measurement.

    Kept rather than overwritten: the trend is the point. A door that has
    done 40 000 cycles in a year is a door that needs adjustment, and that
    is only visible if the readings are kept.
    """

    _name = 'elevator.sensor.reading'
    _description = 'Elevator Sensor Reading'
    _order = 'timestamp desc, id desc'

    sensor_id = fields.Many2one(
        'elevator.sensor',
        required=True,
        ondelete='cascade',
        index=True,
    )
    value = fields.Float(required=True)
    timestamp = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    fieldservice_order_id = fields.Many2one(
        'fieldservice.order',
        string='Work Order',
        ondelete='set null',
        readonly=True,
        help='Opened by this reading, if it crossed the critical threshold.',
    )
