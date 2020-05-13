from threading import Thread, RLock
from .common_utils.file_io import read_netcdf
from .module_control_unit import telemetry, nav, driver
import yaml
import sys

# GLOBALS
currents_map = None
nav_graph = None
map_lock = RLock()
graph_lock = RLock()


# STATIC VALUES
PROPULSION = 10
TIMESTEP = 10
GRID_WIDTH = 100

def main(config):
    global nav_graph, currents_map

    currents_map = read_netcdf(config['init_map'])
    nav_graph = nav.transform_map(currents_map)



if __name__ == '__main__':

    # Load configuration YAML
    with open(sys.argv[1]) as f:
        config = yaml.load(f)

    main(config)

