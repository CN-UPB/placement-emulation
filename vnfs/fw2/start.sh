#!/bin/bash
#./ipconfig.sh > ipconfig.log
socat -d -d TCP-LISTEN:$FW_IN_PORT,fork TCP:$FW_OUT_ADDR:$FW_OUT_PORT &
echo "Socat VNF started ..."
