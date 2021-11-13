from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from utils import *
import multiprocessing


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)

        # Enable ip forwarding on the router so that packet at one interface is forwarded 
        # to the appropriate interface on the same router
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class Config:
    
    intf_ip = None
    host_ip = None
    route_config = None

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

        # next-hop and src-interface should be on same network for ip-route to work
        # you don't have to add routes between interfaces of the same router

        Config.route_config = [

            {
                'node':'h1', 
                'dst-network':'default', 
                'next-hop-ip':Config.intf_ip['r1-eth0'], 
                'src-exit-interface':'h1-eth0',
            },
            {
                'node':'h2', 
                'dst-network':'default', 
                'next-hop-ip':Config.intf_ip['r4-eth0'], 
                'src-exit-interface':'h2-eth0',
            },

            {
                'node':'r1', 
                'dst-network':'66.0.0.0/8', 
                'next-hop-ip':Config.intf_ip['r3-eth0'], 
                'src-exit-interface':'r1-eth2'
            },
            {
                'node':'r1', 
                'dst-network':'default', 
                'next-hop-ip':Config.intf_ip['r2-eth0'], 
                'src-exit-interface':'r1-eth1'
            },

            {
                'node':'r2', 
                'dst-network':'62.0.0.0/8', 
                'next-hop-ip':Config.intf_ip['r1-eth1'], 
                'src-exit-interface':'r2-eth0'
            },
            {
                'node':'r2', 
                'dst-network':'67.0.0.0/8', 
                'next-hop-ip':Config.intf_ip['r1-eth1'], 
                'src-exit-interface':'r2-eth0'
            },
            {
                'node':'r2', 
                'dst-network':'default', 
                'next-hop-ip':Config.intf_ip['r4-eth1'], 
                'src-exit-interface':'r2-eth1'
            },

            {
                'node':'r3', 
                'dst-network':'62.0.0.0/8', 
                'next-hop-ip':Config.intf_ip['r1-eth2'], 
                'src-exit-interface':'r3-eth0'
            },
            {
                'node':'r3', 
                'dst-network':'63.0.0.0/8', 
                'next-hop-ip':Config.intf_ip['r1-eth2'], 
                'src-exit-interface':'r3-eth0'
            },
            {
                'node':'r3', 
                'dst-network':'default', 
                'next-hop-ip':Config.intf_ip['r4-eth2'], 
                'src-exit-interface':'r3-eth1'
            },
            
            {
                'node':'r4', 
                'dst-network':'67.0.0.0/8', 
                'next-hop-ip':Config.intf_ip['r3-eth1'], 
                'src-exit-interface':'r4-eth2'
            },
            {
                'node':'r4', 
                'dst-network':'default', 
                'next-hop-ip':Config.intf_ip['r2-eth1'], 
                'src-exit-interface':'r4-eth1'
            },
        ]


class NetworkTopo(Topo):

    def build(self):

        # Add 4 routers in two different subnets
        r1 = self.addHost('r1', cls=LinuxRouter, ip=None)
        r2 = self.addHost('r2', cls=LinuxRouter, ip=None)
        r3 = self.addHost('r3', cls=LinuxRouter, ip=None)
        r4 = self.addHost('r4', cls=LinuxRouter, ip=None)

        # Add hosts
        h1 = self.addHost('h1', intfName="h1-eth0", ip=Config.host_ip['h1'])
        h2 = self.addHost('h2', intfName="h2-eth0", ip=Config.host_ip['h2'])

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


def run_server(net, buffer_size):
    info( net['h2'].cmd('iperf -s -p 8000 -i1 | tee server_iperf_'+buffer_size+'.txt') )
    

def run_client(net, buffer_size):
    info( net['h1'].cmd('iperf -c 65.0.0.2 -p 8000 -i1 -t10 | tee client_iperf_'+buffer_size+'.txt' ) )


def log_performance(net, buffer_size):
    info( net['r1'].cmd('tc qdisc add dev r1-eth0 root netem limit ' + buffer_size+ ' delay 30ms') )
    info( net['r1'].cmd('tc qdisc add dev r1-eth1 root netem limit ' + buffer_size+ ' delay 30ms') )
    info( net['r1'].cmd('tc qdisc add dev r1-eth2 root netem limit ' + buffer_size+ ' delay 30ms') )

    info( net['r2'].cmd('tc qdisc add dev r2-eth0 root netem limit ' + buffer_size+ ' delay 30ms') )
    info( net['r2'].cmd('tc qdisc add dev r2-eth1 root netem limit ' + buffer_size+ ' delay 30ms') )

    info( net['r3'].cmd('tc qdisc add dev r3-eth0 root netem limit ' + buffer_size+ ' delay 30ms') )
    info( net['r3'].cmd('tc qdisc add dev r3-eth1 root netem limit ' + buffer_size+ ' delay 30ms') )

    info( net['r4'].cmd('tc qdisc add dev r4-eth0 root netem limit ' + buffer_size+ ' delay 30ms') )
    info( net['r4'].cmd('tc qdisc add dev r4-eth1 root netem limit ' + buffer_size+ ' delay 30ms') )
    info( net['r4'].cmd('tc qdisc add dev r4-eth2 root netem limit ' + buffer_size+ ' delay 30ms') )    

    server = multiprocessing.Process(target=run_server, args=(net, buffer_size))
    server.start()
    client = multiprocessing.Process(target=run_client, args=(net, buffer_size))
    client.start()
    server.join()
    client.join()
    

def run():
    Config.setup()
    topo = NetworkTopo()
    net = Mininet(topo=topo)

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

    # Add routing for reaching networks that aren't directly connected

    for config in Config.route_config:
        src_interface = config['src-exit-interface']
        router = config['node']
        dst_host = config['dst-network']
        next_hop_interface = config['next-hop-ip']
        cmd = "ip route add "+dst_host+" via "+next_hop_interface.split("/")[0]+" dev "+src_interface.split("/")[0]
        info(net[router].cmd(cmd))

    buffer_sizes = ['10240', '5242880', '26214400']
    net.start()
    log_performance(net, buffer_size=buffer_sizes[2])
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()