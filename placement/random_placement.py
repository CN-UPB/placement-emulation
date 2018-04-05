# simple random placement
from util import read_network
import yaml
from datetime import datetime
from random import choice


# TODO: only choose from nodes with remaining resources
def place(network_file, service_file, sources_file):
    # read input
    network = read_network.read_network(network_file)
    with open(service_file) as f:
        service = yaml.load(f)
    with open(sources_file) as f:
        sources = yaml.load(f)

    # prepare placement output
    placement = {'time': datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                 'input': {'network': network_file,
                           'service': service_file,
                           'sources': sources_file,
                           'num_nodes': network.number_of_nodes(),
                           'num_edges': network.number_of_edges(),
                           'num_vnfs': len(service['vnfs']),
                           'num_sources': len(sources)},
                 'placement': {'vnfs': [], 'vlinks': []}}

    # placement
    for src in sources:
        # place the first VNF at the source
        # find matching VNF in the service (there should be exactly one)
        matched_vnf = [vnf for vnf in service['vnfs'] if vnf['name'] == src['vnf']][0]
        src_vnf = {'name': src['vnf'], 'node': src['node'], 'image': matched_vnf['image']}
        placement['placement']['vnfs'].append(src_vnf)

        # follow vLinks in service to reache following VNFs and place randomly
        end_of_chain = False
        while not end_of_chain:
            matched_vlink = [vl for vl in service['vlinks'] if vl['src'] == src_vnf['name']]
            if matched_vlink:
                # follow only first matching vlink and place the dest-vnf
                # assume a linear chain, ie, only one matching vlink
                matched_vlink = matched_vlink[0]
                matched_vnf = [vnf for vnf in service['vnfs'] if vnf['name'] == matched_vlink['dest']][0]
                rand_node = choice(list(network.nodes()))
                dest_vnf = {'name': matched_vnf['name'], 'node': rand_node, 'image': matched_vnf['image']}
                placement['placement']['vnfs'].append(dest_vnf)

                # add connecting vLink
                vlink = {'src_vnf': src_vnf['name'], 'src_node': src_vnf['node'],
                         'dest_vnf': dest_vnf['name'], 'dest_node': dest_vnf['node']}
                placement['placement']['vlinks'].append(vlink)

                # update src_vnf for next iteration
                src_vnf = dest_vnf
            else:
                end_of_chain = True

    return placement


network = '../inputs/networks/Abilene.graphml'
service = '../inputs/services/fw1chain.yaml'
sources = '../inputs/sources/source0.yaml'
placement = place(network, service, sources)
print(placement)
