# read and visualize result files
import glob
import yaml
import matplotlib.pyplot as plt


# TODO: store and process delays in an ordered fashion! (see fixme below)

def process_emu_results():
    emu_results = glob.glob('../eval/emulation/*.yaml')
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


def process_sim_results():
    sim_results = glob.glob('../eval/bjointsp/*.yaml')
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
            if emu['input']['network'].endswith(sim['input']['network']) \
                    and emu['input']['service'].endswith(sim['input']['service']) \
                    and emu['input']['sources'].endswith(sim['input']['sources']):
                emu_chain_rtt.append(emu['chain_rtt'])
                sim_chain_rtt.append(sim['chain_rtt'])

                # match inter-VNF RTTs
                for emu_vnf in emu['delays']:
                    for sim_vnf in sim['metrics']['delays']:
                        if emu_vnf['src'] == sim_vnf['src'] and emu_vnf['dest'] == sim_vnf['dest']:
                            emu_vnf_rtt.append(emu_vnf['rtt'])
                            sim_vnf_rtt.append(sim_vnf['rtt'])


    # absolute chain delays
    plt.figure(1)
    x_chain = range(len(emu_delays))
    plt.subplot(2, 1, 1)
    plt.plot(x_chain, emu_chain_rtt, 'g^', x_chain, sim_chain_rtt, 'bs')
    # plt.xticks(x_chain, sim_chain_length)
    plt.legend(['Emulation', 'Placement (simulation)'])
    plt.ylabel('Chain RTT (in ms)')
    plt.title('Delay comparison between emulation and simulation')

    # plot inter-VNF delays
    x_vnfs = range(len(emu_vnf_rtt))
    plt.subplot(2, 1, 2)
    plt.plot(x_vnfs, emu_vnf_rtt, 'g^', x_vnfs, sim_vnf_rtt, 'bs')
    # plt.errorbar(x_vnfs, emu_vnf_rtt, yerr=emu_vnf_std, fmt='none', ecolor='black', capsize=2)
    # plt.xticks(x_vnfs, sim_vnf_length)
    plt.xlabel('Different service/source combinations (chain length)')
    plt.ylabel('Inter-VNF RTT (in ms)')


    # plot delay differences
    plt.figure(2)
    chain_diffs = [emu_chain_rtt[i]-sim_chain_rtt[i] for i in range(len(emu_chain_rtt))]
    plt.subplot(2, 1, 1)
    plt.plot(x_chain, chain_diffs)
    # plt.xticks(x_chain, sim_chain_length)
    plt.ylabel('Chain RTT diff. (in ms)')
    plt.title('Emulation delay - simulation delay')

    vnf_diffs = [emu_vnf_rtt[i]-sim_vnf_rtt[i] for i in range(len(emu_vnf_rtt))]
    plt.subplot(2, 1, 2)
    plt.plot(x_vnfs, vnf_diffs)
    # plt.xticks(x_vnfs, sim_vnf_length)
    plt.xlabel('Different service/source combinations (chain length)')
    plt.ylabel('Inter-VNF RTT diff. (in ms)')


    plt.show()


    # TODO: analyze big difference in VNF delays!
    # => FIXME: this seems to be some problem with ordering! => ensure, I'm comparing the right inter-VNF delays (also chains)! don't rely on sorting..


if __name__ == '__main__':
    emu_delays = process_emu_results()
    sim_delays = process_sim_results()
    plot(emu_delays, sim_delays)
