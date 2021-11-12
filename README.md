
# Login
**username:** mininet

**password:** mininet

# Adding a shared folder
Add a shared folder (mininet-network-emulation) from the settings

# Commands to setup the shared folder
```
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
cd /media/sf_mininet-network-emulation
``` 
