import networkx as nx
import numpy as np
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

            # Get neighbors, with weights and bearings, of (y, x)
            ns = _get_neighbors(y, x, vu, dims=(y_dim, x_dim))

            # Add to di-graph
            currents_graph.add_edges_from(ns)

    return currents_graph


def next_bearing(currents_graph, boat_loc, dest_loc):
    """
    Use a dijkstras algorithm to find shortest path between the boats position and its destination.
    :param currents_graph: graph representation of 2D currents map; networkx.DiGraph
    :param boat_loc: y, x position of the boat; tuple
    :param dest_loc: y, x position of the destination; tuple
    :return: bearing that should be taken; int
             the entire calculated path to the destination; list encoded node_ids
    """

    src_node = _encode_node_id(boat_loc)
    dest_node = _encode_node_id(dest_loc)

    shortest_path = nx.dijkstra_path(currents_graph, src_node, dest_node)

    next_node = shortest_path[1]

    next_bearing = currents_graph.edges[(src_node, next_node)]['bearing']

    return next_bearing, shortest_path


def _get_neighbors(ys, xs, vu_src, dims):
    """
    Get all actual legal neighbors for position (ys, xs).
    Calculate cost of edge to these neighbors based on their bearing, distance,
    and the vu-current at source (ys, xs)
    :param ys: y position of source node; int
    :param xs: x position of source node; int
    :param vu_src: vu-current at source position; ndarray[v, u]
    :param dims: max y-x bounds of the current-map; tuple
    :return: list directed edges with attributes to neghbors;
             readable by networkx.add_edges_from [(src_id, dest_id, {'weight': w, 'bearing': theta}, ...]
    """
    # Get node_id for src
    src = _encode_node_id((ys, xs))

    # Positions of potential neighbors
    coords_adj = [(ys + 0, xs + 1), (ys + 1, xs + 1),
                  (ys + 1, xs + 0), (ys + 1, xs - 1),
                  (ys + 0, xs - 1), (ys - 1, xs - 1),
                  (ys - 1, xs + 0), (ys - 1, xs + 1)]

    # Bearings and initial weights of potential neighbors
    theta_adj = np.array([0, 45, 90, 135, 180, 225, 270, 315])
    w_adj = np.array([1, 1.4, 1, 1.4, 1, 1.4, 1, 1.4])

    # Break bearing and weights into component vectors
    v_adj = w_adj * np.sin(np.radians(theta_adj))
    u_adj = w_adj * np.cos(np.radians(theta_adj))

    vu_adj = np.dstack((v_adj, u_adj))

    # Unpack dims
    y_dim, x_dim = dims

    # Create new list
    neighbors = list()

    # Iterate over each potential neighbor
    for (yd, xd), vu, theta in zip(coords_adj, vu_adj, theta_adj):

        # Check if this neighbor is within bounds
        if (0 <= yd < y_dim) and (0 <= xd < x_dim):

            # If so, get nod_id as dest
            dest = _encode_node_id((yd, xd))
            # Get new weight for this edge by subtracting uv-current weight from source
            w = np.sum(vu - vu_src)**2

            # Add to list
            neighbors.append((src, dest, {'weight': w, 'bearing': theta}))

    return neighbors


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




