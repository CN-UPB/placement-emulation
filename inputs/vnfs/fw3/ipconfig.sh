#!/bin/bash

sleep 1

# IP setup (we need to try different names in different scenarios, but never eth0 which is the docker if)
declare -a PORTS=("l4fw-net-0" "l4fw0-0" "l4fw0-1" "l4fw-eth0" "socat.1-eth0" "vnf-data")

for p in "${PORTS[@]}"
do
    ifconfig $p down
    ifconfig $p 20.0.0.2 netmask 255.255.255.0
    ifconfig $p up
done

ifconfig > /ifconfig.debug
