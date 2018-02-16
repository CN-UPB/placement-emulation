#!/bin/sh

# bridge has no IP address => can't ping to bridge but only through bridge directly to the web server

echo "Latency from bridge (ping)"
echo "\nBridge 1 -> Web"
sudo docker exec -it mn.vnf_bridge1 ping -c10 -q 88.0.0.4

echo "\nLatency of whole chain"
echo "With ping"
sudo docker exec -it mn.vnf_user ping -c10 -q 88.0.0.4
echo "With httping"
sudo docker exec -it mn.vnf_user httping --url http://88.0.0.4 -p 80 -c 10
