#!/usr/bin/env bash

if [ $1 = "2" ]; then
    echo "run python-nxswriter"
    docker exec -it ndts python test
else
    echo "run python3-nxswriter"
    docker exec -it ndts python3 test
fi
if [ $? -ne "0" ]
then
    exit -1
fi
