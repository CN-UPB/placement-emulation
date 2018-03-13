#!/bin/bash

# run placement and emulation sequentially
printf "Expected arguments: -n network -t service -s sources\n"

# get arguments as -n, -t, -s
while getopts n:t:s: option 
do
	case "${option}" 
	in
		n) NETWORK=${OPTARG};;
		t) SERVICE=${OPTARG};;
		s) SOURCES=${OPTARG};;
	esac
done

# start vim-emu with the specified network
printf "\n\nStarting the emulator\n"
sudo python emulator/topology_zoo.py -g $NETWORK &
sleep 10

# start the placement emulation
printf "\n\nStarting the placement emulation\n"
python3 placement/placement_emulator.py -n $NETWORK -t $SERVICE -s $SOURCES

