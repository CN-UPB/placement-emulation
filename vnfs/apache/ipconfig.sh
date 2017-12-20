#!/bin/bash

sleep 1

# IP setup (we need to try different names in different scenarios, but never eth0 which is the docker if)
declare -a PORTS=("http-net-0" "http0-0" "http0-1" "http-eth0" "apache.1-eth0" "vnf-data")

for p in "${PORTS[@]}"
do
    ifconfig $p down
    ifconfig $p 20.0.0.1 netmask 255.255.255.0
    ifconfig $p up
done

ifconfig > /ifconfig.debug
