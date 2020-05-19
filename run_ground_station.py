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

logger = logging.getLogger('gs_logger')


def main(config):
    """

    :param config:
    :return:
    """
    global logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('./logs/gs.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    logger.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
    global latlons, currents, logger

    print("Waiting for connection...")
    az_comms = Comms(ground_station, port_list['manual_az'], listener=True)
    logger.info("Azimuth transmitter connected.")
    prop_comms = Comms(ground_station, port_list['manual_prop'], listener=True)
    logger.info("Propulsion transmitter connected.")
    map_comms = Comms(ground_station, port_list['maps'], listener=True)
    logger.info("Current map transmitter connected.")

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
            logger.info(f"Manual azimuth inputted. Azimuth: {new_az}.")
            duration = input("Duration (seconds): ")
            logger.info(f"Manual azimuth inputted for Duration: {duration}.")

            packet = np.stack((new_az, duration))
            az_comms.send(packet)
            logger.info(f"Manual azimuth input sent. Azimuth: {new_az} for Duration: {duration}.")

        # Receive propulsion input and send
        elif choice == "PROP":
            new_prop = input("New propulsion setting (m/s): ")
            logger.info(f"Manual propulsion inputted. Propulsion: {new_prop}.")
            duration = input("Duration (seconds): ")
            logger.info(f"Manual propulsion inputted for Duration: {duration}.")

            packet = np.stack((new_prop, duration))
            prop_comms.send(packet)
            logger.infoa(f"Manual propulsion input sent. Propulsion: {new_prop} for Duration {duration}.")

        # Receive new map file input and send
        elif choice == "MAP":
            new_map = input("File path to new currents map (.netcdf file): ")
            latlons, currents = read_netcdf(new_map)
            map_stack = np.stack((latlons, currents))
            logger.info("Current map updated.")
            map_comms.send(map_stack)
            logger.info("Updated current map sent")

        # Quit controls
        elif choice == "QUIT":
            quit = True

        else:
            print("Invalid Choice")

        print("\n")


def telem_list(ground_station, port_list):
    global temp, logger

    telem_listener = Comms(ground_station, port_list['telem'], listener=True)

    while telem_listener.conn is None:
        pass

    # Constantly grab temperatures and assign to global variable
    while True:
        temp = telem_listener.recv()
        logger.info(f"New telemetry received. Temperature: {temp:.4f}.")


def path_list(ground_station, port_list):
    global path, logger

    path_listener = Comms(ground_station, port_list['nav_path'], listener=True)

    while path_listener.conn is None:
        pass

    # Grab path and assign to a global variable
    while True:
        path = path_listener.recv()
        logger.info(f"New path received. Path has length {len(path)}.")


def gps_list(ground_station, port_list):
    global pos, logger

    gps_listener = Comms(ground_station, port_list['gps'], listener=True)
    while gps_listener.conn is None:
        pass

    # Grab GPS and assign to a global variable
    while True:
        pos = gps_listener.recv()
        logger.info(f"New GPS received. {pos[0]:.4f} N {pos[1]:.4f} E.")


def visualize():
    global pos, path, temp, latlons, currents

    idx = 0
    while True:
        if path is None or pos is None:
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

