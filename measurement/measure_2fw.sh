#!/bin/sh

echo "Latency between VNFs (ping)"
echo "User -> L4FW 2"
sudo docker exec -it mn.vnf_user ping -c5 -q 77.0.0.2
echo "\nL4FW 2 -> L4FW 1"
sudo docker exec -it mn.vnf_fw2 ping -c5 -q 88.0.0.2
echo "\nL4FW 1 -> Web"
sudo docker exec -it mn.vnf_fw1 ping -c5 -q 99.0.0.2

echo "\nLatency of whole chain"
sudo docker exec -it mn.vnf_user httping --url http://77.0.0.2 -p 80 -c 5
