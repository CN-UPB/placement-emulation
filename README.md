# placement-emulation
Automatically emulate network service placements calculated by placement algorithms

The `placement` folder contains the input files and the result of placing a simple chain with 3 VNFs on a 4-node network.

The `topologies` folder contains [TopologyZoo](http://www.topology-zoo.org) topologies given as `*.graphml` files.

The `vnfs` folder contains a couple of example VNFs (as Docker files to be build locally).

## Emulation environment

### Prerequisites

1. Install [`vim-emu`](https://osm.etsi.org/gitweb/?p=osm/vim-emu.git) (see [README.md "Bare-metal installation"](https://osm.etsi.org/gitweb/?p=osm/vim-emu.git;a=blob;f=README.md;h=ba22ec342ed5d60bf65770aa154adce8b0fcc141;hb=HEAD))
1. Pre-build VNF containers: `cd vnfs; ./build.sh`
1. Install some other dependencies
    * `pip install geopy`

### Start a topology

1. `sudo python emulator/topology_zoo.py -g topologies/Abilene.graphml`
1. Check if everything is working (other terminal): `vim-emu datacenter list`

### Start and place a service (example)

#### Used service

The used service has four containers:
`User -> Proxy (Squid) -> L4FW (Socat) -> Webservice (Apache)`

#### Deployment steps

```bash
# deploy VNFs
vim-emu compute start -n vnf_user -i placement-user-img --net '(id=output,ip=10.0.0.1/24)' -d pop0

vim-emu compute start -n vnf_proxy -i placement-squid-img --net '(id=input,ip=10.0.0.2/24),(id=output,ip=20.0.0.1/24)' -d pop1

vim-emu compute start -n vnf_l4fw -i placement-socat-img --net '(id=input,ip=20.0.0.2/24),(id=output,ip=30.0.0.1/24)' -d pop2

vim-emu compute start -n vnf_web -i placement-apache-img --net '(id=input,ip=30.0.0.2/24)' -d pop3

# setup network forwarding rules
vim-emu network add -src vnf_user:output -dst vnf_proxy:input
vim-emu network add -src vnf_proxy:output -dst vnf_l4fw:input
vim-emu network add -src vnf_l4fw:output -dst vnf_web:input

```

#### Testing the deployment

```bash
# check deployment
vim-emu compute list
+--------------+-------------+----------------------+------------------+-------------------------+
| Datacenter   | Container   | Image                | Interface list   | Datacenter interfaces   |
+==============+=============+======================+==================+=========================+
| pop3         | vnf_web     | placement-apache-img | input            | dc4.s1-eth3             |
+--------------+-------------+----------------------+------------------+-------------------------+
| pop2         | vnf_l4fw    | placement-socat-img  | input,output     | dc3.s1-eth3,dc3.s1-eth4 |
+--------------+-------------+----------------------+------------------+-------------------------+
| pop1         | vnf_proxy   | placement-squid-img  | input,output     | dc2.s1-eth3,dc2.s1-eth4 |
+--------------+-------------+----------------------+------------------+-------------------------+
| pop0         | vnf_user    | placement-user-img   | output           | dc1.s1-eth3             |
+--------------+-------------+----------------------+------------------+-------------------------+

# check basic connectivity
vnf_user ping -c3 10.0.0.2
vnf_proxy ping -c3 20.0.0.2
vnf_l4fw ping -c3 30.0.0.2
```

#### Manual RTT measurement

TODO


### Notes

* Each node of the given graph is turned into an emulated datacenter (PoP)
* PoPs are named based on the node IDs of the networkx graph (not their labels): `pop<ID>` e.g. `pop42`
* Link latencies are calculated based on node's geo. locations
* Link bandwidth is set if given in the graph (not many topologies have it)


## Placement

...
