#!/bin/bash
pip3 install virtualenv
virtualenv -p python3 /home/container/virtv

source /home/container/virtv/bin/activate
pip3 install -r /home/container/platform-requirements.txt