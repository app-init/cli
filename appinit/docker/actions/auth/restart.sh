#!/bin/bash -x
# if [ -e "/home/container/flask.pid" ]; then
# sh /home/container/actions/stop.sh
# sh /home/container/actions/start.sh
CHECK=$(ps aux | grep '[g]unicorn' | awk '{ print $2 }')

if [ "$CHECK" == "" ]; then
  echo "Already killed 'auth'."
else
  kill -HUP $CHECK
fi
