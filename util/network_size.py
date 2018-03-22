# simple helper script printing the network size = #nodes + #edges
# used for estimating emulation setup time

import networkx as nx
import argparse


def network_size(network_file):
    network = nx.read_graphml(network_file)
    print(network.number_of_nodes() + network.number_of_edges())


def parse_args():
    parser = argparse.ArgumentParser(description='Prints the size of a network (#nodes + #edges)')
    parser.add_argument('-n', '--network', help='Graphml network', required=True, default=None, dest='network')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    network_size(args.network)
