#!/bin/bash
# example with 2 bridges

# deploy VNFs
vim-emu compute start -n vnf_user -i placement-user-img --net '(id=output,ip=88.0.0.1/24)' -d pop0
vim-emu compute start -n vnf_bridge2 -i placement-bridge-img --net '(id=input,ip=88.0.0.2/24),(id=output,ip=88.0.0.3/24)' -d pop2
vim-emu compute start -n vnf_bridge1 -i placement-bridge-img --net '(id=input,ip=88.0.0.4/24),(id=output,ip=88.0.0.5/24)' -d pop9
vim-emu compute start -n vnf_web -i placement-apache-img --net '(id=input,ip=88.0.0.6/24)' -d pop8
sleep 3
# setup network forwarding rules
vim-emu network add -src vnf_user:output -dst vnf_bridge2:input
vim-emu network add -src vnf_bridge2:output -dst vnf_bridge1:input
vim-emu network add -src vnf_bridge1:output -dst vnf_web:input
sleep 2
vim-emu compute list
