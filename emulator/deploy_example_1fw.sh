#!/bin/bash
# example with 1 L4FW (and no proxy)

# deploy VNFs
vim-emu compute start -n vnf_user -i placement-user-img --net '(id=output,ip=88.0.0.1/24)' -d pop0
vim-emu compute start -n vnf_fw1 -i placement-fw1-img --net '(id=input,ip=88.0.0.2/24),(id=output,ip=99.0.0.1/24)' -d pop2
vim-emu compute start -n vnf_web -i placement-apache-img --net '(id=input,ip=99.0.0.2/24)' -d pop9
sleep 3
# setup network forwarding rules
vim-emu network add -src vnf_user:output -dst vnf_fw1:input
vim-emu network add -src vnf_fw1:output -dst vnf_web:input
sleep 2
vim-emu compute list
