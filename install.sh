#!/bin/bash
sudo apt-get upgrade
sudo apt-get install flex bison libncurses-dev libreadline-dev
cd /home/net/bird-2.0.8/
./configure
make
make install
sudo apt-get install traceroute
sudo apt-get install iperf3
