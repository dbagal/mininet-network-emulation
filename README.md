
# Login
**username:** mininet

**password:** mininet

# Adding a shared folder
Add a shared folder (mininet-network-emulation) from the settings

# Commands to setup the shared folder
```
sudo apt-get upgrade
sudo apt-get virtualbox-guest-X11
sudo apt-get virtualbox-guest-utils
sudo apt-get virtualbox-guest-dkms
sudo usermod -aG vboxsf mininet
sudo chown -R mininet:users /media/
```

# Locate the folder

Switch to the super user first in order to run all the python files.
```
sudo su
cd /
cd /media/sf_mininet-network-emulation
``` 

# Installing bird

Install directly with apt-get instead of the repository as it leads to errors sometimes.
The version of bird installed by apt-get will be 1.5.0 however. Latest version 2.0.8 is unavailable via apt-get.
```
sudo apt-get install bird
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

Enable and restart bird
```
systemctl enable bird
systemctl restart bird
```

# Installin Iperf

```
sudo apt-get install iperf
```
# Testing bandwidth

```
iperf h1 h2
```

```
sudo apt-get install flex
sudo apt-get install bison
```