# placement-emulation
Automatically emulate network service placements calculated by placement algorithms

Folder structure:

* `emulator`: `topology_zoo.py` script, reading a Topology Zoo network and starting it in `vim-emu` 
* `measurement`: Scripts for measuring the delay between VNFs and on the whole chain (with `ping` and `httping`)
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
vnf_user httping --proxy 10.0.0.2:3128 --url http://20.0.0.2 -p 8899 -c 5
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

Python 3.5+

Install [`bjointsp 2.1+`](https://github.com/CN-UPB/B-JointSP/tree/placement-emulation) (use `setup.py` in the `placement-emulation` branch)

### Place and emulate

1. Select a network topology from `topologies`, e.g., `Abilene.graphml`, as well as a template and sources, defined by `csv` files. See `placement/example-input` for examples.
2. Start the topology on `vim-emu` as described [above](https://github.com/CN-UPB/placement-emulation#start-a-topology), e.g., `sudo python emulator/topology_zoo.py -g topologies/Abilene.graphml`
3. Start the placement and emulation with `python3 placement/placement_emulator.py -n topologies/Abilene.graphml -t placement/example-input/template.csv -s placement/example-input/sources.csv`.
4. You can test the deployment and connectivity as described [above](https://github.com/CN-UPB/placement-emulation#testing-the-deployment).
5. `measurement` contains scripts for measuring the delay between VNFs and on the whole chain. E.g., run `./measurements/measure.sh |& tee -a results/1fw.log` to also log to file.

Note: If you only want to trigger placement without emulation, use the `--placeOnly` option when calling `placement_emulator.py`.



The repository also contains examples without the proxy, which may introduce unexpected effects. These examples contain 1-2 L4FW or 1-2 bridges instead. While L4FW each require a separate TCP connection, leading to higher delays with `httping`, the bridges don't such that there's only one TCP connection from the user to the web server.


## Example input
### Abilene network
The figure below visualizes the Abilene network (from SNDlib). Our topology (from Topology Zoo) only has 11 nodes, missing the "ATLAM5" node.

The black numbers illustrate the pop number used by the `vim-emu` and the placement algorithm. The dark red numbers indicate the rounded link delay between the pops (as used here). This is supposed to support and simplify the analysis of delay measurements.

![abilene](abilene.jpg)


### Network service chains
We use chains of varying length, in which a user (1st "VNF") requests content from a web server (last VNF). In between, there are 1 to 3 forwarding VNFs (either layer 2 or layer 4).

#### Chains with layer-4 forwarders (socat)
L4FW are connected with separate TCP connections. Each TCP connection is setup using TCP's 3-way handshake, leading to considerable delay. These are the different chains (interfaces in brackets):

```
vnf_user (88.0.0.1/24) --> (88.0.0.2/24) vnf_fw1 (99.0.0.1/24) --> (99.0.0.2/24) vnf_web
```

```
vnf_user (77.0.0.1/24) --> (77.0.0.2/24) vnf_fw2 (88.0.0.1/24) --> (88.0.0.2/24) vnf_fw1 (99.0.0.1/24) --> (99.0.0.2/24) vnf_web
```

```
vnf_user (66.0.0.1/24) --> (66.0.0.2/24) vnf_fw3 (77.0.0.1/24) --> (77.0.0.2/24) vnf_fw2 (88.0.0.1/24) --> (88.0.0.2/24) vnf_fw1 (99.0.0.1/24) --> (99.0.0.2/24) vnf_web
```

#### Chains with layer-2 forwarders (bridges)
Here, user and web server are directly connected with a single TCP connection, thus requiring shorter setup delay.

```
vnf_user (88.0.0.1/24) --> (88.0.0.2/24) vnf_bridge1 (88.0.0.3/24) --> (88.0.0.4/24) vnf_web
```

```
vnf_user (88.0.0.1/24) --> (88.0.0.2/24) vnf_bridge2 (88.0.0.3/24) --> (88.0.0.4/24) vnf_bridge1 (88.0.0.5/24) --> (88.0.0.6/24) vnf_web
```

```
vnf_user (88.0.0.1/24) --> (88.0.0.2/24) vnf_bridge3 (88.0.0.3/24) --> (88.0.0.4/24) vnf_bridge2 (88.0.0.5/24) --> (88.0.0.6/24) vnf_bridge1 (88.0.0.7/24) --> (88.0.0.8/24) vnf_web
```

