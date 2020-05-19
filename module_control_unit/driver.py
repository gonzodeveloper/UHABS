from threading import RLock
import time


class ModuleDrivers:
    def __init__(self):

        # Initialize az and prop
        self.azimuth = 0
        self.propulsion = 0

        # Set up locks on az and prop to prevent changing boat vector before previous instructions have been completed
        self.az_lock = RLock()
        self.prop_lock = RLock()


    def set_azimuth(self, theta, force_duration=0):
        # Sleeps the module instructions for a period of time for the lock
        with self.az_lock:
            self.azimuth = theta
            time.sleep(force_duration)


    def set_propulsion(self, speed, force_duration=0):
        # Sleeps the module instructions for a period of time for the lock
        with self.prop_lock:
            self.propulsion = speed
            time.sleep(force_duration)

    # Grab propulsion
    def get_propulsion(self):
        return self.propulsion

    # Grab azimuth
    def get_azimuth(self):
        return self.azimuth