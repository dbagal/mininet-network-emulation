# Mininet Network Emulation

This project implements a network topology using the mininet emulator. 
Routing in the network is done by **BIRD** which is an inter-domain routing daemon.
Finally network performance is measured using **iperf**

**Programming Language:** *Python*

# External libraries used

- *mininet==2.3.0*
- *traceroute==2.0.21*
- *iperf3==3.0.11*
- *BIRD==2.0.8*

# Project structure

- **bird-2.0.8/:** Folder containing files for the BIRD inter-routing unix daemon 
- **bird-conf:** Folder containing configuration folders for every node in the topology
- **folder-setup.sh:** Bash script for migrating the folder to a local folder in the VM
- **install.sh:** Bash script for installing BIRD, traceroute and iperf3
- **PartA/mytopo.py:** Python script for creating a basic network topology and adding static routes
- **PartB/myrip.py:** Python script for running RIP routing protocol with BIRD on the network 
- **PartC/myiperf.py:** Python script for measuring the performance of the network
- **/logs:** Output logs of all the commands run for each part of the assignment 
- **utils.py/:** Python file containing network utilities

# Installation and setup

- Download [Mininet VM](http://mininet.org/download/)

## Login to mininet 

**username:** mininet

**password:** mininet

## Adding a shared folder

- Add a shared folder (named mininet-network-emulation) from the VirtualBox settings for the Guest OS
- Add optical drive (VBoxGuestAdditions.iso) from Settings > Storage (Disk icon besides Controller:SCSI)

## Commands to setup the shared folder inside the VM
```
sudo apt-get upgrade
sudo apt-get install virtualbox-guest-utils
sudo apt-get install virtualbox-guest-dkms
sudo usermod -aG vboxsf mininet
sudo chown -R mininet:users /media/
reboot
```

Copy the shared folder to a local folder inside the VM. This is a requirement for the BIRD service.

```
sudo su
/media/sf_mininet-network-emulation/folder-setup.sh
```

## Installing requirements

```
sudo su
/media/sf_mininet-network-emulation/install.sh
``` 


