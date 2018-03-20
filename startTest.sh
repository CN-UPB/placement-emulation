#!/bin/bash

# run placement and emulation sequentially with example inputs

# constants
NETWORK=topologies/Abilene.graphml
SERVICE=placement/example-input/fw1chain.yaml
SOURCES=placement/example-input/source0.yaml
MEASUREMENT=/measurement/measure_1fw.sh
NUM_PINGS=5
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# start vim-emu with the specified network
printf "\n\nStarting the emulator\n"
sudo python emulator/topology_zoo.py -g $NETWORK &
sleep 10

# start the placement emulation
printf "\n\nStarting the placement emulation\n"
python3 placement/placement_emulator.py -n $NETWORK -t $SERVICE -s $SOURCES

# start measurement: 1. generate individual measurement script, 2. run & log it
printf "\n\nStarting the measurement (logging to results/$TIMESTAMP.log)\n"
MEASUREMENT="$(python3 util/measure_gen.py -t $SERVICE -c $NUM_PINGS)"
eval "${MEASUREMENT}" |& tee -a "results/$TIMESTAMP.log"

# TODO: append input info to log (network, service, sources)

