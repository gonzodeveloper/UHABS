from utils.file_io import read_netcdf
from utils.comms import Comms
from utils.visuals import plot_navigation

from threading import Thread
import yaml
import sys
import time
import numpy as np
import warnings
import logging


# Initialize global variables
temp = None
path = None
pos = None
dest = None

latlons = None
currents = None


def main(config):
    """

    :param config:
    :return:
    """

    global dest, latlons, currents

    # Get initial destination
    dest = config['destination']

    # Read the initial currents from file
    latlons, currents = read_netcdf(config['init_map'])

    # Initialize communications
    ground_station = config['gs_addr']
    port_list = config['ports']

    # Send new maps and manual instructions
    Thread(target=controls, args=(ground_station, port_list,)).start()

    # Receive telemetry, path, and GPS
    Thread(target=telem_list, args=(ground_station, port_list,)).start()
    Thread(target=path_list, args=(ground_station, port_list,)).start()
    Thread(target=gps_list, args=(ground_station, port_list,)).start()

    # Plotting
    Thread(target=visualize).start()


def controls(ground_station, port_list):
    """

    :param az_comms: holds azimuth inputs; float
    :param prop_comms: holds propulsion inputs; float
    :param map_comms: holds lat, longs, and current maps; tuple of numpy float32 arrays
    :return:
    """
    global latlons, currents

    print("Waiting for connection...")
    az_comms = Comms(ground_station, port_list['manual_az'], listener=True)
    prop_comms = Comms(ground_station, port_list['manual_prop'], listener=True)
    map_comms = Comms(ground_station, port_list['maps'], listener=True)

    while az_comms.conn is None and prop_comms.conn is None and map_comms.conn is None:
        pass

    print("Connected! ")
    # Initialize
    quit = False
    while not quit:

        # Prompt for additional instructions
        choice = input("Please input instruction type (AZ, PROP, MAP, QUIT): ")

        # Receive azimuth input and send
        if choice == "AZ":
            new_az = input("New azimuth: (degrees)")
            duration = input("Duration (seconds): ")

            packet = np.stack((new_az, duration))
            az_comms.send(packet)

        # Receive propulsion input and send
        elif choice == "PROP":
            new_prop = input("New propulsion setting (m/s): ")
            duration = input("Duration (seconds): ")

            packet = np.stack((new_prop, duration))
            prop_comms.send(packet)

        # Receive new map file input and send
        elif choice == "MAP":
            new_map = input("File path to new currents map (.netcdf file): ")
            latlons, currents = read_netcdf(new_map)
            map_stack = np.stack((latlons, currents))
            map_comms.send(map_stack)

        # Quit controls
        elif choice == "QUIT":
            quit = True

        else:
            print("Invalid Choice")

        print("\n")


def telem_list(ground_station, port_list):
    global temp

    telem_listener = Comms(ground_station, port_list['telem'], listener=True)

    while telem_listener.conn is None:
        pass

    # Constantly grab temperatures and assign to global variable
    while True:
        temp = telem_listener.recv()


def path_list(ground_station, port_list):
    global path

    path_listener = Comms(ground_station, port_list['nav_path'], listener=True)

    while path_listener.conn is None:
        pass

    # Grab path and assign to a global variable
    while True:
        print("NEW PATH")
        path = path_listener.recv()


def gps_list(ground_station, port_list):
    global pos

    gps_listener = Comms(ground_station, port_list['gps'], listener=True)
    while gps_listener.conn is None:
        pass

    # Grab GPS and assign to a global variable
    while True:
        pos = gps_listener.recv()


def visualize():
    global pos, path, temp, latlons, currents

    idx = 0
    while True:
        if path is None:
            continue
        plot_navigation(pos, dest, path, latlons, currents, temp, plot_idx=idx)
        idx += 1
        time.sleep(10)


if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    # Load configuration YAML
    with open(sys.argv[1]) as f:
        config = yaml.load(f)

    main(config)

