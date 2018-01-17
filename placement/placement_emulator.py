import csv
import argparse
import requests
import bjointsp.main as bjointsp


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


def parse_args():
	parser = argparse.ArgumentParser(description="Triggers placement and then emulation")
	parser.add_argument(
		"-s",
		"--scenario",
		help="Input scenario file (.csv)",
		required=True,
		default=None,
		dest="scenario")
	# parser.add_argument("-n", "--network", help="Network input file (.graphml)", required=True, default=None, dest="network")
	# parser.add_argument("-t", "--template", help="Template input file (.csv)", required=True, default=None, dest="template")
	# parser.add_argument("-s", "--sources", help="Sources input file (.csv)", required=True, default=None, dest="scources")
	parser.add_argument(
		"--placeOnly",
		help="Only perform placement, do not trigger emulation.",
		required=False,
		default=False,
		action="store_true",
		dest="placeOnly")
	return parser.parse_args()


def main():
	args = parse_args()
	# TODO: allow to set cpu, mem, dr as args; or take them from graphml
	result = bjointsp.heuristic(args.scenario, graphml_network=True, cpu=10, mem=10, dr=50)
	if not args.placeOnly:
		print("\n\nEmulating calculated placement:\n")
		emulate_placement(result)
	else:
		print("\nPlacement complete; no emulation (--placeOnly).")


if __name__ == '__main__':
	main()


# FIXME: not all network links are created correctly. in the example, A->B supposedly was created but ping doesn't work
# TODO: take network, template, sources as cmd args instead of reading them from a scenario file
# TODO: start topology_zoo and placement_emulator from one script with one command
