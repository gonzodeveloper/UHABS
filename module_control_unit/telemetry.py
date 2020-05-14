import numpy as np
import pyproj

class ModuleTelemetry:

    @staticmethod
    def get_temp(mu=65, sigma=5):
        """
        Grabs telemetry for the controller to send to ground station.
        :return:
        """
        # Generate a random temperature
        temperature = np.random.normal(mu, sigma)

        return temperature

    @staticmethod
    def get_position(pos, latlons, currents, azimuth, propulsion, time_elaspsed):
        # Code here
        """
        Calculates position based off currents map, bearing, and propulsion of the module
        :param currents_map: u(y, x), v(y, x) 2Dd component arrays for current values; np.dstack
        :param position: (y, x) present position of module; tuple
        :param bearing: angle defined from East for module heading; float
        :return: (y, x) new position of module; tuple
        """
        # Grab module position in grid
        y, x = pos

        lat_start, lon_start = latlons[y, x]

        # Calculate velocity components of module
        boat_u = propulsion * np.cos(np.radians(azimuth))
        boat_v = propulsion * np.sin(np.radians(azimuth))

        # Corrected u-v components
        currents_u, currents_v = currents[y, x]
        u, v = (boat_u + currents_u), (boat_v + currents_v)

        # Corrected speed, azimuth
        corrected_speed = np.sqrt(u**2 + v**2)
        corrected_az = (np.arctan2(u,v) * 180/np.pi) % 360


        # Projected distance
        proj_dist = corrected_speed * time_elaspsed

        # Get a Geodesic object with the WGS84 CRS
        geod = pyproj.Geod(ellps='WGS84')

        # Use the geod to calculate final coordinates based on origin, fwd az and distance travelled
        lon_end, lat_end, _ = geod.fwd(lon_start, lat_start, az=corrected_az, dist=proj_dist)
        return lat_end, lon_end