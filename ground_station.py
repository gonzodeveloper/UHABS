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
	boat = config['boat_addr']
	port_list = config['ports']

	path_transmitter = Listener(boat, port_list['nav_path'])
	telem_transmitter = Listener(boat, port_list['telem'])
	gps_transmitter = Listener(boat, port_list['gps'])

	instr_az_comms  = Transmistter(ground_station, port_list['manual_az'])
	instr_prop_comms = Transmistter(ground_station, port_list['manual_prop'])
	new_map_listener = Transmistter(ground_station, port_list['maps'])

def controls(comms):

	# Initialize
	quit = False
	while not quit:

		# Prompt for additional instructions
		choice = input("Please input instruction type (AZ, PROP, MAP): ")

		# Receive azimuth input and send
		if choice == "AZ":
			new_az = input("Please input new azimuth: ")
			new_az = np.float32(new_az)
			# comms.send(new_az)
			print("You just sent {}.".format('new_az'))

		# Receive propulsion input and send
		elif choice == "PROP":
			new_prop = input("Please input new propulsion: ")
			new_prop = np.float32(new_prop)
			# comms.send(new_prop)
			print("You just sent {}.".format('new_prop'))

		# Receive new map file input and send
		elif choice == "MAP":
			new_map = input("Please input file location for new map: ")
			latlons, currents = read_netcdf(new_map)
                        map_stack = np.stack((latlons, currents))
			# comms.send(map_stack)
			print("You just sent {}.".format('new_map'))

		# Quit controls
		elif choice == "quit":
			quit == True

                else:
                    print("Invalid Choice")

                print()
