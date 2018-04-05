# parser for ping measurements: creates corresp. yaml files
# tailored to fit fixed log structure!
import re
import yaml
import glob
import argparse
import networkx as nx


def parse_log(log_file, input_prefix=''):
    result = {'delays': []}

    with open(log_file, 'r') as f:
        log = f.readlines()
        log = [x.strip() for x in log]      # strip \n

        reading_vnf_delay = False
        reading_chain_delay = False
        delay = {}

        for i, line in enumerate(log):
            if line.startswith('Latency between VNFs'):
                reading_vnf_delay = True
                # extract from next line: src -> dest
                delay = {}
                delay['src'], delay['dest'] = log[i+1].split(' -> ')
            elif line.startswith('Latency of whole chain'):
                reading_vnf_delay = False
                reading_chain_delay = True
                delay = {}

            if reading_vnf_delay and line.startswith('round-trip'):
                # extract delay times
                delay_list = re.findall("\d+\.\d+", line)
                # convert to floats
                delay_list = [float(j) for j in delay_list]
                delay['min'], delay['delay'], delay['max'], delay['stddev'] = delay_list        # delay = avg
                result['delays'].append(delay)
                reading_vnf_delay = False

            if reading_chain_delay and line.startswith('round-trip'):
                delay_list = re.findall("\d+\.\d+", line)
                delay_list = [float(j) for j in delay_list]
                delay['min'], delay['delay'], delay['max'] = delay_list         # delay = avg
                result['chain_delay'] = delay
                reading_chain_delay = False

            if line.startswith('Info'):
                # get info from next 4 lines: timestamp, network, service, sources
                timestamp = log[i+1].replace('timestamp: ', '')
                network = log[i+2].replace('network: ', '')
                service = log[i+3].replace('service: ', '')
                sources = log[i+4].replace('sources: ', '')
                result['time'] = timestamp
                result['input'] = {'network': network, 'service': service, 'sources': sources}

                # extract and add input details: network size, etc.
                # read input files from specified path (+ prefix)
                network = nx.read_graphml(input_prefix + network)
                result["input"]["num_nodes"] = network.number_of_nodes()
                result["input"]["num_edges"] = network.number_of_edges()
                with open(input_prefix + service) as f:
                    service = yaml.load(f)
                    result["input"]["num_vnfs"] = len(service["vnfs"])
                with open(input_prefix + sources) as f:
                    sources = yaml.load(f)
                    result["input"]["num_sources"] = len(sources)

    return result


def write_yaml_log(log_file, delays):
    yaml_file = log_file[:-3] + 'yaml'
    with open(yaml_file, 'w') as f:
        print('Writing delays to {}'.format(yaml_file))
        yaml.dump(delays, f, default_flow_style=False)


def parse_args():
    parser = argparse.ArgumentParser(description="Parses a measurement log and creates a structured yaml file")
    parser.add_argument("-f", "--file", help="Log file", required=True, default=None, dest="file")
    return parser.parse_args()


if __name__ == '__main__':
    # log_files = glob.glob('../eval/emulation/*.log')
    # for log in log_files:
    #     delays = parse_log(log)
    #     write_yaml_log(log, delays)

    args = parse_args()
    result = parse_log(args.file)
    write_yaml_log(args.file, result)
