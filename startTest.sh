#!/bin/bash

# run placement and emulation sequentially with example inputs
NETWORK=topologies/Abilene.graphml
SERVICE=placement/example-input/fw1chain.yaml
SOURCES=placement/example-input/source0.yaml

# start vim-emu with the specified network
printf "\n\nStarting the emulator\n"
sudo python emulator/topology_zoo.py -g $NETWORK &
sleep 10

# start the placement emulation
printf "\n\nStarting the placement emulation\n"
python3 placement/placement_emulator.py -n $NETWORK -t $SERVICE -s $SOURCES

