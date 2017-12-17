#!/bin/sh
PORT=/dev/ttyACM0
stty -F $PORT 115200 raw -echo
./sekvensseri.py $PORT
reset
