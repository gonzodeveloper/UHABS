import numpy as np
import pyproj


class ModuleTelemetry:

    @staticmethod
    def get_temp(mu=65, sigma=5):
        # Generate a random temperature
        temperature = np.random.normal(mu, sigma)

        return temperature

    @staticmethod
    def get_position(geo_pos, current, azimuth, propulsion, time_elaspsed):
        """

        :param geo_pos: lat, long position of boat, tuple
        :param current: two 2-D numpy arrays of u, v values;
        :param azimuth: boat direction; float
        :param propulsion: boat speed; float
        :param time_elaspsed: duration over which boat travels; int
        :return: ending lat, long values of boat; tuple
        """
        # Set starting lat, long
        lat_start, lon_start = geo_pos

        # Find boat velocity vector
        boat_u = propulsion * np.sin(np.radians(azimuth))
        boat_v = propulsion * np.cos(np.radians(azimuth))

        # Find total boat velocity vector, including current vector
        current_u, current_v = current
        u, v = (boat_u + current_u), (boat_v + current_v)

        # Find total boat speed and azimuth
        corrected_speed = np.sqrt(u**2 + v**2)
        corrected_az = (np.arctan2(u,v) * 180/np.pi) % 360

        # Calculated projected distance based on total boath speed
        proj_dist = corrected_speed * time_elaspsed

        # Create geodesics
        geod = pyproj.Geod(ellps='WGS84')

        # Calculate ending lat, long based on geodesic, projected distance, azimuth, and initial lat, long
        lon_end, lat_end, _ = geod.fwd(lon_start, lat_start, az=corrected_az, dist=proj_dist)
        return lat_end, lon_end
