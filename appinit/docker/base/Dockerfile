FROM docker.io/fedora:latest
LABEL maintainer="Matthew Owens mowens@redhat.com"

WORKDIR /home/root

ADD mongodb-org.repo /etc/yum.repos.d/

RUN yum groupinstall -y "Development Tools"
RUN yum -y install mongodb-org
RUN yum install -y \
   wget \
   tar \
   gcc \
   openssl openssl-devel \
   redhat-rpm-config \
   mod_ssl \
   python-devel \
   mysql mysql-devel \
   xmlsec1 xmlsec1-devel \
   xmlsec1-openssl xmlsec1-openssl-devel \
   libtool-ltdl-devel \
   python-pip \
   mod_wsgi \
   python3-devel \
   npm \
   iputils \
   which \
   nginx \
   procps \
   git \
   openssl \ 
   openssl-devel \
   numactl \
   nodejs

RUN setcap cap_net_raw,cap_net_admin+p /usr/bin/ping

# Flask Setup
# RUN which pip
# RUN pip3 install --upgrade pip
# ADD requirements.txt /home/container/
# RUN pip3 install -r /home/container/requirements.txt

# Mongodb Setup
RUN groupadd -r mongodb && useradd -r -d /home/mongodb/ -g  mongodb mongodb
RUN usermod mongodb -a -G wheel

# Platform Setup
ADD platform-requirements.txt /home/container/
ADD install_python.sh /home/container/
RUN /home/container/install_python.sh

# Set global npm directories
RUN mkdir /home/container/.npm-global
RUN npm config set prefix '/home/container/npm-global'

ENV PATH "${PATH}:/home/container/npm-global/bin:/home/container/appinit/"

# Setup base npm
RUN npm install -g n
RUN n latest
RUN npm install -g yarn
RUN yarn config set prefix /home/container/npm-global
RUN yarn global add @app-init/frontend

# ADD entry.sh /home/container/

VOLUME "/home/container/config/"
VOLUME "/home/container/actions/"
VOLUME "/home/container/data/"
VOLUME "/home/container/service/"
VOLUME "/home/container/appinit/"
VOLUME "/home/container/applications/"

WORKDIR /home/container


# RUN export PYTHONPATH="${PYTHONPATH}:/home/container/webplatform_cli"
# RUN export PATH="${PATH}:/home/container/webplatform_cli:/home/container/npm-global"