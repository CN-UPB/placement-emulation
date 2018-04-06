# help with writing consistent output files
import os
from datetime import datetime
import yaml


# dump placement to yaml file with suitable name in specified subfolder
def write_placement(network, service, sources, placement, subfolder):
    # network-service-source-timestamp.yaml
    result_file = os.path.basename(network).split('.')[0] + '-' \
                + os.path.basename(service).split('.')[0] + '-' \
                + os.path.basename(sources).split('.')[0] + '-' \
                + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.yaml'
    result_directory = os.path.join("results/" + subfolder)
    result_path = os.path.join(result_directory, result_file)
    # create subfolder if necessary
    os.makedirs(os.path.dirname(result_path), exist_ok=True)

    # write placement
    with open(result_path, 'w', newline='') as f:
        yaml.dump(placement, f, default_flow_style=False)
        print("Writing solution to {}".format(result_path))

    return result_path
