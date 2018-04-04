# read and visualize result files
import glob
import yaml
import matplotlib.pyplot as plt


def process_emu_results(prefix=''):
    emu_results = glob.glob('../eval/emulation/{}*.yaml'.format(prefix))
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
    return emu_delays


def process_sim_results(prefix=''):
    sim_results = glob.glob('../eval/bjointsp/{}*.yaml'.format(prefix))
    sim_delays = []
    for result_file in sim_results:
        with open(result_file, 'r') as f:
            result = yaml.load(f)

            # TODO: extract chain length, num flows...? or better write to file
            # chain_length = int(result['input']['service'][2]) + 2        # +2 for user and web

            # one-way = RTT/2
            result['chain_rtt'] = result['metrics']['total_delay'] * 2
            for delay in result['metrics']['delays']:
                delay['rtt'] = delay['delay'] * 2

            sim_delays.append(result)
    return sim_delays


def plot(emu_delays, sim_delays):
    # TODO: very hacky and inefficient. what's a more elegant way?
    # match and sort chain and inter-VNF RTTs
    emu_chain_rtt, sim_chain_rtt = [], []
    emu_vnf_rtt, sim_vnf_rtt = [], []
    for emu in emu_delays:
        for sim in sim_delays:
            # match chain delays (same input: network, service, sources)
            if emu['input']['network'].endswith(sim['input']['network']) \
                    and emu['input']['service'].endswith(sim['input']['service']) \
                    and emu['input']['sources'].endswith(sim['input']['sources']):
                emu_chain_rtt.append(emu['chain_rtt'])
                sim_chain_rtt.append(sim['chain_rtt'])

                # match inter-VNF RTTs (same input + src, dest)
                for emu_vnf in emu['delays']:
                    for sim_vnf in sim['metrics']['delays']:
                        if emu_vnf['src'] == sim_vnf['src'] and emu_vnf['dest'] == sim_vnf['dest']:
                            emu_vnf_rtt.append(emu_vnf['rtt'])
                            sim_vnf_rtt.append(sim_vnf['rtt'])


    # 1.1 chain delays
    x_chain = range(len(emu_delays))
    plt.figure(1)
    plt.subplot(2, 1, 1)
    plt.plot(x_chain, emu_chain_rtt, 'g^', x_chain, sim_chain_rtt, 'bs')
    # plt.xticks(x_chain, sim_chain_length)
    plt.legend(['Emulation', 'Placement (simulation)'])
    plt.ylabel('Absolute')
    plt.title('Chain RTT (in ms)')

    # 1.2 chain delay difference emu - sim
    chain_diffs = [emu_chain_rtt[i]-sim_chain_rtt[i] for i in range(len(emu_chain_rtt))]
    plt.subplot(2, 1, 2)
    plt.plot(x_chain, chain_diffs)
    # plt.xticks(x_chain, sim_chain_length)
    plt.xlabel('Different service/source combinations')
    plt.ylabel('RTT difference')

    plt.savefig('../eval/plots/chainRtt.pdf', bbox_inches='tight')


    # 2.1 inter-VNF delays
    x_vnfs = range(len(emu_vnf_rtt))
    plt.figure(2)
    plt.subplot(2, 1, 1)
    plt.plot(x_vnfs, emu_vnf_rtt, 'g^', x_vnfs, sim_vnf_rtt, 'bs')
    # plt.errorbar(x_vnfs, emu_vnf_rtt, yerr=emu_vnf_std, fmt='none', ecolor='black', capsize=2)
    # plt.xticks(x_vnfs, sim_vnf_length)
    plt.legend(['Emulation', 'Placement (simulation)'])
    plt.ylabel('Absolute')
    plt.title('Inter-VNF RTT (in ms)')

    # 2.2 inter-VNF delay difference: emu - sim
    vnf_diffs = [emu_vnf_rtt[i]-sim_vnf_rtt[i] for i in range(len(emu_vnf_rtt))]
    plt.subplot(2, 1, 2)
    plt.plot(x_vnfs, vnf_diffs)
    # plt.xticks(x_vnfs, sim_vnf_length)
    plt.xlabel('Different service/source combinations')
    plt.ylabel('RTT difference')

    plt.savefig('../eval/plots/vnfRtt.pdf', bbox_inches='tight')


    # # 3. plot chain delay ratio: emu_delay/sim_delay (not for inter-VNF delays as they are often 0)
    # plt.figure(3)
    # chain_ratio = [emu_chain_rtt[i]/sim_chain_rtt[i] for i in range(len(emu_chain_rtt))]
    # plt.plot(x_chain, chain_ratio)
    # # plt.xticks(x_chain, sim_chain_length)
    # plt.xlabel('Different service/source combinations')
    # plt.ylabel('Chain RTT ratio')
    # plt.title('Emulation delay / simulation delay')


    # plt.show()


if __name__ == '__main__':
    network_prefix = 'Abilene'
    emu_delays = process_emu_results(network_prefix)
    sim_delays = process_sim_results(network_prefix)
    plot(emu_delays, sim_delays)
