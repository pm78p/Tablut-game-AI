#!/bin/bash

if [[ $# -ne 3 ]]; then
   echo "Need all arguments"
   echo "white or black as first parameter"
   echo "timeout as second parameter"
   echo "server ip as third parameter"
   echo "Example: $0 white 60 192.168.111.129"
   exit 1
fi

COLOR=$1
TIMEOUT=$2
SERVER_IP=$3

python3 /home/tablut/tablut/myTablut/main_client.py $COLOR $TIMEOUT $SERVER_IP
