#!/bin/sh

# format is important (do not change)! it's parsed automatically later

# bridge has no IP address => can't ping to bridge but only through bridge directly to the web server

echo "\nLatency of whole chain (httping)"
echo "With ping"
sudo docker exec -it mn.vnf_user ping -c10 -q 88.0.0.4
echo "With httping"
sudo docker exec -it mn.vnf_user httping --url http://88.0.0.4 -p 80 -c 10
