import argparse
import requests
import ast
import bjointsp.main as bjointsp


compute_url = "http://127.0.0.1:5001/restapi/compute/"
network_url = "http://127.0.0.1:5001/restapi/network"
config_prefix = " -H 'Content-Type: application/json' -d "


def emulate_placement(overlays, templates):
	for ol in overlays.values():
		# start placed VNF instances on the emulator
		for i in ol.instances:
			data = ast.literal_eval(i.component.config)			# convert string config to dict
			response = requests.put(compute_url + i.location + "/" + str(i.component), json=data)
			print("Adding VNF " + str(i.component) + " at " + i.location + ". Success: " + str(response.status_code == requests.codes.ok))
			
		# connect instances along calculated edges
		for e in ol.edges:
			src = str(e.source.component)
			dst = str(e.dest.component)
			data = {"vnf_src_name":src, "vnf_dst_name":dst, "vnf_src_interface":"output", "vnf_dst_interface":"input", "bidirectional":"True"}
			response = requests.put(network_url, json=data)
			print("Adding link from " + src + " to " + dst + ". Success: " + str(response.status_code == requests.codes.ok))


def parse_args():
	parser = argparse.ArgumentParser(description="Triggers placement and then emulation")
	parser.add_argument("-n", "--network", help="Network input file (.graphml)", required=True, default=None, dest="network")
	parser.add_argument("-t", "--template", help="Template input file (.csv)", required=True, default=None, dest="template")
	parser.add_argument("-s", "--sources", help="Sources input file (.csv)", required=True, default=None, dest="sources")
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
	result, overlays, templates = bjointsp.heuristic(args.network, args.template, args.sources, graphml_network=True, cpu=10, mem=10, dr=50)
	if not args.placeOnly:
		print("\n\nEmulating calculated placement:\n")
		#emulate_placement_from_file(result)
		emulate_placement(overlays, templates)
	else:
		print("\nPlacement complete; no emulation (--placeOnly).")


if __name__ == '__main__':
	main()

# TODO: what about scaling? ports & connections need to be decided dynamically
