from mininet.net import Mininet
from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import argparse

from attack import Attacker

class CustomTopology:

    def __init__(self, args):
        self.args = args
        setLogLevel('info')

    # ##########################    
    # basic topo for testing
    # Ryu Controller
    #      s1
    #    /    \
    #  s11    s12
    #  /\      /\
    # h1 h2   h3 h4
    # ##########################   
    def basic(self):
        net = Mininet(build=False, host=CPULimitedHost, link=TCLink, ipBase='10.0.0.0/8')

        info('*** Add Controller (ONOS) ***\n')
        c1 = net.addController(name='c1', controller=RemoteController, ip='127.0.0.1', protocol='tcp', port=6633) # default port 6633
        c2 = net.addController()

        info('*** Add Switches ***\n')
        s1 = net.addSwitch('s1', dpid='0000000000000001')
        s11 = net.addSwitch('s11', dpid='000000000000000b') # dpid 0x6=11
        s12 = net.addSwitch('s12', dpid='000000000000000c') # dpid 0xc=12

        info('*** Add Hosts ***\n')
        h1 = net.addHost('h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
        h2 = net.addHost('h2', ip='10.0.0.2', mac='00:00:00:00:00:02')
        h3 = net.addHost('h3', ip='10.0.0.3', mac='00:00:00:00:00:03')
        h4 = net.addHost('h4', ip='10.0.0.4', mac='00:00:00:00:00:04')

        info('*** Add Links ***\n')
        net.addLink(h1, s11, bw=10)
        net.addLink(h2, s11, bw=10)

        net.addLink(h3, s12, bw=10)
        net.addLink(h4, s12, bw=10)

        net.addLink(s11, s1, bw=10)
        net.addLink(s12, s1, bw=10)

        info('\n*** Build net ***\n')
        net.build()

        info('\n*** Start net ***\n')
        c1.start()
        for s in [s1, s11, s12]:
            s.start([c1])
        net.start()
        net.staticArp()

        # attacker = Attacker(h1, [h4, h3, h2])
        # if self.args.attack:
        #     attacker.simple_ddos_traffic()
        # else:
        #     attacker.simple_normal_traffic()

        CLI(net)

        net.stop()
    
    def large(self):
        net = Mininet(build=False, host=CPULimitedHost, link=TCLink, ipBase='10.0.0.0/24')

        info('*** Add Controller (ONOS) ***\n')
        c1 = net.addController(name='c1', controller=RemoteController, ip='127.0.0.1', protocol='tcp', port=6633) # default port 6633
        c2 = net.addController(name='c2', controller=RemoteController, ip='127.0.0.1', protocol='tcp', port=6634) # default port 6633

        info('*** Add Switches ***\n')
        s1 = net.addSwitch('s1', dpid='0000000000000001')
        s11 = net.addSwitch('s11', dpid='000000000000000b')
        s12 = net.addSwitch('s12', dpid='000000000000000c')
        s13 = net.addSwitch('s13', dpid='000000000000000d')
        s14 = net.addSwitch('s14', dpid='000000000000000e')
        s15 = net.addSwitch('s15', dpid='000000000000000f')
        # out domain switch
        s2 = net.addSwitch('s2', dpid='0000000000000002')

        info('*** Add Hosts ***\n')
        h111 = net.addHost('h111', ip='10.1.1.1', mac='00:00:00:01:01:01')
        h112 = net.addHost('h112', ip='10.1.1.2', mac='00:00:00:01:01:02')
        h113 = net.addHost('h113', ip='10.1.1.3', mac='00:00:00:01:01:03')
        h114 = net.addHost('h114', ip='10.1.1.4', mac='00:00:00:01:01:04')
        h115 = net.addHost('h115', ip='10.1.1.5', mac='00:00:00:01:01:05')

        h121 = net.addHost('h121', ip='10.1.2.1', mac='00:00:00:01:02:01')
        h122 = net.addHost('h122', ip='10.1.2.2', mac='00:00:00:01:02:02')
        h123 = net.addHost('h123', ip='10.1.2.3', mac='00:00:00:01:02:03')
        h124 = net.addHost('h124', ip='10.1.2.4', mac='00:00:00:01:02:04')
        h125 = net.addHost('h125', ip='10.1.2.5', mac='00:00:00:01:02:05')

        h131 = net.addHost('h131', ip='10.1.3.1', mac='00:00:00:01:03:01')
        h132 = net.addHost('h132', ip='10.1.3.2', mac='00:00:00:01:03:02')
        h133 = net.addHost('h133', ip='10.1.3.3', mac='00:00:00:01:03:03')
        h134 = net.addHost('h134', ip='10.1.3.4', mac='00:00:00:01:03:04')
        h135 = net.addHost('h135', ip='10.1.3.5', mac='00:00:00:01:03:05')

        h141 = net.addHost('h141', ip='10.1.4.1', mac='00:00:00:01:04:01')
        h142 = net.addHost('h142', ip='10.1.4.2', mac='00:00:00:01:04:02')
        h143 = net.addHost('h143', ip='10.1.4.3', mac='00:00:00:01:04:03')
        h144 = net.addHost('h144', ip='10.1.4.4', mac='00:00:00:01:04:04')
        h145 = net.addHost('h145', ip='10.1.4.5', mac='00:00:00:01:04:05')

        h151 = net.addHost('h151', ip='10.1.5.1', mac='00:00:00:01:05:01')
        h152 = net.addHost('h152', ip='10.1.5.2', mac='00:00:00:01:05:02')
        h153 = net.addHost('h153', ip='10.1.5.3', mac='00:00:00:01:05:03')
        h154 = net.addHost('h154', ip='10.1.5.4', mac='00:00:00:01:05:04')
        h155 = net.addHost('h155', ip='10.1.5.5', mac='00:00:00:01:05:05')

        # out domain host
        h200 = net.addHost('h200', ip='10.2.0.0', mac='00:00:00:02:00:00')

        info('*** Add Links ***\n')
        # depth 0
        net.addLink(s1, s2, bw=10)
        
        # depth 1
        net.addLink(s1, s11, bw=10)
        net.addLink(s1, s12, bw=10)
        net.addLink(s1, s13, bw=10)
        net.addLink(s1, s14, bw=10)
        net.addLink(s1, s15, bw=10)

        # depth 2
        net.addLink(s11, h111, bw=10)
        net.addLink(s11, h112, bw=10)
        net.addLink(s11, h113, bw=10)
        net.addLink(s11, h114, bw=10)
        net.addLink(s11, h115, bw=10)

        net.addLink(s12, h121, bw=10)
        net.addLink(s12, h122, bw=10)
        net.addLink(s12, h123, bw=10)
        net.addLink(s12, h124, bw=10)
        net.addLink(s12, h125, bw=10)

        net.addLink(s13, h131, bw=10)
        net.addLink(s13, h132, bw=10)
        net.addLink(s13, h133, bw=10)
        net.addLink(s13, h134, bw=10)
        net.addLink(s13, h135, bw=10)

        net.addLink(s14, h141, bw=10)
        net.addLink(s14, h142, bw=10)
        net.addLink(s14, h143, bw=10)
        net.addLink(s14, h144, bw=10)
        net.addLink(s14, h145, bw=10)

        net.addLink(s15, h151, bw=10)
        net.addLink(s15, h152, bw=10)
        net.addLink(s15, h153, bw=10)
        net.addLink(s15, h154, bw=10)
        net.addLink(s15, h155, bw=10)

        net.addLink(s2, h200, bw=10)

        info('\n*** Build net ***\n')
        net.build()

        info('\n*** Start net ***\n')
        c1.start()
        c2.start()
        for s in [s1, s11, s12, s13, s14, s15]:
            s.start([c1])
        for s in [s2]:
            s.start([c2])
        net.start()
        net.staticArp()

        CLI(net)

        net.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--attack', default=False, action='store_true')
    parser.add_argument('--large', default=False, action='store_true')
    args = parser.parse_args()

    customTopo = CustomTopology(args)
    if args.large:
        customTopo.large()
    else:
        customTopo.basic()