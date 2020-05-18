from .common_utils.file_io import read_netcdf
from .common_utils.comms import Transmistter, Listener
from .module_control_unit.nav import ModuleNavigation
from .module_control_unit.driver import ModuleDrivers
from .module_control_unit.telemetry import ModuleTelemetry

from threading import Thread
import yaml
import sys
import time
import numpy as np


def main(config):

	# Read the initial currents from file
	latlons, currents = read_netcdf(config['init_map'])

	# Initialize command modules
	nav = ModuleNavigation(config['nav_timestep'], latlons, currents)
	telem = ModuleTelemetry()
	drivers = ModuleDrivers()

	# Initialize communications
	ground_station = config['gs_addr']
	port_list = config['ports']

	path_transmitter = Listener(ground_station, port_list['nav_path'])
	telem_transmitter = Listener(ground_station, port_list['telem'])
	gps_transmitter = Listener(ground_station, port_list['gps'])

	instr_az_comms  = Transmistter(ground_station, port_list['manual_az'])
	instr_prop_comms = Transmistter(ground_station, port_list['manual_prop'])
	new_map_listener = Transmistter(ground_station, port_list['maps'])

def controls(comms)
	quit = False
	while not quit:
		choice = input("Please input instruction type (AZ, PROP, MAP): ")
		if choice == "AZ":
			new_az = input("Please input new azimuth: ")
			new_az = np.float32(new_az)
			comms.send(new_az)
		if choice == "PROP":
			new_prop = input("Please input new propulsion: ")
			new_prop = np.float32(new_prop)
			comms.send(new_prop)
		if choice == "MAP":
			new_map = input("Please input file location for new map: ")
			new_map_array = read_netcdf(new_map)
			comms.send(new_map_array)
		if choice == "quit":
			quit == True