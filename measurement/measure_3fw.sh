#!/bin/sh

echo "Latency between VNFs (ping)"
echo "User -> L4FW 3"
sudo docker exec -it mn.vnf_user ping -c10 -q 66.0.0.2
echo "\nL4FW 3 -> L4FW 2"
sudo docker exec -it mn.vnf_fw3 ping -c10 -q 77.0.0.2
echo "\nL4FW 2 -> L4FW 1"
sudo docker exec -it mn.vnf_fw2 ping -c10 -q 88.0.0.2
echo "\nL4FW 1 -> Web"
sudo docker exec -it mn.vnf_fw1 ping -c10 -q 99.0.0.2

echo "\nLatency of whole chain"
sudo docker exec -it mn.vnf_user httping --url http://66.0.0.2 -p 80 -c 10
