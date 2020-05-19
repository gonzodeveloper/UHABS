from threading import RLock
import time


class ModuleDrivers:
    def __init__(self):
        self.azimuth = 0
        self.propulsion = 0

        self.az_lock = RLock()
        self.prop_lock = RLock()


    def set_azimuth(self, theta, force_duration=0):
        with self.az_lock:
            self.azimuth = theta
            time.sleep(force_duration)


    def set_propulsion(self, speed, force_duration=0):
        with self.prop_lock:
            self.propulsion = speed
            time.sleep(force_duration)


    def get_propulsion(self):
        return self.propulsion


    def get_azimuth(self):
        return self.azimuth
