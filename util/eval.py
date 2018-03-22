# read and visualize result files
import glob
import yaml
import matplotlib.pyplot as plt


# TODO: store and process delays in an ordered fashion! (see fixme below)

def process_emu_results():
    # TODO: clean up/remove separate lists for delay, std, etc
    emu_results = glob.glob('../eval/emulation/*.yaml')
    emu_delays = []
    emu_chain_rtt = []
    emu_vnf_rtt = []
    emu_vnf_std = []
    for result_file in emu_results:
        with open(result_file, 'r') as f:
            result = yaml.load(f)

            # chain delays = httping = TCP handshake = 2x RTT
            result['chain_rtt'] = result['chain_delay']['delay'] / 2
            emu_chain_rtt.append(result['chain_delay']['delay'] / 2)

            # vnf delays = ping = RTT
            for delay in result['delays']:
                delay['rtt'] = delay['delay']
                emu_vnf_rtt.append(delay['delay'])
                emu_vnf_std.append(delay['stddev'])

            emu_delays.append(result)
    return emu_delays


def process_bjointsp_results():
    # TODO: calc rtts and return process result list similar to emu results
    bjointsp_results = glob.glob('../eval/bjointsp/*.yaml')
    bjointsp_delays = []
    bjointsp_chain_length = []      # num vnfs in the chain
    bjointsp_chain_rtt = []
    bjointsp_vnf_length = []        # num vnfs in the chain
    bjointsp_vnf_rtt = []
    for result_file in bjointsp_results:
        with open(result_file, 'r') as f:
            result = yaml.load(f)
            bjointsp_delays.append(result)
            # cut chain length from service name, eg, "fw1chain.yaml" - WARNING: this will not work with generic names
            chain_length = int(result['input']['service'][2]) + 2        # +2 for user and web
            bjointsp_chain_length.append(chain_length)
            # one-way = RTT/2
            bjointsp_chain_rtt.append(result['metrics']['total_delay'] * 2)
            for delay in result['metrics']['delays']:
                bjointsp_vnf_length.append(chain_length)
                bjointsp_vnf_rtt.append(delay['delay'] * 2)


def plot():
    # TODO: work with sorted, processed result lists instead of separate lists for everything
    # plot chain delays
    plt.figure(1)
    x_chain = range(len(emu_chain_rtt))
    plt.subplot(2, 1, 1)
    plt.plot(x_chain, emu_chain_rtt, 'g^', x_chain, bjointsp_chain_rtt, 'bs')
    plt.xticks(x_chain, bjointsp_chain_length)
    plt.legend(['Emulation', 'Placement (simulation)'])
    plt.ylabel('Chain RTT (in ms)')
    plt.title('Delay comparison between emulation and simulation')

    # plot inter-VNF delays
    x_vnfs = range(len(emu_vnf_rtt))
    plt.subplot(2, 1, 2)
    plt.plot(x_vnfs, emu_vnf_rtt, 'g^', x_vnfs, bjointsp_vnf_rtt, 'bs')
    plt.errorbar(x_vnfs, emu_vnf_rtt, yerr=emu_vnf_std, fmt='none', ecolor='black', capsize=2)
    plt.xticks(x_vnfs, bjointsp_vnf_length)
    plt.xlabel('Different service/source combinations (chain length)')
    plt.ylabel('Inter-VNF RTT (in ms)')


    # plot delay differences
    plt.figure(2)
    chain_diffs = [emu_chain_rtt[i]-bjointsp_chain_rtt[i] for i in range(len(emu_chain_rtt))]
    plt.subplot(2, 1, 1)
    plt.plot(x_chain, chain_diffs)
    plt.xticks(x_chain, bjointsp_chain_length)
    plt.ylabel('Chain RTT diff. (in ms)')
    plt.title('Emulation delay - simulation delay')

    vnf_diffs = [emu_vnf_rtt[i]-bjointsp_vnf_rtt[i] for i in range(len(emu_vnf_rtt))]
    plt.subplot(2, 1, 2)
    plt.plot(x_vnfs, vnf_diffs)
    # plt.xticks(x_vnfs, bjointsp_vnf_length)
    plt.xlabel('Different service/source combinations (chain length)')
    plt.ylabel('Inter-VNF RTT diff. (in ms)')


    plt.show()


    # TODO: analyze big difference in VNF delays!
    # => FIXME: this seems to be some problem with ordering! => ensure, I'm comparing the right inter-VNF delays (also chains)! don't rely on sorting..


if __name__ == '__main__':
    pass
    # TODO: call other methods: process, then plot
