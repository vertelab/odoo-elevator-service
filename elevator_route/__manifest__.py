# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'website': 'https://vertel.se/apps/odoo-elevator-service/elevator_route',
    'name': 'Elevator Route — Ruttplanering',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'license': 'AGPL-3',
    'summary': 'Plan a technician day: route order, travel time, map view',
    'description': '''
Elevator Route — Ruttplanering
==============================

    A technician's day, ordered.

    A service company with 400 elevators in a city does not send a
    technician to one address at a time. It plans a day: five or six stops,
    in an order that minimises driving. Odoo has the work orders and the
    map; what it lacks is the sequence and the travel time between stops.

    What this adds to fieldservice.order:

        routing_sequence       where in the day this stop falls
        estimated_arrival      when the technician gets there
        travel_time_minutes    from the previous stop

    Plus a map view showing the day's stops in order, so the planner can
    see whether the route doubles back.

    Why the sequence is manual
    --------------------------
    Automatic route optimisation needs a distance matrix — an external
    service or a self-hosted OSRM. That is a deployment decision, not
    something a module should assume. The sequence is therefore set by the
    planner, and the module computes arrival times from it: departure plus
    travel plus service time per stop.

    A company that later adds a routing service can fill the sequence
    automatically; the rest of the module does not change.

    Features:

        - Route sequence, ETA and travel time on work orders
        - Arrival times computed forward from a day's start
        - Map view of the day's stops in order
        - "Plan route" action that sequences the selected orders
    ''',
    'category': 'Elevator Service',
    'depends': [
        'elevator_base',
        'elevator_contract',
        'fieldservice_vrtl',
        'web_map_ce',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fieldservice_order_views.xml',
        'views/route_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
