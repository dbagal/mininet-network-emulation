from mininet.node import Node
from mininet.log import setLogLevel, info
from contextlib import contextmanager
import os

setLogLevel('info')

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)

        # Enable ip forwarding on the router so that packet at one interface is forwarded 
        # to the appropriate interface on the same router
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class BirdRouter(Node):

    @contextmanager
    def in_router_dir(self): 
        path = os.getcwd()
        self.cmd('cd ../bird-conf/%s' % self.name)
        yield
        self.cmd('cd %s' % path)


    def config(self, **params):
        super(BirdRouter, self).config(**params)
        
        self.cmd('sysctl net.ipv4.ip_forward=1')
        with self.in_router_dir():
            info(self.cmd('sudo bird -l'))
        

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        with self.in_router_dir():
            self.cmd('sudo birdc -l down')

        super(BirdRouter, self).terminate()


class BirdHost(Node):

    @contextmanager
    def in_host_dir(self):
        path = os.getcwd()
        self.cmd('cd ../bird-conf/%s' % self.name)
        yield
        self.cmd('cd %s' % path)


    def config(self, **params):
        super(BirdHost, self).config(**params)
        
        with self.in_host_dir():
            info(self.cmd('sudo bird -l'))


    def terminate(self):
        with self.in_host_dir():
            info(self.cmd('sudo birdc -l down'))

        super(BirdHost, self).terminate()


def get_network_addr(cidr):
    ip, subnet = cidr.split("/")
    subnet = int(subnet)
    subnet_mask_bits= [1,]*subnet + [0,]*(32-subnet)
    ip_bin = [format(int(quad), "b") for quad in ip.split(".")]
    ip_bin = [list('0'*(8-len(x))+x) for x in ip_bin]
    ip_bits = []
    for quad in ip_bin:
        ip_bits+= [int(bit) for bit in quad]

    nw_addr_bits = [x*y for x,y in zip(ip_bits, subnet_mask_bits )]
    nw_addr = []
    for i in range(0,32,8):
        nw_addr += [str(int("".join(str(i) for i in nw_addr_bits[i:i+8]), 2))]
    
    return ".".join(nw_addr)+"/"+str(subnet)



    
    

