#!/bin/bash -x
gunicorn appinit_backend.app:app -c /home/container/config/gunicorn.py
# if [ ! -e "/home/container/flask.pid" ]; then
#   cd /home/cee-tools/api/application/
#   echo "Starting 'auth' service"

# else
#   echo "Already running 'auth' service"
# fi
