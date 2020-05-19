from utils.file_io import read_netcdf
from utils.comms import Comms
from module_control_unit.nav import ModuleNavigation
from module_control_unit.driver import ModuleDrivers
from module_control_unit.telemetry import ModuleTelemetry

from threading import Thread
import yaml
import sys
import time
import warnings
import logging

# Set logger
logger = logging.getLogger('boat_logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('./logs/boat.log')
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
logger.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)


def main(config):

    # Read the initial currents from file
    latlons, currents = read_netcdf(config['init_map'])

    # Initialize command modules
    nav = ModuleNavigation(config['nav_timestep'], latlons, currents)
    telem = ModuleTelemetry()
    drivers = ModuleDrivers()

    drivers.set_propulsion(config['init_propulstion'])

    # Initialize communications
    ground_station = config['gs_addr']
    port_list = config['ports']

    path_comms = Comms(ground_station, port_list['nav_path'])
    telem_comms = Comms(ground_station, port_list['telem'])
    gps_comms = Comms(ground_station, port_list['gps'])

    instr_az_comms = Comms(ground_station, port_list['manual_az'])
    instr_prop_comms = Comms(ground_station, port_list['manual_prop'])
    new_map_comms = Comms(ground_station, port_list['maps'])

    # Start autonomous navigation
    Thread(target=auto_pilot, args=(config['init_pos'],
                                    config['destination'],
                                    nav,
                                    telem,
                                    drivers,
                                    path_comms,
                                    gps_comms,
                                    config['nav_timestep'],
                                    config['sim_speedup_factor'])).start()

    # Send telemetry and gps
    Thread(target=telemetry_reports, args=(telem, telem_comms,
                                           config['telem_freq'], config['sim_speedup_factor'])).start()

    # Listen for new maps and instructions
    Thread(target=recieve_manual_directions, args=(drivers, instr_az_comms)).start()
    Thread(target=recieve_manual_propulsion, args=(drivers, instr_prop_comms)).start()
    Thread(target=recieve_new_maps, args=(nav, new_map_comms)).start()

    # Logging
    logging.info("")


def auto_pilot(init_pos, dest, nav, telem, drivers, path_trans, gps_trans, timestep, sim_speedup_factor=1):

    global logger
    pos = init_pos

    while pos != dest:

        # Calculate the shortest path given our position and destination
        az, path = nav.get_next_azimuth(pos, dest)
        logger.info(f"Path recalculated.")

        # Set the bearing of the craft
        bearing = drivers.set_azimuth(az)
        logger.info(f"Azimuth set: {bearing:.2f}")

        # Get the ocean current at our position
        current = nav.get_current(pos)
        logger.info(f"Ocean current at position acquired.")

        # Get module's propulsion
        prop = drivers.get_propulsion()
        logger.info(f"Propulsion: {prop}")

        # Next position is determined by our position, speed, dir, ocean current, and time elapsed
        pos = telem.get_position(pos, current, az, prop, timestep)
        logger.info(f"GPS updated. GPS transmitted: {pos[0]:.4f} N {pos[1]:.4f} E")

        # Transmit data
        gps_trans.send(pos)
        path_trans.send(path)
        logger.info("Path and GPS sent.")

        time.sleep(timestep / sim_speedup_factor)


def telemetry_reports(telem, comms, freq, sim_speedup_factor):
    global logger
    while True:
        # Sample the temperature of the module (simulated)
        data = telem.get_temp()

        # Report to ground station
        comms.send(data)
        logger.info(f"Telemetry sent: {data:.4f}")
        time.sleep(freq / sim_speedup_factor)


def recieve_manual_directions(drivers, comms):
    global logger
    while True:
        # Wait for manual directions from the ground station
        packet = comms.recv()
        az, duration = packet[0], packet[1]

        # Force set drivers for manual direction
        drivers.set_azimuth(az, force_duration=duration)
        logger.info(f"Manual direction command received. Azimuth set to {az} for duration {duration}.")


def recieve_manual_propulsion(drivers, comms):
    global logger
    while True:
        # Wait for manual propulsion from the ground station
        packet = comms.recv()
        speed, duration = packet[0], packet[1]

        # Force set drivers for manual propulsion
        drivers.set_propulsion(speed, force_duration=duration)
        logger.info(f"Manual propulsion command received. Speed set to {speed} for duration {duration}.")


def recieve_new_maps(nav, comms):
    while True:
        # Wait for new currents map from ground station
        latlons, currents = comms.recv()
        logger.info(f"New current map receieved.")

        # Update currents map
        nav.set_currents_map(latlons, currents)


if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    # Load configuration YAML
    with open(sys.argv[1]) as f:
        config = yaml.load(f)

    main(config)

