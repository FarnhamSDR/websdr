#!/bin/bash
sudo killall -9 rtl_tcp
sudo screen -dmS rtl23 rtl_tcp -d 0 -f 1296600000 -s 2048000 -a 127.0.0.1 -p 5901
sleep 1;
sudo screen -dmS rtl432 rtl_tcp -d 1 -f 434000000 -s 2048000 -a 127.0.0.1 -p 5902
##sleep 1;
##sudo screen -dmS rtl144 rtl_tcp -d 2 -f 145000000 -s 2048000 -a 127.0.0.1 -p 5903
