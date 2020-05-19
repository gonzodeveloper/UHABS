from netCDF4 import Dataset
import numpy as np


def read_netcdf(filename):
    with Dataset(filename) as nc:
        lats = nc.variables['latitude'][:]
        lons = nc.variables['longitude'][:]

        sar_wind = nc.variables['sar_wind'][:]
        input_dir = nc.variables['input_dir'][:]

        u = sar_wind * np.cos(input_dir)
        v = sar_wind * np.sin(input_dir)

        return np.dstack((lats, lons)), np.dstack((u, v))

