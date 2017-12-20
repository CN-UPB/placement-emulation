FROM ubuntu:xenial
MAINTAINER manuel.peuster@uni-paderborn.de

# define interface names (should be the same as in VNFD)
ENV IFOUT output

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y -q \
	net-tools \
	iproute \
	inetutils-ping \
	curl \
        wget \
        hping3 \
        httping

ADD start.sh start.sh
RUN chmod +x start.sh

WORKDIR /

# entry point
ENV SON_EMU_CMD ./start.sh
CMD /bin/bash

