# simple helper script printing the network size = #nodes + #edges
# used for estimating emulation setup time

import networkx as nx
import glob
import os
import argparse


def network_size(network_file):
    network = nx.read_graphml(network_file)
    print(network.number_of_nodes() + network.number_of_edges())
    return network.number_of_nodes(), network.number_of_edges()


# get size of all networks, return dict
def all_sizes():
    sizes = {}
    net_files = glob.glob('../inputs/networks/*.graphml')
    for net in net_files:
        net_name = os.path.basename(net).replace('.graphml', '')
        sizes[net_name] = network_size(net)
    return sizes


def parse_args():
    parser = argparse.ArgumentParser(description='Prints the size of a network (#nodes + #edges)')
    parser.add_argument('-n', '--network', help='Graphml network', required=True, default=None, dest='network')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    network_size(args.network)
