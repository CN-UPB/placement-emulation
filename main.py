import csv
import requests
import networkx as nx
import bjointsp.read_write.reader as reader


# read network topology from Topology Zoo in GraphML using NetworkX
def read_network(network_file, node_cpu, node_mem):
	network = nx.read_graphml(network_file, node_type=int)
	# assign specified node capacities
	for n in network.nodes:
		network.nodes[n]["cpu"] = node_cpu
		network.nodes[n]["mem"] = node_mem
	# TODO: use same methods as topology_zoo to read network and set delay & bandwidth for links


# parse placement result and issue REST API calls to instantiate and chain the VNFs in the emulator accordingly
def emulate_placement(placement):
	compute_url = "http://127.0.0.1:5001/restapi/compute/"
	network_url = "http://127.0.0.1:5001/restapi/network"
	read_instances, read_edges = False, False
	with open(placement, "r") as embedding_file:
		reader = csv.reader((row for row in embedding_file), delimiter="\t")
		for row in reader:
			if len(row) > 0:
				if row[0].startswith("#"):
					read_instances = False
					read_edges = False
				if row[0].startswith("# instances:"):
					read_instances = True
				elif row[0].startswith("# edges:"):
					read_edges = True

				# recreate instances from previous embedding
				if read_instances:
					if len(row) == 2:
						dc = row[1];
						vnf = row[0];
						response = requests.put(compute_url + dc + "/" +vnf)
						print("Adding VNF " + vnf + " at " + dc + ". Success: " + str(response.status_code == requests.codes.ok))

				# recreate edges from previous embedding (edge format: "A.0->B.0 ...."
				if read_edges:
					if len(row) == 4:
						src = row[0].split("->")[0].split(".")[0]
						dst = row[0].split("->")[1].split(".")[0]
						data = {"vnf_src_name":src, "vnf_dst_name":dst, "vnf_src_interface":src+"-eth0", "vnf_dst_interface":dst+"-eth0", "bidirectional":True}
						response = requests.put(network_url, json=data)
						print("Adding link from " + src + " to " + dst + ". Success: " + str(response.status_code == requests.codes.ok))


# placement_result = "placement/result.csv"
# emulate_placement(placement_result)
# read_network("topologies/Abilene.graphml", 10, 10)
# TODO: adjust bjointsp to support triggering the MIP and heuristic from the outside
# TODO: take network, template, sources as cmd args
# TODO: read network from graphml
