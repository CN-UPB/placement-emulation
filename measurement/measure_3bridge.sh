#!/bin/sh

echo "\nLatency of whole chain"
echo "With ping"
sudo docker exec -it mn.vnf_user ping -c10 -q 88.0.0.8
echo "With httping"
sudo docker exec -it mn.vnf_user httping --url http://88.0.0.8 -p 80 -c 10
