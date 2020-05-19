from .common_utils.file_io import read_netcdf
from .common_utils.comms import Transmistter, Listener
from .module_control_unit.nav import ModuleNavigation
from .module_control_unit.driver import ModuleDrivers
from .module_control_unit.telemetry import ModuleTelemetry

from threading import Thread
import yaml
import sys
import time


def main(config):

    # Read the initial currents from file
    latlons, currents = read_netcdf(config['init_map'])

    # Initialize command modules
    nav = ModuleNavigation(config['nav_timestep'], latlons, currents)
    telem = ModuleTelemetry()
    drivers = ModuleDrivers()

    # Initialize communications
    boat = config['boat_addr']
    ground_station = config['gs_addr']
    port_list = config['ports']

    path_transmitter = Transmistter(ground_station, port_list['nav_path'])
    telem_transmitter = Transmistter(ground_station, port_list['telem'])
    gps_transmitter = Transmistter(ground_station, port_list['gps'])

    instr_az_comms  = Listener(boat, port_list['manual_az'])
    instr_prop_comms = Listener(boat, port_list['manual_prop'])
    new_map_listener = Listener(boat, port_list['maps'])

    # Start autonomous navigation
    Thread(target=auto_pilot, args=(config['init_pos'],
                                    config['destination'],
                                    nav,
                                    telem,
                                    drivers,
                                    path_transmitter,
                                    gps_transmitter,
                                    config['nav_timestep'],
                                    config['sim_speedup_factor'])).start()

    # Send telemetry and gps
    Thread(target=telemetry_reports, args=(telem, telem_transmitter, config['telem_freq'])).start()

    # Listen for new maps and instructions
    Thread(target=recieve_manual_directions, args=(drivers, instr_az_comms)).start()
    Thread(target=recieve_manual_propulsion, args=(drivers, instr_prop_comms)).start()
    Thread(target=recieve_new_maps, args=(nav, new_map_listener)).start()


def auto_pilot(init_pos, dest, nav, telem, drivers, path_trans, gps_trans, timestep, sim_speedup_factor=1):
    pos = init_pos

    while pos != dest:

        # Calculate the shortest path given our position and destination
        az, path = nav.get_next_azimuth(pos, dest)

        # Set the bearing of the craft
        drivers.set_azimuth(az)

        # Get the ocean current at our position
        current = nav.get_current(pos)
        # Get module's propulsion
        prop = drivers.get_propulsion()

        # Next position is determined by our position, speed, dir, ocean currrent, and time elapsed
        pos = telem.get_position(pos, current, az, prop, timestep)

        # Transmit data
        gps_trans.send(pos)
        path_trans.send(path)


        time.sleep(timestep / sim_speedup_factor)


def telemetry_reports(telem, comms, freq, sim_speedup_factor):
    while True:
        data = telem.get_temp()
        comms.send(data)
        time.sleep(freq / sim_speedup_factor)


def recieve_manual_directions(drivers, comms):
    while True:
        az, duration = comms.recv()
        drivers.set_azimuth(az, force_duration=duration)


def recieve_manual_propulsion(drivers, comms):
    while True:
        speed, duration = comms.recv()
        drivers.set_propulsion(speed, force_duration=duration)


def recieve_new_maps(nav, comms):
    while True:
        latlons, currents = comms.recv()
        nav.set_currents_map(latlons, currents)


if __name__ == '__main__':
    # Load configuration YAML
    with open(sys.argv[1]) as f:
        config = yaml.load(f)

    main(config)

