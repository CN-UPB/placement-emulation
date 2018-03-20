FROM ubuntu:xenial
MAINTAINER manuel.peuster@uni-paderborn.de

# configure layer 4 forwarding
ENV FW_IN_PORT 80
ENV FW_OUT_ADDR 77.0.0.2
ENV FW_OUT_PORT 80

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y -q \
	net-tools \
	iproute \
	inetutils-ping \
	iptables \
	arptables \
	ebtables \
	bridge-utils \
	ethtool \
	bmon \
	vim \
    curl \
	socat

ADD start.sh start.sh
RUN chmod +x start.sh
ADD ipconfig.sh ipconfig.sh
RUN chmod +x ipconfig.sh

WORKDIR /

EXPOSE 80

# entry point
ENV SON_EMU_CMD ./start.sh
CMD /bin/bash
