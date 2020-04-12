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

        attacker = Attacker(h1, [h2, h3])
        if self.args.attack:
            attacker.simple_ddos_traffic()
        else:
            attacker.simple_normal_traffic()

        CLI(net)

        net.stop()
    
    def large(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--attack', default=False, action='store_true')
    args = parser.parse_args()

    customTopo = CustomTopology(args)
    customTopo.basic()