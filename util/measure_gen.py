# script for creating suitable measurement shell-scripts
import yaml
import json
import argparse


# read interface IPs from string and return as dict
def get_interfaces(if_string):
    interfaces = {}
    # remove brackets and split at commas
    if_string = if_string.replace('(','').replace(')','')
    split_strings = if_string.split(',')
    # add to dictionary
    for i, split_string in enumerate(split_strings):
        if split_string.startswith('id='):
            interfaces[split_string[3:]] = split_strings[i+1][3:-3]         # remove 'ip=' and '/24'

    return interfaces


# generate script according to specified service (in yaml format)
def generate_measure_script(service_file, num_pings=10):
    echo_vnf = 'echo "Latency between VNFs (ping)"'
    echo_chain = 'echo "Latency of whole chain (httping)"'
    first_fwd = None        # first forwarder in chain
    lines = ['#!/bin/sh', '']

    # read service yaml file
    with open(service_file, 'r') as f_service:
        service = yaml.load(f_service)

        # set input and output IPs
        ips = {}
        for vnf in service['vnfs']:
            image = json.loads(vnf['image'])
            interfaces = get_interfaces(image['network'])
            ips[vnf['name']] = {}
            for port, ip in interfaces.items():
                ips[vnf['name']][port] = ip

        # write measurements between VNFs (assuming they all have IPs, not layer 2)
        for vl in service['vlinks']:
            lines.append(echo_vnf)
            lines.append('echo "{} -> {}"'.format(vl['src'], vl['dest']))
            dest_ip = ips[vl['dest']]['input']
            lines.append('sudo docker exec -it mn.{} ping -c{} -q {}'.format(vl['src'], num_pings, dest_ip))

            # save 1st forwarder in chain for later
            if vl['src'] == 'vnf_user':
                first_fwd = vl['dest']
        lines.append('')

        # write measurements of whole chain (assuming it starts with vnf_user)
        lines.append(echo_chain)
        dest_ip = ips[first_fwd]['input']
        lines.append('sudo docker exec -it mn.vnf_user httping --url {} -c {}'.format(dest_ip, num_pings))

        # print
        for l in lines:
            print(l)


def parse_args():
    parser = argparse.ArgumentParser(description="Generates a custom measurement script")
    parser.add_argument("-t", "--template", help="Template/service input file (.yaml)", required=True, default=None, dest="template")
    parser.add_argument("-c", help="Number of ping measurements (-c arg)", required=False, default=10, dest="num_pings")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    generate_measure_script(args.template, args.num_pings)

