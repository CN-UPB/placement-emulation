import csv
import requests
import json


# parse placement result and issue REST API calls to instantiate and chain the VNFs in the emulator accordingly
def emulate_embedding(embedding):
	compute_url = "http://127.0.0.1:5001/restapi/compute/"
	network_url = "http://127.0.0.1:5001/restapi/network"
	read_instances, read_edges = False, False
	with open(embedding, "r") as embedding_file:
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


embedding = "placement/result.csv"
emulate_embedding(embedding)

