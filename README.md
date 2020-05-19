# UHABS Navigation Module and Simulation

## Overview

This navigation sub-system was designed for autonomous guidence of the UHABS ocean recovery module. While we have not got to ocean testing, we have created a simulation for proof-of-concept. 

![sim animation](https://github.com/gonzodeveloper/UHABS/blob/master/visuals/animation.gif?raw=true)

In future iterations of this project, this code can be adapted for live use with the substitution of driver and telemetry code.

## Usage

While each of the modules can be used independently, we have included a full simulation through the **run_boat.py** and **run ground_station.py** scripts. These can be configured with the provided YAML template. 

## Techniques

The navigation path of the craft is determined by ocean current (or wind vector) maps and a classical shortest path algorithm, Dijstra's. 

The currents map is given by a 2-dimensional grid of u-v component vectors along with their corresponding latitude and longitude values. This is a common format that can be found in netCDF files produced by satelite measurements or model outputs. 

In order to run a shortest path algorithm on the currents map we have to transform it into a discrete network graph of nodes and verticies. This is accomplished by itterating through each grid cell, calculating its geodesic distance to its neighbors, and scaling those distances by the cell's u-v current vectors to define a directed edge weight. 

