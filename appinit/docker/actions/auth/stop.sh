#!/bin/bash -x
CHECK=$(ps aux gunicorn | tail -n +2 | awk '{ print $1 }')

if [ "$CHECK" == "" ]; then
  echo "Already killed 'auth'."
else
  echo "Stopping 'auth'."
  kill -s TERM $CHECK
fi
