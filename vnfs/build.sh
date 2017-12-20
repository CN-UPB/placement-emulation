#!/bin/bash
# automatically build VNF containers
set -e
docker build -t placement-apache-img -f apache/Dockerfile apache
docker build -t placement-socat-img -f socat/Dockerfile socat
docker build -t placement-squid-img -f squid/Dockerfile squid
docker build -t placement-user-img -f user/Dockerfile user
