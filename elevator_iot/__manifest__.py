# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_iot',
    'name': 'Elevator IoT — Hissövervakning',
    'version': '18.0.1.0.4',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'Sensor readings, alarm thresholds and automatic fault orders',
    'description': '''
Elevator IoT — Hissövervakning
==============================

    A modern elevator reports its own state: door cycles, run hours, fault
    codes, whether the car is moving. That stream is the difference between
    a service company that finds out an elevator is stuck when the tenant
    calls, and one that sends a technician before anyone notices.

    This module is the receiving end: sensors on the elevator, readings over
    time, thresholds that raise an alarm, and an alarm that opens a work
    order.

    What it does not do is talk to the hardware. Every gateway speaks its
    own protocol — Modbus, MQTT, a vendor cloud API. That belongs in a
    connector, and a connector per vendor. This module defines the model
    the connector writes into:

        elevator.sensor          a measured value on an elevator
        elevator.sensor.reading  one measurement, with a timestamp

    A connector calls sensor.add_reading(value) and the rest — thresholds,
    alarms, work orders — happens here.

    A sensor carries a warning and a critical threshold, and a direction
    (above or below). Crossing the warning raises a notification; crossing
    the critical opens a work order, because a critical reading on an
    elevator is a stopped elevator waiting to happen.

    The reading that triggered an alarm is recorded on the alarm, so the
    technician sees the value, not just the fact that something happened.

    Features:

        - Sensors per elevator: door cycles, run hours, fault codes, state
        - Readings with timestamp, kept for trend
        - Warning and critical thresholds, configurable per sensor
        - Alarm raises a notification or a work order
        - Sensor state visible on the elevator
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        # Sensors on an asset are generic: maintenance_iot owns the model,
        # the thresholds and the alarm-to-request logic. This module adds
        # what is specific to elevator monitoring.
        'maintenance_iot',
    ],
    'data': [
        'views/iot_menu.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
