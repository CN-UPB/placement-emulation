# read graphml, calculate delays, return NetworkX graph
# for consistent calculation and rounding of delays across placement algorithms and with emulation!
import networkx as nx
from geopy.distance import vincenty


# TODO: also use for bjointsp? just have to add cpu, mem, dr and retrieve bidirectional edges
# read graphml, calculate delays, return undirected(!) NetworkX graph
# if specified (as dict), set additional node and/or edge attributes (e.g., resources)
def read_network(file, node_attr=None, edge_attr=None):
    SPEED_OF_LIGHT = 299792458  # meter per second
    PROPAGATION_FACTOR = 0.77  	# https://en.wikipedia.org/wiki/Propagation_delay

    network = nx.read_graphml(file, node_type=int)

    # add 'pop' to node index (eg, 1 --> pop1)
    node_mapping = {n: 'pop{}'.format(n) for n in network.nodes}
    network = nx.relabel_nodes(network, node_mapping)

    # calculate link delay based on geo positions of nodes
    for e in network.edges(data=True):
        n1 = network.nodes(data=True)[e[0]]
        n2 = network.nodes(data=True)[e[1]]
        n1_lat, n1_long = n1.get('Latitude'), n1.get('Longitude')
        n2_lat, n2_long = n2.get('Latitude'), n2.get('Longitude')
        distance = vincenty((n1_lat, n1_long), (n2_lat, n2_long)).meters	    # in meters
        delay = (distance / SPEED_OF_LIGHT * 1000) * PROPAGATION_FACTOR  	    # in milliseconds
        # round to integer delays!
        network[e[0]][e[1]]['delay'] = round(delay)

    # set node and edge attributes if specified
    # all attributes are set equally for all nodes/edges
    if node_attr:
        for key, value in node_attr.items():
            nx.set_node_attributes(network, key, value)
    if edge_attr:
        for key, value in edge_attr.items():
            nx.set_edge_attributes(network, key, value)

    return network
