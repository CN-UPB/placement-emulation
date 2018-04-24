#!/bin/bash

# return filename without path or extension
function filename {
	filename=$(basename "$1")
	extension="${filename##*.}"
	filename="${filename%.*}"
	echo $filename
}


# run placement, emulation, and measurements sequentially
printf "Expected arguments: -a algorithm -n network -t service -s sources -c num_pings\n"

# get arguments as -a, -n, -t, -s, -c
while getopts a:n:t:s:c: option 
do
	case "${option}" 
	in
		a) ALG=${OPTARG};;
		n) NETWORK=${OPTARG};;
		t) SERVICE=${OPTARG};;
		s) SOURCES=${OPTARG};;
		c) NUM_PINGS=${OPTARG};;
	esac
done


# other constants, individual log file
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
network_name=$(filename $NETWORK)
service_name=$(filename $SERVICE)
sources_name=$(filename $SOURCES)
LOG="results/$ALG/emulation/$network_name-$service_name-$sources_name-$TIMESTAMP.log"
mkdir -p results/$ALG/emulation


# start vim-emu with the specified network
printf "\n\nStarting the emulator\n"
sudo python place_emu/emulator/topology_zoo.py -g $NETWORK &

# wait for the emulator to start (depends on network size)
echo "Start"
NETWORKSIZE="$(python3 place_emu/util/network_size.py -n $NETWORK)"
sleep $NETWORKSIZE

# start the placement emulation
printf "\n\nStarting the placement emulation\n"
python3 place_emu/placement/placement_emulator.py -a $ALG --network $NETWORK --service $SERVICE --sources $SOURCES

# start measurement: 1. generate individual measurement script, 2. run & log it
printf "\n\nStarting the measurement (logging to $LOG)\n"
MEASUREMENT="$(python3 place_emu/util/measure_gen.py -t $SERVICE -c $NUM_PINGS)"
eval "${MEASUREMENT}" |& tee -a $LOG

# append info to log: timestamp, network, service, sources
printf "\nInfo\n" >> $LOG
echo "timestamp: $TIMESTAMP" >> $LOG
echo "algorithm: $ALG" >> $LOG
echo "network: $NETWORK" >> $LOG
echo "service: $SERVICE" >> $LOG
echo "sources: $SOURCES" >> $LOG

# convert log to structured yaml file
python3 place_emu/util/log_parser.py -f $LOG
rm $LOG

# stop: find the pids and stop the process (will automatically clean up)
pgrep -f "python place_emu" | sudo xargs kill
sleep $(($NETWORKSIZE/2))
echo "Placement-emulation completed!"

