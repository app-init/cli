#!/bin/bash -x
if [ -e "/run/nginx.pid" ]; then
  sh /home/container/actions/stop.sh
  sh /home/container/actions/start.sh
else
  sh /home/container/actions/start.sh
fi
