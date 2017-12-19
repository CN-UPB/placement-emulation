import csv
import requests


# parse placement result and issue REST API calls to instantiate and chain the VNFs in the emulator accordingly
def emulate_embedding(embedding):
	compute_url = "http://127.0.0.1:5001/restapi/compute/"
	network_url = "http://127.0.0.1:5001/restapi/network/"
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
						response = requests.put(compute_url + f"{dc}/{vnf}")
						print(response)

				# recreate edges from previous embedding
				if read_edges:
					if len(row) == 4:
						pass
						# TODO: rest call to connect vnfs


embedding = "placement/result.csv"
emulate_embedding(embedding)
