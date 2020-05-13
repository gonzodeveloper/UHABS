import networkx as nx
import numpy as np
import pyproj
import struct


def transform_map(currents_map):
    """
    Transforms the u, v component current map into a directed graph
    :param currents_map: u(y, x), v(y, x) 2D component arrays for current values; np.dstack
    :return: directed graph representation of map; networkx.DiGraph
    """
    # Create empty directed graph
    currents_graph = nx.DiGraph()

    # Dimensions to iterate through
    y_dim = currents_map.shape[0]
    x_dim = currents_map.shape[1]

    # Iterate through positions in graph
    for y in range(y_dim):
        for x in range(x_dim):

            # Get current direction (y, x)
            vu = currents_map[y, x]

            # Get neighbors, with weights and azimuths, of (y, x)
            ns = _get_neighbors(y, x, vu, dims=(y_dim, x_dim))

            # Add to di-graph
            currents_graph.add_edges_from(ns)

    return currents_graph


def next_azimuth(currents_graph, boat_loc, dest_loc):
    """
    Use a dijkstras algorithm to find shortest path between the boats position and its destination.
    :param currents_graph: graph representation of 2D currents map; networkx.DiGraph
    :param boat_loc: y, x position of the boat; tuple
    :param dest_loc: y, x position of the destination; tuple
    :return: azimuth that should be taken; int
             the entire calculated path to the destination; list encoded node_ids
    """

    src_node = _encode_node_id(boat_loc)
    dest_node = _encode_node_id(dest_loc)

    shortest_path = nx.dijkstra_path(currents_graph, src_node, dest_node)

    next_node = shortest_path[1]

    next = currents_graph.edges[(src_node, next_node)]['azimuth']

    return next, shortest_path


def _get_neighbors(ys, xs, currents_map, latlons, dims):
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
    src = _encode_node_id((ys, xs))

    lat_src, lon_src = latlons[ys, xs]
    uv_src = currents_map[ys, xs]

    # Positions of potential neighbors
    neighbors = [(ys + 0, xs + 1), (ys + 1, xs + 1),
                 (ys + 1, xs + 0), (ys + 1, xs - 1),
                 (ys + 0, xs - 1), (ys - 1, xs - 1),
                 (ys - 1, xs + 0), (ys - 1, xs + 1)]

    # Get the lat-lon coords of the VALID adjacent positions
    valid_neighbors = [(yd, xd) for (yd, xd) in neighbors if (0 <= yd < y_dim) and (0 <= xd < x_dim)]
    coords_adj = [latlons[yd, xd] for (yd, xd) in valid_neighbors]
    lats_adj, lons_adj = coords_adj[::,0], coords_adj[::,1]

    # Get a Geod object with the WGS84 CRS
    geod = pyproj.Geod(ellps='WGS84')

    # Get the forward azimuths and distances to the adjacent coords (ignore back azimuths)
    azimuth, _, dist_adj = geod.inv(lon_src, lat_src, lons_adj, lats_adj)

    # Get 0 - 360 representation of azimuths
    theta_adj = azimuth % 360

    # Break azimuth and weights into component vectors
    u_adj = dist_adj * np.cos(np.radians(theta_adj))
    v_adj = dist_adj * np.sin(np.radians(theta_adj))

    uv_adj = np.dstack((u_adj, v_adj))

    # For each adjacent   w = (us - ud)^2 + (vs - vd)^2
    w_adj = np.sum((uv_adj - uv_src)**2)

    # Get list of esdination node_ids
    dest_ids = [_encode_node_id((yd, xd)) for yd, xd in valid_neighbors]

    edges = [(src, dest, {'weight': w, 'azimuth': theta}) for dest, w, theta in zip(dest_ids, w_adj, theta_adj)]
    return edges


def _encode_node_id(position):
    """
    Packs node position into byte string for id
    :param position: y, x position on current map; tuple
    :return: node id; byte array
    """
    y, x = position
    return struct.pack('II', y, x)


def _decode_node_id(raw):
    """
    Unpacks node id from byte string to position y, x
    :param raw: node id; byte array
    :return: y, x position on current map; tuple
    """
    return struct.unpack("II", raw)




