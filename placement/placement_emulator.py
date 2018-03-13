import argparse
import yaml
import requests
import ast
import bjointsp.main as bjointsp


compute_url = "http://127.0.0.1:5001/restapi/compute/"
network_url = "http://127.0.0.1:5001/restapi/network"
config_prefix = " -H 'Content-Type: application/json' -d "


def emulate_placement(placement):
    with open(placement, "r") as place_file:
        result = yaml.load(place_file)

        # start placed VNF instances on the emulator
        for vnf in result["placement"]["vnfs"]:
            data = ast.literal_eval(vnf["image"])			# convert string config to dict
            response = requests.put(compute_url + vnf["node"] + "/" + vnf["name"], json=data)
            print("Adding VNF " + vnf["name"] + " at " + vnf["node"] + ". Success: " + str(response.status_code == requests.codes.ok))

        # connect instances along calculated edges
        for vlink in result["placement"]["vlinks"]:
            src = vlink["src_vnf"]
            dst = vlink["dest_vnf"]
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
    placement = bjointsp.place(args.network, args.template, args.sources, cpu=1, mem=10, dr=50)
    if args.placeOnly:
        print("\nPlacement complete; no emulation (--placeOnly).")
    else:
        print("\n\nEmulating calculated placement:\n")
        emulate_placement(placement)


if __name__ == '__main__':
    main()

# TODO: what about scaling? ports & connections need to be decided dynamically. load balancing?
