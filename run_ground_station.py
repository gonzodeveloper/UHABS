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

# Initialize global variables
temp = 0
path = 0
gps = [0, 0]


def main(config):
	"""

	:param config:
	:return:
	"""
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

	path_listener = Listener(boat, port_list['nav_path'])
	telem_listener = Listener(boat, port_list['telem'])
	gps_listener = Listener(boat, port_list['gps'])

	instr_az_transmitter = Transmistter(ground_station, port_list['manual_az'])
	instr_prop_transmitter = Transmistter(ground_station, port_list['manual_prop'])
	new_map_transmitter = Transmistter(ground_station, port_list['maps'])

	# Send new maps and manual instructions
	Thread(target=controls, args=(instr_az_transmitter, instr_prop_transmitter, new_map_transmitter,)).start()

	# Receive telemetry, path, and GPS
	Thread(target=telem_list, args=(telem_listener,)).start()
	Thread(target=path_list, args=(path_listener,)).start()
	Thread(target=gps_list, args=(gps_listener,)).start()


<<<<<<< HEAD:run_ground_station.py

def controls(comms):
=======
def controls(az_comms, prop_comms, map_comms):
	"""

	:param az_comms: holds azimuth inputs; float
	:param prop_comms: holds propulsion inputs; float
	:param map_comms: holds lat, longs, and current maps; tuple of numpy float32 arrays
	:return:
	"""
>>>>>>> af10c8e360a0e0d856be871f64df38e638fb0a33:ground_station.py

	# Initialize
	quit = False
	while not quit:

		# Prompt for additional instructions
		choice = input("Please input instruction type (AZ, PROP, MAP): ")

		# Receive azimuth input and send
		if choice == "AZ":
			new_az = input("Please input new azimuth: ")
			new_az = np.float32(new_az)
			az_comms.send(new_az)
			print("You just sent {}.".format('new_az'))

		# Receive propulsion input and send
		elif choice == "PROP":
			new_prop = input("Please input new propulsion: ")
			new_prop = np.float32(new_prop)
			prop_comms.send(new_prop)
			print("You just sent {}.".format('new_prop'))

		# Receive new map file input and send
		elif choice == "MAP":
			new_map = input("Please input file location for new map: ")
			latlons, currents = read_netcdf(new_map)
			map_stack = np.stack((latlons, currents))
			map_comms.send(map_stack)
			print("You just sent {}.".format('new_map'))

		# Quit controls
		elif choice == "quit":
			quit = True

		else:
			print("Invalid Choice")

	print()


def telem_list(telem_listener):

	# Constantly grab temperatures and assign to global variable
	global temp
	while True:
		temp = telem_listener.recv()


def path_list(path_listener):

	# Grab path and assign to a global variable
	global path
	while True:
		path = path_listener.recv()


def gps_list(gps_listener):

	# Grab GPS and assign to a global variable
	global gps
	while True:
		gps = gps_listener.recv()

