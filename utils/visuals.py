import matplotlib.pyplot as plt
import numpy as np
import datetime


def plot_navigation(position, destination, path, latlons, currents, temp, plot_idx, save_dir="./visuals/plots", skip_factor=10):
    # Determine the skip factor for plotting ( plotting all points will be a mess )
    skip = (slice(None, None, skip_factor), slice(None, None, skip_factor))

    # Separate latlons from grid (also UV
    lats, lons = latlons[::,::, 0], latlons[::, ::, 1]
    u, v = currents[::,::,0], currents[::,::,1]

    # Determine absolute speed
    speed = np.sqrt(u**2 + v**2)

    # Flip lats and lons for plotting
    path_plt = np.rot90(path[::skip_factor], 2)

    # FIg size
    plt.figure(figsize=(10, 8))

    # Plot current vectors
    plt.quiver(lons[skip], lats[skip], u[skip], v[skip], speed[skip], scale_units='inches', scale=20)

    # Plot navigation path
    plt.plot(path_plt[::, 0], path_plt[::, 1], color='black')

    # Plot position and destination
    plt.scatter(position[1], position[0], s=50, c='red',
                label=f"Position: {position[0]:.4f}°N  {position[1]:.4f}°E")
    plt.scatter(destination[1], destination[0], s=50, c='navy',
                label=f"Destination: {destination[0]:.4f}°N  {destination[1]:.4f}°E")

    # Labels
    time = datetime.datetime.now().replace(microsecond=0)
    plt.title(f"Navigation Path  - Time: {time}  - Temp: {temp:.2f}°F")
    plt.legend()
    plt.grid()

    plt.savefig(f"{save_dir}/plot_{plot_idx:03d}")
