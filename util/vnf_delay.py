# simple script to copy and adjust simulation results to include a fixed VNF processing delay
import glob
import yaml


# quick and drity. just run once!
sim_files = glob.glob('../eval/Abilene/greedy/with_vnf_delay/*.yaml')
for sim_f in sim_files:
    with open(sim_f, 'r') as f:
        result = yaml.load(f)
        vnf_delay = len(result['placement']['vnfs'])
        result['metrics']['total_delay'] += vnf_delay
    with open(sim_f, 'w', newline='') as f:
        yaml.dump(result, f, default_flow_style=False)
