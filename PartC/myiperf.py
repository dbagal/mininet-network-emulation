import os, sys, time
import multiprocessing
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
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
        self.addLink(h1, r1, 
                    cls=TCLink, bw=100, delay="30ms",
                    intfName2="r1-eth0", params2={'ip':Config.intf_ip['r1-eth0']})

        self.addLink(h2, r4, 
                    cls=TCLink, bw=100, delay="30ms",
                    intfName2="r4-eth0", params2={'ip':Config.intf_ip['r4-eth0']})

        # linking routers amongst themselves
        self.addLink(r1,r2, 
                    cls=TCLink, bw=100, delay="30ms",
                    intfName1="r1-eth1", 
                    intfName2="r2-eth0", 
                    params1={'ip':Config.intf_ip['r1-eth1']}, 
                    params2={'ip':Config.intf_ip['r2-eth0']})

        self.addLink(r1,r3, 
                    cls=TCLink, bw=100, delay="30ms",
                    intfName1="r1-eth2", 
                    intfName2="r3-eth0", 
                    params1={'ip':Config.intf_ip['r1-eth2']}, 
                    params2={'ip':Config.intf_ip['r3-eth0']})

        self.addLink(r2,r4, 
                    cls=TCLink, bw=100, delay="30ms",
                    intfName1="r2-eth1", 
                    intfName2="r4-eth1", 
                    params1={'ip':Config.intf_ip['r2-eth1']}, 
                    params2={'ip':Config.intf_ip['r4-eth1']})

        self.addLink(r3,r4, 
                    cls=TCLink, bw=100, delay="30ms",
                    intfName1="r3-eth1", 
                    intfName2="r4-eth2", 
                    params1={'ip':Config.intf_ip['r3-eth1']}, 
                    params2={'ip':Config.intf_ip['r4-eth2']})


def run_server(net, buffer_size, path):
    # run server on port 8000
    # handle one client connection and exit (-1)
    info( net['h2'].cmd('iperf3 -s -p 8000 -i1 -1 | tee '+path+'/server_iperf_'+buffer_size+'.txt') )
    

def run_client(net, buffer_size, path):
    # run client and connect to the server on port 8000
    info( net['h1'].cmd('iperf3 -c '+Config.host_ip['h2'].split("/")[0]+' -p 8000 -i1 -t10 | tee '+path+'/client_iperf_'+buffer_size+'.txt' ) )


def log_performance(net, buffer_size, log_path):
    interfaces = list(Config.intf_ip.keys())

    # set buffer size for each of the router interfaces
    for intf in interfaces:
        router = intf.split("-")[0]
        net[router].cmd('tc qdisc add dev %s root netem limit %s'%(intf, buffer_size))    

    # run the iperf server followed by the iperf client
    server = multiprocessing.Process(target=run_server, args=(net, buffer_size, log_path))
    server.start()
    client = multiprocessing.Process(target=run_client, args=(net, buffer_size, log_path))
    client.start()
    server.join()
    client.join()
    

def run():
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

    # initialise the setup, create the topology and create the network from the topology
    Config.setup()

    path = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(path, "logs")
    if not os.path.exists(log_path): os.makedirs(log_path)

    # change directory to PartB to run the code
    os.chdir(path)

    topo = NetworkTopo()
    net = Mininet(topo=topo, controller=None)

    # initialize buffer sizes to 10Kb, 5Mb, 25Mb
    buffer_sizes = ['10240', '5242880', '26214400']
    net.start()
    
    # wait for some time till BIRD sets up all the routes
    time.sleep(10)
    
    # start measuring network performance
    log_performance(net, buffer_sizes[0], log_path)

    # use this only in case of shared folder
    # copy all log files from vm folder where the code is run to the shared folder
    os.system("cp -r ./logs/* /media/sf_mininet-network-emulation/PartC/logs/")

    #CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()