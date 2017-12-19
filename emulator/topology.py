"""
Copyright (c) 2015 5GTANGO
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
Neither the name of the 5GTANGO [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.
This work has been performed in the framework of the 5GTANGO project,
funded by the European Commission under Grant number 761493 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the 5GTANGO
partner consortium (www.5gtango.eu).
"""


# simple, manually created 3-node network (chain)
# TODO: copy into son-emu's examples folder
import logging
from mininet.log import setLogLevel
from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from mininet.node import RemoteController

logging.basicConfig(level=logging.INFO)


def create_topology1():
	net = DCNetwork(controller=RemoteController, monitor=False, enable_learning=False)

	# metadata just for info; not used anywhere (only before during placement)
	dc0 = net.addDatacenter("0", metadata={"cpu": 0, "mem": 0})
	dc1 = net.addDatacenter("1", metadata={"cpu": 10, "mem": 10})
	dc2 = net.addDatacenter("2", metadata={"cpu": 10, "mem": 10})

	# links are bidirectional
	net.addLink(dc0, dc1, delay="10ms")
	net.addLink(dc1, dc2, delay="10ms")

	# create a new instance of a endpoint implementation
	rapi = RestApiEndpoint("127.0.0.1", 5001, net)
	rapi.connectDatacenter(dc0)
	rapi.connectDatacenter(dc1)
	rapi.connectDatacenter(dc2)
	rapi.start()

	net.start()
	net.CLI()
	net.stop()			# when the user types exit in the CLI, we stop the emulator


def main():
	setLogLevel('info')  		# set Mininet loglevel
	create_topology1()


if __name__ == '__main__':
	main()
