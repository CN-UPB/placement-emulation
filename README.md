# Generic Placement Emulation Framework
This placement emulation framework (PEF) supports the automatic emulation of network service placements calculated by arbitrary placement algorithms. This allows to get hands-on practical experience with deployed services and enables realistic performance measurements.

This prototype belongs to the paper **"A Generic Emulation Framework for Reusing and Evaluating VNF Placement Algorithms"** accepted at IEEE NFV-SDN 2018 by Stefan Schneider, Manuel Peuster, and Holger Karl.

## Cite this work

If you use this placement emulation framework, please cite the following publication:

> Stefan Schneider, Manuel Peuster, and Holger Karl: "A Generic Emulation Framework for Reusing and Evaluating VNF Placement Algorithms", 2018 IEEE Conference on Network Function Virtualization and Software Defined Networks (NFV-SDN), Verona, Italy. (2018)


## Installation

1. Install the emulator [`vim-emu`](https://osm.etsi.org/gitweb/?p=osm/vim-emu.git) (see [README.md "Bare-metal installation"](https://osm.etsi.org/gitweb/?p=osm/vim-emu.git;a=blob;f=README.md;h=ba22ec342ed5d60bf65770aa154adce8b0fcc141;hb=HEAD))
  * `cd vim-emu; sudo python setup.py develop`
2. Pre-build VNF containers: `cd inputs/vnfs; ./build.sh`
3. Install the B-JointSP placement algorithm [`bjointsp 2.3+`](https://github.com/CN-UPB/B-JointSP)
4. Install other dependencies of the placement emulation framework: `python setup.py install` (requires Python 3.5+)

We tested the installation on Ubuntu 16.04.



To install the dependencies required for running the Jupyter notebooks, additionally run:

```bash
pip install -r notebook_requirements.txt
```


## Usage

**Quickstart:**

To start the emulator, calculate the placement, emulate it, measure and log delays, and stop the emulator with one command, use:

```
./place-emu.sh -a algorithm -n network -t service -s sources -c num_pings
```

Where `algorithm` is a placement algorithm, e.g., `bjointsp`, `random`, or `greedy`. Inputs `network`, `service`, and `sources` are paths to input parameters, e.g., from the `inputs`. `num_pings` is the number of packets sent by each delay measurement, e.g., 5 for testing and 100 for evaluation.
If you just want to test placement-emulation with predefined parameters, simply run `test.sh`.


**Separate steps:**

If you prefer to run the steps yourself, you can follow these manual steps:

1. Select inputs from `inputs`
2. Start a network topology on `vim-emu`, e.g., `sudo python place_emu/emulator/topology_zoo.py -g inputs/networks/Abilene.graphml`
3. Start the placement and emulation with `python3 place_emu/placement_emulator.py -a bjointsp --network inputs/networks/Abilene.graphml --service inputs/services/fw1chain.yaml --sources inputs/sources/source0.yaml`.
4. You can test the deployment and connectivity as described [in the wiki](https://github.com/CN-UPB/placement-emulation/wiki/emulation), e.g., with `vim-emu compute list`. Delay measurements can be performed with `ping` or `httping` from inside `vim-emu`.
5. Important: Stop the emulator using `exit` inside the ContainerNet terminal. This is necessary to clean up, so that the emulator can be started again.

*Note*:
The `-a` argument sets the placement algorithm: Currently, we support `bjointsp`, `random`, and `greedy`.
If you only want to trigger placement without emulation, use the `--placeOnly` option when calling `placement_emulator.py`.


**Experiments:**

Use scripts like `runAll.sh` to run a large number of placement emulations sequentially. *Important:* use `|& tee some_log.log` to log the display output for debugging.

## Contact

Lead developers: Stefan Schneider and Manuel Peuster

For questions or support, please use [GitHub's issue system](https://github.com/CN-UPB/placement-emulation/issues). Please also consider the additional information on the [wiki pages](https://github.com/CN-UPB/placement-emulation/wiki).
