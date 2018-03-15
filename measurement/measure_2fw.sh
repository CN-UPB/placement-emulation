#!/bin/sh

# format is important (do not change)! it's parsed automatically later

echo "Latency between VNFs (ping)"
echo "vnf_user -> vnf_fw2"
sudo docker exec -it mn.vnf_user ping -c10 -q 77.0.0.2
echo "\nLatency between VNFs (ping)"
echo "vnf_fw2 -> vnf_fw1"
sudo docker exec -it mn.vnf_fw2 ping -c10 -q 88.0.0.2
echo "\nLatency between VNFs (ping)"
echo "vnf_fw1 -> vnf_web"
sudo docker exec -it mn.vnf_fw1 ping -c10 -q 99.0.0.2

echo "\nLatency of whole chain"
sudo docker exec -it mn.vnf_user httping --url http://77.0.0.2 -p 80 -c 10
