
# Login
**username:** mininet

**password:** mininet

# Adding a shared folder
Add a shared folder (mininet-network-emulation) from the settings
Add optical drive (VBoxGuestAdditions.iso) from Settings > Storage (Disk icon besides Controller:SCSI)

# Commands to setup the shared folder
```
sudo apt-get upgrade
sudo apt-get install virtualbox-guest-utils
sudo apt-get install virtualbox-guest-dkms
sudo usermod -aG vboxsf mininet
sudo chown -R mininet:users /media/
reboot
```

# Locate the folder

Switch to the super user first in order to run all the python files.
```
sudo su
cd /media/sf_mininet-network-emulation
mkdir /home/net
cp -r /media/sf_mininet-network-emulation/* /home/net
``` 

# Installing traceroute

```
sudo apt-get install traceroute
```

# Installing bird

Install the following dependencies first
```
sudo apt-get install flex
sudo apt-get install bison
sudo apt-get install libncurses-dev
sudo apt-get libreadline-dev
```

Install bird using the following commands then
```
./configure
make
make install
```


# Setting up configuration for RIP

Open the configuration file in edit mode
```
cd /
nano /etc/bird/bird.conf
```

Add the following lines to the configuration file
```
protocol rip {
        import all;
        export all;
        interface "eth*" {
                metric 2;
                port 1520;
                mode multicast;
                update time 12;
                timeout time 60;
                authentication cryptographic;
                password "secret" { algorithm hmac sha256; };
        };
}
```


# Installing Iperf

```
sudo apt-get install iperf
```
# Testing bandwidth

```
iperf h1 h2
```
