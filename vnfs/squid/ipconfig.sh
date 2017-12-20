#!/bin/bash

sleep 1

# IP setup (we need to try different names in different scenarios, but never eth0 which is the docker if)
declare -a PORTS=("prox-net-0" "proxy0-0" "proxy0-1" "proxy-eth0" "squid-vnf-0" "vnf-data")

for p in "${PORTS[@]}"
do
    ifconfig $p down
    ifconfig $p 20.0.0.3 netmask 255.255.255.0
    ifconfig $p up
done

#ifconfig eth0 down
#ifconfig eth0 172.17.0.99 netmask 255.255.255.0
#ifconfig eth0 up

ifconfig > /ifconfig.debug
