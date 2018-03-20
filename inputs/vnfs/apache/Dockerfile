FROM ubuntu:xenial
MAINTAINER manuel.peuster@uni-paderborn.de

# define interface names (should be the same as in VNFD)
ENV IFIN input

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y -q \
	net-tools \
	iproute \
	inetutils-ping \
	apache2 \
	php7.0 \
	libapache2-mod-php7.0 \
	curl \
        wget \
	lynx-cur

# Enable apache mods.
RUN a2enmod php7.0
RUN a2enmod rewrite

ADD start.sh start.sh
RUN chmod +x start.sh
ADD ipconfig.sh ipconfig.sh
RUN chmod +x ipconfig.sh

ADD www /var/www/site
ADD apache.conf /etc/apache2/sites-enabled/000-default.conf

WORKDIR /

EXPOSE 80

# entry point
ENV SON_EMU_CMD ./start.sh
CMD /bin/bash

# manually test
#docker run --rm -it  --name cattube -p 80:80 http-apache-img /usr/sbin/apache2ctl -D FOREGROUND &

