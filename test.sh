#!/bin/bash

# run placement and emulation sequentially with example inputs

# return filename without path or extension
function filename {
	filename=$(basename "$1")
	extension="${filename##*.}"
	filename="${filename%.*}"
	echo $filename
}


# constants
NETWORK=inputs/networks/Abilene.graphml
SERVICE=inputs/services/fw1chain.yaml
SOURCES=inputs/sources/source0.yaml
NUM_PINGS=3

# individual log file
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
network_name=$(filename $NETWORK)
service_name=$(filename $SERVICE)
sources_name=$(filename $SOURCES)
LOG="results/measurements/$network_name-$service_name-$sources_name-$TIMESTAMP.log"


# start vim-emu with the specified network
printf "\n\nStarting the emulator\n"
sudo python emulator/topology_zoo.py -g $NETWORK &
sleep 10

# start the placement emulation
printf "\n\nStarting the placement emulation\n"
python3 placement/placement_emulator.py -n $NETWORK -t $SERVICE -s $SOURCES

# start measurement: 1. generate individual measurement script, 2. run & log it
printf "\n\nStarting the measurement (logging to $LOG)\n"
MEASUREMENT="$(python3 util/measure_gen.py -t $SERVICE -c $NUM_PINGS)"
eval "${MEASUREMENT}" |& tee -a $LOG

# append info to log: timestamp, network, service, sources
printf "\nInfo\n" >> $LOG
echo "timestamp: $TIMESTAMP" >> $LOG
echo "network: $NETWORK" >> $LOG
echo "service: $SERVICE" >> $LOG
echo "sources: $SOURCES" >> $LOG

# stop: find the pids and stop the process (will automatically clean up)
pgrep -f "python emu" | sudo xargs kill
sleep 5
echo "Placement-emulation completed!"

