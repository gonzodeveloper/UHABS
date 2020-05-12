from .nav_sim import transform_map, next_bearing
from .gps_sim import calculate_positions
from .comms import send, recv
from .driver import set_bearing
from .telemetry_sim import telem_sim

import numpy as np
NEW_BEARING = '0'
NEW_MAP = '1'


def control(conn, bearing, pos, dest, map):
    """
    Constantly sends current position, path, and telemetry to ground station
    Receives manual input for bearings and new current maps
    :param conn:
    :param bearing: angle defined with East as 0; float
    :param pos: (y, x) coordinate of module's present position; tuple
    :param dest: (y, x) coordinate of module's destination; tuple
    :param map: u(y, x), v(y, x) 2D component arrays for current values; np.dstack
    :return:
    """
    # Transform the present currents map to a graph
    graph = transform_map(map)
    while True:

        # Get flags of received signals
        flag, data = recv(conn)

        # If received signal is a new bearing, set new bearing to match.
        if flag == NEW_BEARING:
            bearing = data
            set_bearing(bearing)
            continue

        # If received signal is a new currents map, set new map to match
        elif flag == NEW_MAP:
            map = data
            graph = transform_map(map)

        # Recalculate position and bearing based off updated current map and bearing
        pos = calculate_positions(map, bearing, pos)
        bearing = next_bearing(graph, pos, dest)

        # Grab telemetry
        telemetry = telem_sim()

        # Send current bearing, position, and telemetry to ground station
        send(bearing, pos, telemetry)

    return
