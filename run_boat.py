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
    nav = ModuleNavigation(config['init_pos'], config['init_dest'], config['nav_timestep'], latlons, currents)
    telem = ModuleTelemetry()
    drivers = ModuleDrivers()

    # Initialize communications
    ground_station = config['gs_addr']
    port_list = config['ports']

    path_transmitter = Transmistter(ground_station, port_list['nav_path'])
    telem_transmitter = Transmistter(ground_station, port_list['telem'])
    gps_transmitter = Transmistter(ground_station, port_list['gps'])

    instr_az_comms  = Listener(ground_station, port_list['manual_az'])
    instr_prop_comms = Listener(ground_station, port_list['manual_prop'])
    new_map_listener = Listener(ground_station, port_list['maps'])


    # Start autonomous navigation
    Thread(target=auto_pilot, args=(nav, drivers, path_transmitter, telem)).start()

    # Send telemetry and gps
    Thread(target=telemetry_reports, args=(telem, telem_transmitter, config['telem_freq'])).start()
    Thread(target=location_reports, args=(telem, gps_transmitter, config['telem_freq'])).start()

    # Listen for new maps and instructions
    Thread(target=recieve_manual_directions, args=(drivers, instr_az_comms)).start()
    Thread(target=recieve_manual_propulsion, args=(drivers, instr_prop_comms)).start()
    Thread(target=recieve_new_maps, args=(nav, new_map_listener)).start()


def auto_pilot(nav, telem, drivers, comms, timestep):
    while nav.pos != nav.dest:
        az, path = nav.get_next_azimuth()

        drivers.set_azimuth(az)
        comms.send(path)
        nav.pos = telem.get_position()

        time.sleep(timestep)


def telemetry_reports(telem, comms, freq):
    while True:
        data = telem.get_temp()
        comms.send(data)
        time.sleep(freq)

def location_reports(telem, comms, freq):
    while True:
        data = telem.get_position()
        comms.send(data)
        time.sleep(freq)

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

