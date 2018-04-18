# simple greedy placement
from util import reader, writer
import yaml
import networkx as nx
from datetime import datetime
import argparse


# get closest node regarding delay with available resources + the length of the corresponding shortest path
def get_closest_node(network, src_node):
    # only nodes with remaining resources (here, cpu)
    available_nodes = [v for v, cpu in nx.get_node_attributes(network, 'cpu').items() if cpu > 0]

    # choose closest node from available nodes
    lengths = nx.shortest_path_length(network, src_node, weight='delay')
    lengths = {v: length for (v, length) in lengths.items() if v in available_nodes}
    closest = min(lengths, key=lengths.get)

    # also return shortest path to the closest node
    path = nx.shortest_path(network, src_node, closest, weight='delay')

    print('Closest available node from {}: {} (shortest path length: {})'.format(src_node, closest, lengths[closest]))
    return closest, path, lengths[closest]


# place VNFs at closest node (max 1 per node) and connect with shortest paths
def place(network_file, service_file, sources_file):
    # read input
    # set cpu=1 as node resource and assume each vnf needs 1 cpu => max 1 vnf per node
    # for better comparison with other placement algorithms
    network = reader.read_network(network_file, node_attr={'cpu': 1})
    with open(service_file) as f:
        service = yaml.load(f)
    with open(sources_file) as f:
        sources = yaml.load(f)

    # prepare placement output
    placement = {'time': datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                 'input': {'algorithm': 'greedy',
                           'network': network_file,
                           'service': service_file,
                           'sources': sources_file,
                           'num_nodes': network.number_of_nodes(),
                           'num_edges': network.number_of_edges(),
                           'num_vnfs': len(service['vnfs']),
                           'num_sources': len(sources)},
                 'placement': {'vnfs': [], 'vlinks': []},
                 'metrics': {'delays': [], 'total_delay': 0}}

    # placement
    for src in sources:
        # place the first VNF at the source
        # find matching VNF in the service (there should be exactly one)
        matched_vnf = [vnf for vnf in service['vnfs'] if vnf['name'] == src['vnf']][0]
        src_vnf = {'name': src['vnf'], 'node': src['node'], 'image': matched_vnf['image']}
        placement['placement']['vnfs'].append(src_vnf)
        print('Placed {} at {}'.format(src_vnf['name'], src_vnf['node']))
        # decrease node resource (cpu)
        network.node[src_vnf['node']]['cpu'] -= 1

        # follow vLinks in service to reach following VNFs and place them greedily as close as possible (delay)
        end_of_chain = False
        while not end_of_chain:
            matched_vlink = [vl for vl in service['vlinks'] if vl['src'] == src_vnf['name']]
            if matched_vlink:
                # follow only first matching vlink and place the dest-vnf
                # assume a linear chain, ie, only one matching vlink
                matched_vlink = matched_vlink[0]
                matched_vnf = [vnf for vnf in service['vnfs'] if vnf['name'] == matched_vlink['dest']][0]

                # get closest node with remaining resources
                closest_node, path, path_length = get_closest_node(network, src_vnf['node'])

                dest_vnf = {'name': matched_vnf['name'], 'node': closest_node, 'image': matched_vnf['image']}
                placement['placement']['vnfs'].append(dest_vnf)
                print('Placed {} at {}'.format(dest_vnf['name'], dest_vnf['node']))
                network.node[dest_vnf['node']]['cpu'] -= 1

                # add connecting vLink
                vlink = {'src_vnf': src_vnf['name'], 'src_node': src_vnf['node'],
                         'dest_vnf': dest_vnf['name'], 'dest_node': dest_vnf['node'], 'path': path}
                placement['placement']['vlinks'].append(vlink)

                # set vLink delay along shortest path
                delay = {'src': src_vnf['name'], 'src_node': src_vnf['node'],
                         'dest': dest_vnf['name'], 'dest_node': dest_vnf['node'], 'delay': path_length}
                placement['metrics']['delays'].append(delay)
                placement['metrics']['total_delay'] += path_length

                # update src_vnf for next iteration
                src_vnf = dest_vnf
            else:
                end_of_chain = True

    # write placement to file
    result = writer.write_placement(network_file, service_file, sources_file, placement, 'greedy')

    return result


def parse_args():
    parser = argparse.ArgumentParser(description="Simple random placement")
    parser.add_argument("--network", help="Network input file (.graphml)", required=True, default=None, dest="network")
    parser.add_argument("--service", help="Template input file (.yaml)", required=True, default=None, dest="service")
    parser.add_argument("--sources", help="Sources input file (.yaml)", required=True, default=None, dest="sources")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    placement = place(args.network, args.service, args.sources)
