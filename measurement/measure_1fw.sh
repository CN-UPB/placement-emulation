#!/bin/sh

echo "Latency between VNFs (ping)"
# why is this ping so high (~100ms) on the same pop?
echo "User -> L4FW 1"
sudo docker exec -it mn.vnf_user ping -c5 -q 88.0.0.2
echo "\nL4FW 1 -> Web"
sudo docker exec -it mn.vnf_fw1 ping -c5 -q 99.0.0.2

echo "\nLatency of whole chain"
sudo docker exec -it mn.vnf_user httping --url http://88.0.0.2 -p 80 -c 5
