import os, sys, time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from utils import *


class Config:
    
    intf_ip = None
    host_ip = None

    @staticmethod
    def setup():
        Config.intf_ip = {
            'r1-eth0': '62.0.0.1/8',
            'r1-eth1': '63.0.0.1/8',
            'r1-eth2': '67.0.0.1/8',
            'r2-eth0': '63.0.0.2/8',
            'r2-eth1': '64.0.0.1/8',
            'r3-eth0': '67.0.0.2/8',
            'r3-eth1': '66.0.0.1/8',
            'r4-eth0': '65.0.0.1/8',
            'r4-eth1': '64.0.0.2/8',
            'r4-eth2': '66.0.0.2/8',
        }

        Config.host_ip = {
            'h1': '62.0.0.2/8',
            'h2': '65.0.0.2/8'
        }


class NetworkTopo(Topo):

    def build(self):

        # Add 4 routers in two different subnets
        r1 = self.addHost('r1', cls=BirdRouter, ip=None)
        r2 = self.addHost('r2', cls=BirdRouter, ip=None)
        r3 = self.addHost('r3', cls=BirdRouter, ip=None)
        r4 = self.addHost('r4', cls=BirdRouter, ip=None)

        # Add hosts
        h1 = self.addHost('h1', cls=BirdHost, intfName="h1-eth0", ip=Config.host_ip['h1'])
        h2 = self.addHost('h2', cls=BirdHost, intfName="h2-eth0", ip=Config.host_ip['h2'])

        # linking hosts to the routers
        self.addLink(h1, r1, intfName2="r1-eth0", params2={'ip':Config.intf_ip['r1-eth0']})
        self.addLink(h2, r4, intfName2="r4-eth0", params2={'ip':Config.intf_ip['r4-eth0']})

        # linking routers amongst themselves
        self.addLink(r1,r2, 
                    intfName1="r1-eth1", 
                    intfName2="r2-eth0", 
                    params1={'ip':Config.intf_ip['r1-eth1']}, 
                    params2={'ip':Config.intf_ip['r2-eth0']})

        self.addLink(r1,r3, 
                    intfName1="r1-eth2", 
                    intfName2="r3-eth0", 
                    params1={'ip':Config.intf_ip['r1-eth2']}, 
                    params2={'ip':Config.intf_ip['r3-eth0']})

        self.addLink(r2,r4, 
                    intfName1="r2-eth1", 
                    intfName2="r4-eth1", 
                    params1={'ip':Config.intf_ip['r2-eth1']}, 
                    params2={'ip':Config.intf_ip['r4-eth1']})

        self.addLink(r3,r4, 
                    intfName1="r3-eth1", 
                    intfName2="r4-eth2", 
                    params1={'ip':Config.intf_ip['r3-eth1']}, 
                    params2={'ip':Config.intf_ip['r4-eth2']})


def run():
    Config.setup()

    path = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(path, "logs")
    if not os.path.exists(log_path): os.makedirs(log_path)

    # change directory to PartB to run the code
    os.chdir(path)

    topo = NetworkTopo()
    net = Mininet(topo=topo, controller=None)

    """ 
    NETWORK TOPOLOGY             
                            (0) [R2] (1)
                           /            \
                        (1)              (1)
    [H1] (0) -- (0) [R1]                    [R3] (0) -- (0) H2
                        (2)              (2)
                           \            /
                            (0) [R3] (1)
    """
    net.start()
    
    # log routing tables
    info(net['r1'].cmd('route -n | tee ' +log_path+ '/r1-routing-table.txt'))
    info(net['r2'].cmd('route -n | tee ' +log_path+ '/r2-routing-table.txt'))
    info(net['r3'].cmd('route -n | tee ' +log_path+ '/r3-routing-table.txt'))
    info(net['r4'].cmd('route -n | tee ' +log_path+ '/r4-routing-table.txt'))
    
    # wait for some time till BIRD sets up all the routes
    time.sleep(10)

    # log traceroute from h1 to h2 
    # note: since route -n is used, there is no dns resolution happening when displaying the routing tables. 
    # hence traceroute is not able to identify h2. 
    # hence use h2's ip address instead of its name 'h2'
    info(net['h1'].cmd('traceroute -m 5 ' + Config.host_ip['h2'].split("/")[0] +' | tee ' +log_path+ '/traceroute-h1-h2-1.txt'))
    
    # take r1-r2 link down 
    info(net.configLinkStatus('r1','r2','down'))
    
    # wait for some time till BIRD sets up new routes after the link is taken down
    time.sleep(5)
    info(net['h1'].cmd('traceroute -m 5 ' + Config.host_ip['h2'].split("/")[0] +' | tee ' +log_path+ '/traceroute-h1-h2-2.txt'))

    # use this only in case of shared folder
    # copy all log files from vm folder where the code is run to the shared folder
    os.system("cp -r ./logs/* /media/sf_mininet-network-emulation/PartB/logs/")

    #CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()