#!/usr/bin/env bash

if [[ -z "$1" ]];then
    echo "ERROR: must specify program"
    exit 1
fi

while (( 0 == 0 ));do
    $@ &
    pid=`jobs -l | awk '{print $2}'`
    wait $pid
done