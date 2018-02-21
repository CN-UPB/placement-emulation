#!/bin/bash
# automatically build VNF containers
set -e
docker build -t placement-apache-img -f apache/Dockerfile apache
docker build -t placement-socat-img -f socat/Dockerfile socat
docker build -t placement-squid-img -f squid/Dockerfile squid
docker build -t placement-user-img -f user/Dockerfile user
docker build -t placement-fw1-img -f fw1/Dockerfile fw1
docker build -t placement-fw2-img -f fw2/Dockerfile fw2
docker build -t placement-fw3-img -f fw3/Dockerfile fw3
docker build -t placement-bridge-img -f bridge/Dockerfile bridge
