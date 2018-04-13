# script with function to prepare and support evaluation
import glob
import yaml
import pandas as pd
import os


# load simulation results and calculate RTT
# network and algorithm name are used to filter the results
def sim_delays(network, algorithm):
    sim_results = glob.glob('../eval/{}/{}/{}*.yaml'.format(network, algorithm, network))
    sim_delays = []
    for result_file in sim_results:
        with open(result_file, 'r') as f:
            result = yaml.load(f)

            # one-way = RTT/2
            result['chain_rtt'] = result['metrics']['total_delay'] * 2
            for delay in result['metrics']['delays']:
                delay['rtt'] = delay['delay'] * 2

            sim_delays.append(result)

    return sim_delays


# load corresponding emulation results and calculate RTT
def emu_delays(network, algorithm):
    emu_results = glob.glob('../eval/{}/{}/emulation/{}*.yaml'.format(network, algorithm, network))
    emu_delays = []
    for result_file in emu_results:
        with open(result_file, 'r') as f:
            result = yaml.load(f)

            # chain delays = httping = TCP handshake = 2x RTT
            result['chain_rtt'] = result['chain_delay']['delay'] / 2

            # vnf delays = ping = RTT
            for delay in result['delays']:
                delay['rtt'] = delay['delay']

            emu_delays.append(result)
            # TODO: also store std (how is std affected, when mean/2?)

    return emu_delays


# sort and match simulation and emulation delays; calc difference and ratio; return structured pandas dataframes
def match_sim_emu(sim_delays, emu_delays):
    input_cols = ['network', 'num_nodes', 'num_edges', 'service', 'num_vnfs', 'sources', 'num_sources', 'algorithm']
    chain_df = pd.DataFrame(columns=input_cols + ['sim_rtt', 'emu_rtt'])
    vnf_df = pd.DataFrame(columns=input_cols + ['src', 'dest', 'sim_rtt', 'emu_rtt'])
    chain_index = 0
    vnf_index = 0

    # match and sort chain and inter-VNF RTTs and insert into data frames
    for emu in emu_delays:
        # only use name of network, service, and source files (instead of full path)
        emu_network_name = os.path.basename(emu['input']['network']).replace('.graphml', '')
        emu_service_name = os.path.basename(emu['input']['service']).replace('.yaml', '')
        emu_sources_name = os.path.basename(emu['input']['sources']).replace('.yaml', '')

        for sim in sim_delays:
            # only use name of network, service, and source files (instead of full path)
            sim_network_name = os.path.basename(sim['input']['network']).replace('.graphml', '')
            sim_service_name = os.path.basename(sim['input']['service']).replace('.yaml', '')
            sim_sources_name = os.path.basename(sim['input']['sources']).replace('.yaml', '')

            # match chain delays (same input: network, service, sources)
            if emu_network_name == sim_network_name and emu_service_name == sim_service_name and emu_sources_name == sim_sources_name:
                # insert into data frame
                inputs = [emu_network_name, sim['input']['num_nodes'], sim['input']['num_edges'],
                          emu_service_name, sim['input']['num_vnfs'],
                          emu_sources_name, sim['input']['num_sources'], sim['input']['algorithm']]
                # somehow the simulation RTT needs to be cast to float explicitly
                chain_df.loc[chain_index] = inputs + [float(sim['chain_rtt']), emu['chain_rtt']]
                chain_index += 1

                # match inter-VNF RTTs (same input + src, dest)
                for emu_vnf in emu['delays']:
                    for sim_vnf in sim['metrics']['delays']:
                        if emu_vnf['src'] == sim_vnf['src'] and emu_vnf['dest'] == sim_vnf['dest']:
                            vnf_df.loc[vnf_index] = inputs + [sim_vnf['src'], sim_vnf['dest'], float(sim_vnf['rtt']), emu_vnf['rtt']]
                            vnf_index += 1

    # calc RTT difference (emu_rtt - sim_rtt) and ratio (emu_rtt / sim_rtt)
    chain_df['rtt_diff'] = chain_df['emu_rtt'] - chain_df['sim_rtt']
    chain_df['rtt_ratio'] = chain_df['emu_rtt'] / chain_df['sim_rtt']
    vnf_df['rtt_diff'] = vnf_df['emu_rtt'] - vnf_df['sim_rtt']
    vnf_df['rtt_ratio'] = vnf_df['emu_rtt'] / vnf_df['sim_rtt']
    # if sim_rtt = 0, rtt_ratio = inf!

    return chain_df, vnf_df


# calc and save RTT difference and ratio; also return additional auxiliary dataframes
# df contains sim_rtt and emu_rtt; input_cols are the names of the input columns (eg, 'network')
def calc_stats(df, input_cols):
    # calc RTT difference (emu_rtt - sim_rtt) and ratio (emu_rtt / sim_rtt); if sim_rtt = 0, rtt_ratio = inf
    df['rtt_diff'] = df['emu_rtt'] - df['sim_rtt']
    df['rtt_ratio'] = df['emu_rtt'] / df['sim_rtt']

    # create auxiliary df with separate rows for each RTT and a type (sim or emu); for easier plotting later
    # temporary df with simulation RTTs
    sim_df = df[input_cols].copy()
    sim_df['rtt'] = df['sim_rtt']
    sim_df['type'] = 'sim'
    # temporary df with emulation RTTs
    emu_df = df[input_cols].copy()
    emu_df['rtt'] = df['emu_rtt']
    emu_df['type'] = 'emu'
    aux_df = pd.concat([sim_df, emu_df])

    return df, aux_df


# call other functions to prepare evaluation; returns pandas dataframes
def prepare_eval(network, algorithm):
    sim = sim_delays(network, algorithm)
    emu = emu_delays(network, algorithm)
    chain_df, vnf_df = match_sim_emu(sim, emu)

    input_cols = ['algorithm', 'network', 'num_nodes', 'num_edges', 'service', 'num_vnfs', 'sources', 'num_sources']
    chain_df, aux_chain_df = calc_stats(chain_df, input_cols)
    vnf_df, aux_vnf_df = calc_stats(vnf_df, input_cols + ['src', 'dest'])

    return chain_df, aux_chain_df, vnf_df, aux_vnf_df
