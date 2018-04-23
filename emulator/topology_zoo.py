"""
Copyright (c) 2017 SONATA-NFV and Paderborn University
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the SONATA-NFV, Paderborn University
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.

This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).
"""
import logging
import argparse
import networkx as nx
import signal
import time
from geopy.distance import vincenty
import numpy as np
from mininet.net import Containernet
from mininet.log import setLogLevel
from mininet.link import TCLink
from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint

logging.basicConfig(level=logging.INFO)
setLogLevel('info')  # set Mininet loglevel
logging.getLogger('werkzeug').setLevel(logging.INFO)
logging.getLogger('dcemulator.node').setLevel(logging.INFO)
logging.getLogger('dcemulator.net').setLevel(logging.INFO)
LOG = logging.getLogger("vim-emu.topologyzoo")
LOG.setLevel(logging.DEBUG)

"""
Assumptions & properties

Default link bw: 100 Mbps * BW_SCALE_FACTOR (used if not given in topology)
Default link delay: 1 ms (used if not given in topology)
"""
SPEED_OF_LIGHT = 299792458  # meter per second
PROPAGATION_FACTOR = 0.77  # https://en.wikipedia.org/wiki/Propagation_delay
BW_SCALE_FACTOR = 0.1  # downscale all link bandwidths to work with Containernet 


class TopologyZooTopology(object):

    def __init__(self, args):
        # run daemonized to stop on signal
        self.running = True
        signal.signal(signal.SIGINT, self._stop_by_signal)
        signal.signal(signal.SIGTERM, self._stop_by_signal)

        self.args = args
        self.G = self._load_graphml(args.graph_file)
        self.G_name = self.G.graph.get("label", args.graph_file)
        LOG.debug("Graph label: {}".format(self.G_name))
        self.net = None
        self.pops = list()
         # initialize global rest api
        self.rest_api = RestApiEndpoint("0.0.0.0", 5001)
        self.rest_api.start()
        # initialize and start topology
        self.create_environment()
        self.create_pops()
        self.create_links()
        self.start_topology()
        self.daemonize()
        self.stop_topology()

    def _load_graphml(self, path):
        try:
            G = nx.read_graphml(path, node_type=int)
            LOG.info("Loaded graph from '{}' with {} nodes and {} edges."
                     .format(path, G.__len__(), G.size()))
            LOG.debug(G.adjacency_list())
            return G
        except:
            LOG.exception("Could not read {}".format(path))
        return None

    def create_environment(self):
        self.net = DCNetwork(monitor=False, enable_learning=False)
        self.rest_api.connectDCNetwork(self.net)

    def create_pops(self):
        i = 0
        for n in self.G.nodes(data=True):
            # name = n[1].get("label").replace(" ", "_")  # human readable names
            name = "pop{}".format(n[0])  # use ID as name
            p = self.net.addDatacenter(name)
            self.rest_api.connectDatacenter(p)
            self.pops.append(p)
            LOG.info("Created pop: {} representing {}"
                     .format(p, n[1].get("label", n[0])))

    def create_links(self):
        for e in self.G.edges(data=True):
            # parse bw limit from edge
            bw_mbps = self._parse_bandwidth(e)
            # calculate delay from nodes; use np.around for consistent rounding behavior in phyton2 and 3
            delay = np.around(self._calc_delay_ms(e[0], e[1]))
            try:
                self.net.addLink(self.pops[e[0]], self.pops[e[1]],
                                 cls=TCLink,
                                 delay='{}ms'.format(int(delay)),
                                 bw=min(bw_mbps, 1000))
                LOG.info("Created link: {}".format(e))
            except:
                    LOG.exception("Error in experiment")

    def _parse_bandwidth(self, e):
        """
        Calculate the link bandwith based on LinkLabel field.
        Default: 100 Mbps (if field is not given)
        Result is returned in Mbps and down scaled by 10x to fit in the Mininet range.
        """
        ll = e[2].get("LinkLabel")
        if ll is None:
            return 100  # default
        ll = ll.strip(" <>=")
        mbits_factor = 1.0
        if "g" in ll.lower():
            mbits_factor = 1000
        elif "k" in ll.lower():
            mbits_factor = (1.0 / 1000)
        ll = ll.strip("KMGkmpsbit/-+ ")
        try:
            bw = float(ll) * mbits_factor
        except:
            LOG.warning("Could not parse bandwidth: {}".format(ll))
            bw = 100  # default
        LOG.debug("- Bandwidth {}-{} = {} Mbps"
              .format(e[0], e[1], bw))    
        return bw * BW_SCALE_FACTOR  # downscale to fit in mininet supported range

    def _calc_distance_meter(self, n1id, n2id):
        """
        Calculate distance in meter between two geo positions.
        """
        n1 = self.G.nodes(data=True)[n1id]
        n2 = self.G.nodes(data=True)[n2id]
        n1_lat, n1_long = n1[1].get("Latitude"), n1[1].get("Longitude")
        n2_lat, n2_long = n2[1].get("Latitude"), n2[1].get("Longitude")
        try:
            return vincenty((n1_lat, n1_long), (n2_lat, n2_long)).meters
        except:
            LOG.exception("Could calculate distance between nodes: {}/{}"
                  .format(n1id, n2id))
        return 0

    def _calc_delay_ms(self, n1id, n2id):
        meter = self._calc_distance_meter(n1id, n2id)
        if meter <= 0:
            return 1  # default 1 ms delay
        LOG.debug("- Distance {}-{} = {} km"
              .format(n1id, n2id, meter / 1000))
        # calc delay
        delay = (meter / SPEED_OF_LIGHT * 1000) * PROPAGATION_FACTOR  # in milliseconds
        LOG.debug("- Delay {}-{} = {} ms (rounded: {} ms)"
              .format(n1id, n2id, delay, round(delay)))
        return delay

    def start_topology(self):
        print("start_topology")
        self.net.start()

    def cli(self):
        self.net.CLI()

    def daemonize(self):
        print("Daemonizing vim-emu. Send SIGTERM or SIGKILL to stop.")
        while self.running:
            time.sleep(1)

    def _stop_by_signal(self, signum, frame):
        print("Received SIGNAL {}. Stopping.".format(signum))
        self.running = False
        
    def stop_topology(self):
        self.rest_api.stop()
        self.net.stop()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Emulator TopologyZoo Reader")
    parser.add_argument(
        "-g",
        "--graph",
        help="Input GraphML file",
        required=True,
        default=None,
        dest="graph_file")
    return parser.parse_args()


def main():
    args = parse_args()
    LOG.debug("Args: {}".format(args))
    t = TopologyZooTopology(args)
    # t.cli()
    # t.stop_topology()


if __name__ == '__main__':
    main()
