#!/bin/bash
#./ipconfig.sh > ipconfig.log
/usr/sbin/apache2ctl -D FOREGROUND &
echo "Apache VNF started ..."
