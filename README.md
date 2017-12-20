# placement-emulation
Automatically emulate network service placements calculated by placement algorithms

The `placement` folder contains the input files and the result of placing a simple chain with 3 VNFs on a 4-node network.

The `topologies` folder contains [TopologyZoo](http://www.topology-zoo.org) topologies given as `*.graphml` files.

The `vnfs` folder contains a couple of example VNFs (as Docker files to be build locally).

## Emulation environment

### Prerequisites

1. Install [`vim-emu`](https://osm.etsi.org/gitweb/?p=osm/vim-emu.git) (see [README.md "Bare-metal installation"](https://osm.etsi.org/gitweb/?p=osm/vim-emu.git;a=blob;f=README.md;h=ba22ec342ed5d60bf65770aa154adce8b0fcc141;hb=HEAD))
1. Build VNF containers: `cd vnfs; ./build.sh`
1. Install some other dependencies
    * `pip install geopy`

### Start a topology

1. `sudo python emulator/topology_zoo.py -g topologies/Abilene.graphml`
1. Check if everything is working (other terminal): `vim-emu datacenter list`

### Start and place a service (example)

TODO



### Notes

* Each node of the given graph is turned into an emulated datacenter (PoP)
* PoPs are named based on the node IDs of the networkx graph (not their labels): `pop<ID>` e.g. `pop42`
