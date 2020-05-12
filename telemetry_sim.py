import numpy as np

def telem_sim:
    """
    Grabs telemetry for the controller to send to ground station.
    :return:
    """
    # Generate a random temperature
    temperature = np.random.normal(65, 5)

    return temperature