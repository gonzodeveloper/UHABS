from common_utils.file_io import read_netcdf
from module_control_unit.nav import ModuleNavigation
from ground_station.visuals import plot_navigation

latlons, currents = read_netcdf("data/S1A_ESA_159.56W_20.87N_VV_C5_GFS05CDF_wind_level2.nc")

nav = ModuleNavigation(100, latlons, currents)

src = (20, -158)
dest = (21, -160)
az, path = nav.get_next_azimuth(src, dest)

plot_navigation(src, dest, path, latlons, currents, 35)
