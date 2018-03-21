# read and visualize result files
import glob
import yaml
import matplotlib.pyplot as plt


# emulation results
emu_results = glob.glob('../eval/emulation/*.yaml')
emu_chain_rtt = []
emu_vnf_rtt = []
emu_vnf_std = []
for result_file in emu_results:
    with open(result_file, 'r') as f:
        result = yaml.load(f)
        # chain delays = httping = TCP handshake = 2x RTT
        emu_chain_rtt.append(result['chain_delay']['delay'] / 2)

        # vnf delays = ping = RTT
        for delay in result['delays']:
            emu_vnf_rtt.append(delay['delay'])
            emu_vnf_std.append(delay['stddev'])


# placement results
bjointsp_results = glob.glob('../eval/bjointsp/*.yaml')
bjointsp_chain_rtt = []
bjointsp_vnf_rtt = []
for result_file in bjointsp_results:
    with open(result_file, 'r') as f:
        result = yaml.load(f)
        # one-way = RTT/2
        bjointsp_chain_rtt.append(result['metrics']['total_delay'] * 2)
        for delay in result['metrics']['delays']:
            bjointsp_vnf_rtt.append(delay['delay'] * 2)


# plot chain delays
x_chain = range(len(emu_chain_rtt))
plt.subplot(2, 1, 1)
plt.plot(x_chain, emu_chain_rtt, 'g^', x_chain, bjointsp_chain_rtt, 'bs')
plt.legend(['Emulation', 'Placement (simulation)'])
plt.ylabel('Chain RTT delays (in ms)')
plt.title('Delay comparison between emulation and simulation')

# plot inter-VNF delays
x_vnfs = range(len(emu_vnf_rtt))
plt.subplot(2, 1, 2)
plt.plot(x_vnfs, emu_vnf_rtt, 'g^', x_vnfs, bjointsp_vnf_rtt, 'bs')
plt.errorbar(x_vnfs, emu_vnf_rtt, yerr=emu_vnf_std, fmt='none', ecolor='black', capsize=2)
plt.xlabel('Different service/source combinations')
plt.ylabel('VNF RTT delays (in ms)')

plt.show()

# TODO: analyze big difference in VNF delays!
# TODO: plot the delay difference as a function of the total (simulation) delay?
# TODO: modularize
