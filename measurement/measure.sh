#!/bin/sh

echo "Latency between VNFs (ping)"
echo "User -> Proxy"
sudo docker exec -it mn.vnf_user ping -c10 -q 10.0.0.2
echo "\nProxy -> L4FW"
sudo docker exec -it mn.vnf_proxy ping -c10 -q 20.0.0.2
echo "\nL4FW -> Web"
sudo docker exec -it mn.vnf_l4fw ping -c10 -q 30.0.0.2

echo "\nLatency of whole chain"
sudo docker exec -it mn.vnf_user httping --proxy 10.0.0.2:3128 --url http://20.0.0.2 -p 8899 -c 10
