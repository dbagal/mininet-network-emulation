from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter(Node):
    def config(topo, **params):
        super(LinuxRouter, topo).config(**params)

        # Enable forwarding on the router
        topo.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(topo):
        topo.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, topo).terminate()


class Config:
    
    intf_ip = None
    host_ip = None
    route_config = None

    @staticmethod
    def setup():
        Config.intf_ip = {
            'r1-eth0': '10.0.0.1',
            'r1-eth1': '10.0.2.1',
            'r1-eth2': '10.0.3.1',
            'r2-eth0': '10.0.2.2',
            'r2-eth1': '10.0.4.1',
            'r3-eth0': '10.0.3.2',
            'r3-eth1': '10.0.5.1',
            'r4-eth0': '10.0.1.1',
            'r4-eth1': '10.0.5.2',
            'r4-eth2': '10.0.4.2',
        }

        Config.host_ip = {
            'h1': '10.0.0.2',
            'h2': '10.0.1.2'
        }

        Config.route_config = [
            {'router':'r1', 'src': Config.intf_ip['r1-eth0'], 'dst':Config.host_ip['h2'], 'next-hop': Config.intf_ip['r1-eth1']},
            {'router':'r1', 'src': Config.intf_ip['r1-eth1'], 'dst':Config.host_ip['h2'], 'next-hop': Config.intf_ip['r2-eth0']},
            {'router':'r2', 'src': Config.intf_ip['r2-eth0'], 'dst':Config.host_ip['h2'], 'next-hop': Config.intf_ip['r2-eth1']},
            {'router':'r2', 'src': Config.intf_ip['r2-eth1'], 'dst':Config.host_ip['h2'], 'next-hop': Config.intf_ip['r4-eth1']},
            {'router':'r4', 'src': Config.intf_ip['r4-eth1'], 'dst':Config.host_ip['h2'], 'next-hop': Config.intf_ip['r4-eth0']},

            {'router':'r4', 'src': Config.intf_ip['r4-eth0'], 'dst':Config.host_ip['h1'], 'next-hop': Config.intf_ip['r4-eth2']},
            {'router':'r4', 'src': Config.intf_ip['r4-eth2'], 'dst':Config.host_ip['h1'], 'next-hop': Config.intf_ip['r3-eth1']},
            {'router':'r3', 'src': Config.intf_ip['r3-eth1'], 'dst':Config.host_ip['h1'], 'next-hop': Config.intf_ip['r3-eth0']},
            {'router':'r3', 'src': Config.intf_ip['r3-eth0'], 'dst':Config.host_ip['h1'], 'next-hop': Config.intf_ip['r1-eth2']},
            {'router':'r1', 'src': Config.intf_ip['r1-eth2'], 'dst':Config.host_ip['h1'], 'next-hop': Config.intf_ip['r1-eth0']},
        ]


class NetworkTopo(Topo):

    def build(self):

        # Add 4 routers in two different subnets
        r1 = self.addHost('r1', cls=LinuxRouter, ip=Config.intf_ip['r1-eth0']+"/24")
        r2 = self.addHost('r2', cls=LinuxRouter, ip=Config.intf_ip['r2-eth0']+"/24")
        r3 = self.addHost('r3', cls=LinuxRouter, ip=Config.intf_ip['r3-eth0']+"/24")
        r4 = self.addHost('r4', cls=LinuxRouter, ip=Config.intf_ip['r4-eth0']+"/24")

        # Add hosts
        h1 = self.addHost('h1', ip=Config.host_ip['h1']+"/24")
        h2 = self.addHost('h2', ip=Config.host_ip['h2']+"/24")

        # linking hosts to the routers
        self.addLink(h1, r1, intfName2="r1-eth0", params2={'ip':Config.intf_ip['r1-eth0']+"/24"})
        self.addLink(h2, r4, intfName2="r4-eth0", params2={'ip':Config.intf_ip['r4-eth0']+"/24"})

        # linking routers amongst themselves
        self.addLink(r1,r2, 
                    intfName1="r1-eth1", intfName2="r2-eth0", 
                    params1={'ip':Config.intf_ip['r1-eth1']+"/24"}, 
                    params2={'ip':Config.intf_ip['r2-eth0']+"/24"})

        self.addLink(r1,r3, 
                    intfName1="r1-eth2", intfName2="r3-eth0", 
                    params1={'ip':Config.intf_ip['r1-eth2']+"/24"}, 
                    params2={'ip':Config.intf_ip['r3-eth0']+"/24"})

        self.addLink(r2,r4, 
                    intfName1="r2-eth1", intfName2="r4-eth1", 
                    params1={'ip':Config.intf_ip['r2-eth1']+"/24"}, 
                    params2={'ip':Config.intf_ip['r4-eth2']+"/24"})

        self.addLink(r3,r4, 
                    intfName1="r3-eth1", intfName2="r4-eth2", 
                    params1={'ip':Config.intf_ip['r3-eth1']+"/24"}, 
                    params2={'ip':Config.intf_ip['r4-eth1']+"/24"})


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
        src_interface = config['src']
        router = config['router']
        dst_host = config['dst']
        next_hop_interface = config['next-hop']
        cmd = "ip route add "+dst_host+" via "+next_hop_interface+" dev "+src_interface
        info(net[router].cmd(cmd))
    

    net.start()
    info( '\n########### Routing Table of r1: ###########\n' )
    info( net['r1'].cmd('route') )

    info( '\n########### Routing Table of r2: ###########\n' )
    info( net['r2'].cmd('route') )

    info( '\n########### Routing Table of r3: ###########\n' )
    info( net['r3'].cmd('route') )

    info( '\n########### Routing Table of r4: ###########\n' )
    info( net['r4'].cmd('route') )

    info( '\n########### h1 pinging h2 ###########\n' )
    info( net['h1'].cmd('traceroute 10.0.1.2'))

    info( '\n########### h2 pinging h1 ###########\n' )
    info( net['h2'].cmd('traceroute 10.0.0.2'))

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()