from netCDF4 import Dataset
import numpy as np


def read_netcdf(filename):
    """

    :param filename: grabs filename to read; string
    :return: two 2-D numpy arrays containing u and v vector component information for current maps; 2-D numpy array
    """
    with Dataset(filename) as nc:

        # Grab lat, long
        lats = nc.variables['latitude'][:]
        lons = nc.variables['longitude'][:]

        # Grab speed + direction
        sar_wind = nc.variables['sar_wind'][:]
        input_dir = nc.variables['input_dir'][:]

        # Convert speed + direction to u and v component for wind vectors
        u = sar_wind * np.sin(input_dir)
        v = sar_wind * np.cos(input_dir)

        return np.dstack((lats, lons)), np.dstack((u, v))

