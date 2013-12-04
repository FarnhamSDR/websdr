#!/bin/bash
sudo killall -9 rtl_tcp
sudo screen -dmS rtl1 rtl_tcp -d 0 -f 145000000 -s 2048000 -a 127.0.0.1 -p 5901
sudo screen -dmS rtl2 rtl_tcp -d 1 -f 445500000 -s 2048000 -a 127.0.0.1 -p 5902
