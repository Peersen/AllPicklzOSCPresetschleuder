#!/usr/bin/env bash

cd ~/
./keepalive.sh "python ./picklz.py --port=7676 --num-leds=139" > /dev/null &
