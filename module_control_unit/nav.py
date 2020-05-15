from threading import RLock
import networkx as nx
import numpy as np
import pyproj
import struct
import scipy

class ModuleNavigation:


    def __init__(self, nav_timestep, latlons, currents):


        self.latlons = latlons
        self.currents = currents
        self.timestep = nav_timestep
        self.nav_graph = self._transform_map()

        self.kdtree = self._build_tree()

        self.map_lock = RLock()

    def set_currents_map(self, latlons, currents):
        with self.map_lock:
            self.latlons = latlons
            self.currents = currents
            self.nav_graph = self._transform_map()

    def get_next_azimuth(self, geo_pos, geo_dest):
        """
        Use a dijkstras algorithm to find shortest path between the boats position and its destination.
        :param currents_graph: graph representation of 2D currents map; networkx.DiGraph
        :param boat_loc: y, x position of the boat; tuple
        :param dest_loc: y, x position of the destination; tuple
        :return: azimuth that should be taken; int
                 the entire calculated path to the destination; list encoded node_ids
        """

        idx_pos = self._geo_idx(geo_pos)
        idx_dest = self._geo_idx(geo_dest)

        src_node = ModuleNavigation._encode_node_id(idx_pos)
        dest_node = ModuleNavigation._encode_node_id(idx_dest)

        shortest_path = nx.dijkstra_path(self.nav_graph, src_node, dest_node)

        next_node = shortest_path[1]

        next_az = self.nav_graph.edges[(src_node, next_node)]['azimuth']

        path_ids = np.array([self._decode_node_id(ids) for ids in shortest_path])

        return next_az, path_ids
    def get_current(self, geo_pos):

        y, x = self._geo_idx(geo_pos)
        return self.currents[y, x]

    def _geo_idx(self, geo_pos):

        lat, lon = geo_pos
        result = self.kdtree.query((lat, lon))
        return np.unravel_index(result[1], (self.latlons.shape[0], self.latlons.shape[1]))

    def _build_tree(self):
        model_grid = list(zip(np.ravel(self.latlons[::, ::, 0]), np.ravel(self.latlons[::,::,1])))

        return scipy.spatial.KDTree(model_grid)

    def _transform_map(self):
        """
        Transforms the u, v component current map into a directed graph
        :param currents_map: u(y, x), v(y, x) 2D component arrays for current values; np.dstack
        :return: directed graph representation of map; networkx.DiGraph
        """
        # Create empty directed graph
        currents_graph = nx.DiGraph()

        # Dimensions to iterate through
        y_dim = self.currents.shape[0]
        x_dim = self.currents.shape[1]

        # Iterate through positions in graph
        for y in range(y_dim):
            for x in range(x_dim):


                # Get neighbors, with weights and azimuths, of (y, x)
                ns = self._get_neighbors(y, x, dims=(y_dim, x_dim))

                # Add to di-graph
                currents_graph.add_edges_from(ns)

        return currents_graph

    def _get_neighbors(self, ys, xs, dims):
        """
        Get all actual legal neighbors for position (ys, xs).
        Calculate cost of edge to these neighbors based on their azimuth, distance,
        and the vu-current at source (ys, xs)
        :param ys: y position of source node; int
        :param xs: x position of source node; int
        :param dims: max y-x bounds of the current-map; tuple
        :return: list directed edges with attributes to neghbors;
                 readable by networkx.add_edges_from [(src_id, dest_id, {'weight': w, 'azimuth': theta}, ...]
        """
        # Unpack dims
        y_dim, x_dim = dims

        # Get node_id for src
        src = ModuleNavigation._encode_node_id((ys, xs))

        # Geocoords for src
        lat_src, lon_src = self.latlons[ys, xs]

        # Positions of potential neighbors
        neighbors = [(ys + 0, xs + 1), (ys + 1, xs + 1),
                     (ys + 1, xs + 0), (ys + 1, xs - 1),
                     (ys + 0, xs - 1), (ys - 1, xs - 1),
                     (ys - 1, xs + 0), (ys - 1, xs + 1)]

        # Get the lat-lon coords of the VALID adjacent positions
        valid_neighbors = [(yd, xd) for (yd, xd) in neighbors if (0 <= yd < y_dim) and (0 <= xd < x_dim)]

        coords_adj = [self.latlons[yd, xd] for (yd, xd) in valid_neighbors]
        lats_adj, lons_adj = coords_adj[::,0], coords_adj[::,1]

        # Get a Geod object with the WGS84 CRS
        geod = pyproj.Geod(ellps='WGS84')

        # Get the forward azimuths and distances to the adjacent coords (ignore back azimuths)
        azimuth, _, dist_adj = geod.inv(lon_src, lat_src, lons_adj, lats_adj)

        # Get 0 - 360 representation of azimuths
        theta_adj = azimuth % 360

        # Get velocity
        velocity = dist_adj / self.timestep

        # Break azimuth and weights into component vectors
        u_adj = velocity * np.cos(np.radians(theta_adj))
        v_adj = velocity * np.sin(np.radians(theta_adj))

        # Current at source
        current_u, current_v = self.currents[ys, xs]

        # Find the most favorable edge by subtracting current from adjacent vectors
        u, v = (u_adj - current_u), (v_adj - current_v)

        # Weight scaling
        w_adj = np.sqrt(u**2 + v**2)

        # Get list of esdination node_ids
        dest_ids = [ModuleNavigation._encode_node_id((yd, xd)) for yd, xd in valid_neighbors]

        edges = [(src, dest, {'weight': w, 'azimuth': theta}) for dest, w, theta in zip(dest_ids, w_adj, theta_adj)]
        return edges

    @staticmethod
    def _encode_node_id(idx_pos):
        """
        Packs node position into byte string for id
        :param position: y, x position on current map; tuple
        :return: node id; byte array
        """
        y, x = idx_pos
        return struct.pack('II', y, x)

    @staticmethod
    def _decode_node_id(raw):
        """
        Unpacks node id from byte string to position y, x
        :param raw: node id; byte array
        :return: y, x position on current map; tuple
        """
        return struct.unpack("II", raw)




