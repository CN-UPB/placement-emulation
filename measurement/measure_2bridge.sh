#!/bin/sh

echo "Latency from bridges (ping)"
echo "\nBridge 2 -> Web"
sudo docker exec -it mn.vnf_bridge2 ping -c5 -q 88.0.0.6
echo "\nBridge 1 -> Web"
sudo docker exec -it mn.vnf_bridge1 ping -c5 -q 88.0.0.6

echo "\nLatency of whole chain"
echo "With ping"
sudo docker exec -it mn.vnf_user ping -c5 -q 88.0.0.6
echo "With httping"
sudo docker exec -it mn.vnf_user httping --url http://88.0.0.6 -p 80 -c 5
