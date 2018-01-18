# placement-emulation
Automatically emulate network service placements calculated by placement algorithms

Folder structure:

* `emulator`: `topology_zoo.py` script, reading a Topology Zoo network and starting it in `vim-emu` 
* `placement`: `placement_emulator.py` triggers the `bjointsp` placement algorithm and starts the placed VNFs on the emulator
  * `placement/example-input`: example input for the placement algorithm
* `topologies`: Contains [TopologyZoo](http://www.topology-zoo.org) topologies given as `*.graphml` files
* `vnfs`: Contains a couple of example VNFs (as Docker files to be build locally)

More details are provided below.

## Emulation environment

### Prerequisites

1. Install [`vim-emu`](https://osm.etsi.org/gitweb/?p=osm/vim-emu.git) (see [README.md "Bare-metal installation"](https://osm.etsi.org/gitweb/?p=osm/vim-emu.git;a=blob;f=README.md;h=ba22ec342ed5d60bf65770aa154adce8b0fcc141;hb=HEAD))
    * `cd vim-emu; sudo python setup.py develop`
2. Pre-build VNF containers: `cd vnfs; ./build.sh`
3. Install some other dependencies
    * `pip install geopy`

### Start a topology

1. `sudo python emulator/topology_zoo.py -g topologies/Abilene.graphml`
2. Check if everything is working (other terminal): `vim-emu datacenter list`

### Start and place a service (example)

#### Used service

The used service has four containers:
`User -> Proxy (Squid) -> L4FW (Socat) -> Webservice (Apache)`

```
     Example Service Chain an IPs

       +-------+        +------+
       |       |        |      |
       |  User |        | Web  |
       |       |        |      |
       +-------+        +---^--+
10.0.0.1/24|                | 30.0.0.2/24
           |                |
10.0.0.2/24|                | 30.0.0.1/24
       +---v---+        +---+--+
       |       |        |      |
       | Proxy +--------> L4FW |
       |       |        |      |
       +-------+        +------+
         20.0.0.1/24  20.0.0.2/24


```

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
(this script is also available in `emulator/deploy_example.sh`)

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
containernet> vnf_user ping -c3 10.0.0.2
containernet> vnf_proxy ping -c3 20.0.0.2
containernet> vnf_l4fw ping -c3 30.0.0.2

# full chain HTTP connectivity
containernet> vnf_user curl -x http://10.0.0.2:3128 http://20.0.0.2:8899
```

This `curl` command might look confusing. It does the following:

* a HTTP request to the IP of `vnf_l4fw` that forwards the request arriving at port `TCP:8899` to `vnf_web` on port `TCP:80`
* for the request it has to use the proxy (`vnf_proxy`) which is specified by `-x http://10.0.0.2:3128`

#### Manual RTT measurement

(in a new terminal)
```bash
# log into to vnf_user
docker exec -it mn.vnf_user /bin/bash

# basic check
vnf_user curl -x http://10.0.0.2:3128 http://20.0.0.2:8899 -v

# use httping to measure RTT between user and vnf_web
httping --proxy 10.0.0.2:3128 --url http://20.0.0.2 -p 8899 -c 5
```

#### Shut down experiment

```bash
containernet> exit
```

### Notes

* Each node of the given graph is turned into an emulated datacenter (PoP)
* PoPs are named based on the node IDs of the networkx graph (not their labels): `pop<ID>` e.g. `pop42`
* Link latencies are calculated based on node's geo. locations
* Link bandwidth is set if given in the graph (not many topologies have it)


## Placement

### Prerequisites

Python 3.5+ (on Ubuntu 16.04 always use `python3` instead of `python`)

Install [`bjointsp`](https://github.com/CN-UPB/B-JointSP/tree/placement-emulation) (use `setup.py` in the `placement-emulation` branch)

### Place and emulate

1. Select a network topology from `topologies`, e.g., `Abilene.graphml`, and create a `csv` files describing the placement scenario (template, network, sources - see `placement/example-input`).
2. Start the topology on `vim-emu` as described [above](https://github.com/CN-UPB/placement-emulation#start-a-topology), e.g., `sudo python emulator/topology_zoo.py -g topologies/Abilene.graphml`
3. Start the placement and emulation with `python placement/placement_emulator.py -s placement/example_input/scenario.csv`.
4. You can list the deployed VNFs with `vim-emu compute list` and check their connectivity in the `containernet` terminal with `vnf1 ping -c 3 vnf2`.

Note: If you only want to trigger placement without emulation, use the `--placeOnly` option when calling `placement_emulator.py`.

### TODO

* Create VNFs with multiple interfaces and connect them correctly if necessary. Eg, S->A->B: A needs 2 interfaces to work correctly.
* Combine `topology_zoo` and `placement_emulator` in one script (or call them from one script) so that everything can be started with one command
* Pass placement arguments via command line, not specified in a `scenario.csv` (cleaner & more flexible approach)
